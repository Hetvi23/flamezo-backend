/**
 * Centralized Feature Access Control
 *
 * Under the May 2026 single-tier business model every onboarded restaurant is
 * on GOLD (the only active tier) and therefore has access to every feature on
 * day one. The helper and constants below are retained for backwards
 * compatibility with the many components that import them, but they now
 * always report "unlocked".
 *
 * If a paid tier is ever reintroduced, restore the original SILVER/GOLD lists
 * and reinstate the gating logic.
 */

export type PlanType = 'SILVER' | 'GOLD';

// Kept for backwards-compatible imports; the lists are no longer consulted
// for gating because `getFeatureAccessStatus` always reports unlocked.
export const GOLD_ONLY_FEATURES: string[] = [];
export const SILVER_FEATURES: string[] = [];

/**
 * Returns the feature-access status for a given plan + feature.
 *
 * Under the single-tier model every feature is unlocked for every plan, so
 * this always returns `{ isLocked: false, requiredTier: null }`. The
 * signature is preserved for the dozens of call sites that already use it.
 */
export function getFeatureAccessStatus(_plan: PlanType, _feature?: string) {
  return { isLocked: false, requiredTier: null as PlanType | null };
}
