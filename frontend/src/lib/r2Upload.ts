/**
 * R2 Direct Upload Utility
 * Handles direct upload to Cloudflare R2 via Media Asset API
 *
 * Hardened for mobile:
 *  - Client-side image compression (HEIC → JPEG, large → small)
 *  - AbortController timeout on the R2 PUT (2 min)
 *  - Automatic retry with exponential backoff (3 attempts)
 */

import { compressImage, getSafeContentType } from './imageCompression'

interface UploadSessionResponse {
  upload_id: string
  object_key: string
  upload_url: string
  headers: Record<string, string>
  expires_in: number
}

interface ConfirmUploadResponse {
  name: string
  media_id: string
  status: string
  primary_url: string
  message?: string
}

interface R2UploadOptions {
  ownerDoctype: string
  ownerName: string
  mediaRole: string
  file: File
  altText?: string
  caption?: string
  displayOrder?: number
  /** Skip client-side compression (e.g. for videos) */
  skipCompression?: boolean
}

/** Timeout for the R2 PUT request (ms). 2 minutes for large files on slow mobile. */
const R2_PUT_TIMEOUT = 120_000

/** Max retry attempts for the R2 PUT step. */
const MAX_RETRIES = 2

/**
 * Upload file directly to R2 and create Media Asset
 */
export async function uploadToR2(options: R2UploadOptions): Promise<ConfirmUploadResponse> {
  const { ownerDoctype, ownerName, mediaRole, altText, caption, displayOrder, skipCompression } = options

  // Compress image before upload (HEIC→JPEG, large→small, normalizes content-type)
  const mediaType = getMediaType(options.file)
  let file = options.file
  if (mediaType === 'image' && !skipCompression) {
    file = await compressImage(options.file)
  }

  // Ensure content-type is correct (mobile browsers can report empty/wrong types)
  const contentType = getSafeContentType(file)

  const csrf = (window as any).frappe?.csrf_token || (window as any).csrf_token

  // Step 1: Request upload session
  const sessionRes = await fetch('/api/method/flamezo_backend.flamezo.media.api.request_upload_session', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Frappe-CSRF-Token': csrf,
    },
    body: JSON.stringify({
      owner_doctype: ownerDoctype,
      owner_name: ownerName,
      media_role: mediaRole,
      filename: file.name,
      content_type: contentType,
      size_bytes: file.size,
    }),
  })

  if (!sessionRes.ok) {
    const error = await sessionRes.json().catch(() => ({ message: 'Failed to request upload session' }))
    console.error('CDN Upload - Session request failed:', error)
    throw new Error(error.exc || error.message || 'Failed to request upload session')
  }

  const sessionJson = await sessionRes.json()
  const session: UploadSessionResponse = sessionJson.message

  if (!session?.upload_url) {
    console.error('CDN Upload - Invalid session response:', sessionJson)
    throw new Error('Invalid upload session response')
  }

  // Step 2: Direct upload to R2 (presigned PUT) — with timeout + retry
  await uploadToR2WithRetry(session, file, contentType)

  // Step 3: Confirm upload (creates Media Asset + enqueues processing)
  const confirmRes = await fetch('/api/method/flamezo_backend.flamezo.media.api.confirm_upload', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Frappe-CSRF-Token': csrf,
    },
    body: JSON.stringify({
      upload_id: session.upload_id,
      owner_doctype: ownerDoctype,
      owner_name: ownerName,
      media_role: mediaRole,
      alt_text: altText || '',
      caption: caption || '',
      display_order: displayOrder || 0,
    }),
  })

  if (!confirmRes.ok) {
    const error = await confirmRes.json().catch(() => ({ message: 'Confirm upload failed' }))
    console.error('CDN Upload - Confirm upload failed:', error)
    throw new Error(error.exc || error.message || 'Confirm upload failed')
  }

  const confirmJson = await confirmRes.json()
  const result = confirmJson.message

  if (!result || !result.primary_url) {
    console.error('CDN Upload - Invalid confirm response:', confirmJson)
    throw new Error('Invalid confirm upload response')
  }

  return result
}

/**
 * PUT file to R2 presigned URL with timeout and retry.
 * Retries up to MAX_RETRIES times on network failure (the presigned URL stays valid for 10 min).
 */
async function uploadToR2WithRetry(
  session: UploadSessionResponse,
  file: File,
  contentType: string,
): Promise<void> {
  let lastError: Error | null = null

  for (let attempt = 0; attempt <= MAX_RETRIES; attempt++) {
    try {
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), R2_PUT_TIMEOUT)

      const putRes = await fetch(session.upload_url, {
        method: 'PUT',
        headers: {
          'Content-Type': contentType,
        },
        body: file,
        signal: controller.signal,
      })

      clearTimeout(timeoutId)

      if (!putRes.ok) {
        throw new Error(`R2 upload failed: ${putRes.status} ${putRes.statusText}`)
      }

      return // success
    } catch (err: any) {
      lastError = err
      const isNetworkError = err.name === 'TypeError' || err.name === 'AbortError'

      if (!isNetworkError || attempt === MAX_RETRIES) {
        break
      }

      // Exponential backoff: 1s, 2s
      const delay = 1000 * (attempt + 1)
      console.warn(`CDN Upload - R2 PUT attempt ${attempt + 1} failed, retrying in ${delay}ms...`, err.message)
      await sleep(delay)
    }
  }

  console.error('CDN Upload - R2 upload failed after retries:', lastError)
  throw new Error(
    lastError?.name === 'AbortError'
      ? 'Upload timed out. Please check your internet connection and try again.'
      : 'Upload failed. Please check your internet connection and try again.',
  )
}

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

/**
 * Determine media type from file
 */
export function getMediaType(file: File): 'image' | 'video' {
  const videoExtensions = ['mp4', 'webm', 'ogg', 'mov', 'avi', 'mkv', 'flv', 'wmv']
  const extension = file.name.split('.').pop()?.toLowerCase() || ''

  if (file.type.startsWith('video/') || videoExtensions.includes(extension)) {
    return 'video'
  }
  return 'image'
}
