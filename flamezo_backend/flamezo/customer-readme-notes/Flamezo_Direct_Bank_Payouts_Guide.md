# 🏦 Direct Bank Payouts — Complete Setup Guide

> **Last Updated:** 2026-05-23 — Reflects the current Flamezo platform model post-Razorpay Route migration.

A 3-minute setup that lets customer payments land in **your bank account directly** — instead of waiting for our weekly transfer.

This guide will walk you through the entire process from start to finish. No technical knowledge needed.

---

## 🌟 What You're Setting Up

Right now, here's what happens when a customer pays online at your restaurant:

> **Today**  →  Customer pays → Money goes to Flamezo → We transfer to your bank weekly via NEFT

After this setup, here's what will happen:

> **After Setup**  →  Customer pays → Money splits instantly → Your bank receives 97% in 2 business days · Flamezo keeps the 3% Success Share

**Why this is better:**

✔ Money in your bank **48 hours after the order** instead of 7+ days  
✔ Fully automatic — no waiting for our weekly transfer  
✔ Razorpay sends a settlement statement straight to your registered email  
✔ Cleaner accounting — no need to reconcile Flamezo's bulk transfers against orders  

---

## 📋 Before You Start (2 minutes)

Have these 4 things ready before you sit down to fill the form. It's much faster than searching mid-way.

### 1. PAN Card 🪪
Your business PAN (if you have a company / partnership) OR your personal PAN (if you run the restaurant as a proprietorship).

> Format: **10 characters** — 5 letters, 4 numbers, 1 letter. Example: `ABCDE1234F`

### 2. Bank Passbook or Cancelled Cheque 📒
You need 3 things from it:
- **Account number** (just the digits)
- **IFSC code** (11 characters, like `HDFC0001234`)
- **Account holder name** (exactly as printed)

### 3. Knowledge of Your Business Type 🏢
Pick the one that matches your registration paperwork:

| If your restaurant is… | Pick this |
|---|---|
| Just you, no formal company | **Proprietorship** |
| 2 or more partners, no incorporation | **Partnership** |
| Limited Liability Partnership (LLP) | **LLP** |
| Pvt. Ltd. company | **Private Limited** |
| Listed / public company | **Public Limited** |
| No registered business at all | **Individual** |

> 👉 **Most small restaurants are "Proprietorship"** — even if you have a partner. Pick this if unsure.

### 4. Email Access 📬
Check that you can access the email you signed up to Flamezo with. **Razorpay sends important verification emails here.** If they need clarification, they'll email you (not us).

---

## 🚨 The ONE Thing That Trips People Up

The single biggest reason KYC gets rejected is:

> The name on the **PAN card** doesn't match the name on the **bank account**.

**Before submitting, double-check this.** If your PAN says "Rajesh Kumar Sharma" but your bank account is in the name of "Sharma Restaurant Foods", Razorpay will reject it.

### How to fix a mismatch BEFORE submitting:

- **Option A** — Use the bank account whose holder name matches the PAN holder name exactly  
- **Option B** — If using a business-name bank account, the PAN must also be a business PAN with the same registered name (not a personal PAN)  
- **Option C** — Open a new current account in the PAN holder's name (or matching the business legal name on PAN)

---

## 🚀 STEP 1: Open the Setup Page

1. Log into your Flamezo dashboard
2. Click **"Direct Bank Payouts"** in the left sidebar  
   *(Look for the 🏦 bank icon — usually right under "Customer pay & Usage")*
3. You should see a hero box that says **"Get paid directly to your bank"**

> ✨ **Tip**: If you see a yellow banner at the top of the dashboard saying *"Want your customer payments to land in your bank directly?"* — that's the same link. Click "Set Up".

---

## 🏢 STEP 2: Fill in Business Details

### Field 1 — Legal Business Name

This must match your **PAN card** exactly.

✔ If your PAN says **"Sharma Restaurant"** → type `Sharma Restaurant`  
✔ If your PAN says **"Rajesh Kumar Sharma"** (proprietor's personal PAN) → type `Rajesh Kumar Sharma`  

❌ Don't add abbreviations or change capitalisation — Razorpay does an exact string match.

### Field 2 — Business Type

Pick from the dropdown. Each option has a hint underneath explaining what it means.

> Most restaurants pick **Proprietorship**.

### Field 3 — PAN Number

Type your 10-character PAN.

> 💡 The form **automatically capitalises** what you type — so even if you type `abcde1234f`, it'll show as `ABCDE1234F`. That's correct.

If the form says *"PAN must be 10 characters like ABCDE1234F"*, double-check you've copied all 10 characters correctly.

---

## 🏦 STEP 3: Fill in Bank Account Details

### Field 1 — Account Number

Just the digits — no spaces, no dashes. The form will automatically strip anything that's not a number.

> Example: `50100123456789` (typically 9–16 digits depending on the bank)

### Field 2 — IFSC Code

11 characters. Find it on:

- Your bank passbook (front page)
- A cancelled cheque (printed near the bottom)
- Your bank's mobile app under "Account Details"

> Example: `HDFC0001234`  
> The form **auto-capitalises** — type lowercase, it'll fix it.

If the form rejects it with *"IFSC must be 11 characters like HDFC0001234"*, you probably missed a character or typed the wrong code.

### Field 3 — Account Holder Name

**This is the field that decides whether KYC passes or fails. Re-read [The ONE Thing That Trips People Up](#-the-one-thing-that-trips-people-up) above before filling this in.**

Type the name **exactly as it's printed on your bank passbook**. If your passbook says "RAJESH KUMAR SHARMA" in all caps, use that. If it says "Rajesh Kumar Sharma", use that.

---

## ✅ STEP 4: Click Submit

Once all 6 fields are filled and the form looks clean:

1. Click **"Submit for Verification"**
2. You'll see a green pop-up: *"Submitted! Razorpay is reviewing your details."*
3. The big card at the top of the page changes from orange (Not Started) to **blue (Under Review)**

That's it. You can close the page. Razorpay takes it from here.

---

## ⏳ STEP 5: Wait for Razorpay (1–3 Business Days)

During this time:

✔ Your restaurant **keeps working normally** — orders, payments, deliveries all unaffected  
✔ Customer payments **still flow** — they just settle to you weekly via Flamezo as before  
✔ You don't need to check the dashboard repeatedly — the system will update itself when Razorpay decides  

**You don't need to do anything during this wait.**

### What Razorpay actually checks during these days:

- ✔ Does the PAN number exist in their database?
- ✔ Does the PAN holder name match the bank account holder name?
- ✔ Is the IFSC valid and the account active?
- ✔ Does the business type match what's registered against the PAN?

If everything's clean, most submissions are **approved within a few hours** — sometimes instantly.

---

## 🎉 STEP 6: You're Activated!

Once Razorpay approves, here's what happens automatically:

1. Your dashboard hero card turns **emerald green** with *"Direct payouts are active"*
2. The yellow nudge banner disappears from the top of the dashboard
3. **The very next online order** automatically splits — your bank gets the merchant share, Flamezo keeps the Success Share
4. Razorpay sends a settlement email to your registered email confirming activation

### When does the first payout actually arrive?

| You ran an order on | Bank credit reaches you by |
|---|---|
| Monday | Wednesday |
| Tuesday | Thursday |
| Wednesday | Friday |
| Thursday | Monday (next week) |
| Friday | Tuesday (next week) |
| Saturday | Tuesday (next week) |
| Sunday | Wednesday (next week) |

> This is **Razorpay's standard T+2 business-day** settlement schedule. Holidays and bank closures may push it by a day.

### Where can I see the payouts?

Two places:

1. **Razorpay's own merchant dashboard** ([dashboard.razorpay.com](https://dashboard.razorpay.com)) — log in with the email/phone you used in the KYC form. You'll see every settlement, with the exact orders that contributed to it.
2. **Your bank statement / app** — UPI / NEFT credit from "RAZORPAY SOFTWARE" with a reference ID

---

## 🛠️ Common Issues & How to Fix Them

### Problem 1 — "Razorpay needs more information"

You'll see an amber hero on the KYC page: *"Razorpay needs more information"*. They've also sent you an email with the specific request.

**Fix:**
1. Open the email from Razorpay (subject usually starts with *"Action needed:"*)
2. Read which specific field they're flagging
3. Come back to Direct Bank Payouts page
4. The form is **pre-filled with your previous submission**
5. Edit just the flagged field
6. Click **"Re-submit Details"**

---

### Problem 2 — "Submission was rejected"

Red hero on the KYC page: *"Submission was rejected"*. The most common reasons:

| Reason | What to do |
|---|---|
| PAN holder name ≠ bank holder name | Either change the bank account, or update the legal name field to match the PAN exactly |
| Wrong IFSC (typed for the wrong branch) | Look up the correct IFSC on your bank's mobile app and re-submit |
| Business type doesn't match PAN registration | Switch business type in the dropdown (e.g. you picked Pvt Ltd but PAN is for a proprietorship) |
| PAN entered with a typo | Double-check character by character against the physical card |

After fixing, click **"Re-submit Details"**.

---

### Problem 3 — Stuck in "Under Review" for more than 5 days

Razorpay usually takes 1–3 business days. If it's been 5+ days:

1. Check your spam folder for any email from Razorpay you might have missed
2. Contact Flamezo support — share your restaurant ID and we can ping Razorpay to push things along

---

### Problem 4 — "Account Suspended" status

Rose-red hero on the KYC page. This means Razorpay has put a temporary hold on your account — usually due to a customer dispute, compliance flag, or regulatory check.

**What still works:** Your restaurant continues taking orders. Customer payments still settle to you — via Flamezo's weekly NEFT (we automatically fall back to that mode).

**What to do:** Contact Flamezo support. We'll coordinate with Razorpay to clear the suspension.

---

## ❓ Frequently Asked Questions

### Do I HAVE to set this up?

No. Without setup:
- Customer payments still work
- They land in Flamezo's account first
- We transfer to your bank **weekly via NEFT**

With setup:
- Customer payments split **instantly**
- Bank credit in **T+2 days** instead of 7+

It's purely a "do you want faster payouts" choice. Most restaurants choose to set it up because faster cash flow = easier operations.

---

### Will my Success Share go up or down after setting this up?

**Neither.** Your Success Share rate is unchanged — same 3% (or 1.5% if you're a legacy restaurant) you'd pay either way.

The only difference is **when and how** Flamezo collects it:
- **Before setup**: We deduct it from the money we hold, then settle the rest to you weekly
- **After setup**: Razorpay splits it automatically at the moment of payment — we get our share, you get yours, simultaneously

---

### What about cash orders?

Cash orders work **identically** whether or not you've done KYC.

- Customer pays cash at the counter → 100% of the cash stays with you
- A small Success Share ledger entry is created for our share
- We recover it automatically — first from your Flamezo wallet, then from the next online order's split (we just take a bit extra), then from your autopay mandate if set up

You'll never get a manual invoice for cash Success Share. It all happens behind the scenes.

---

### What if my bank account changes later?

Just come back to the Direct Bank Payouts page and update the bank fields, then click **"Update Details"**. Razorpay will do a fresh verification (usually faster the second time since they already know your PAN).

Important: Your existing settlements aren't lost — they'll just route to the new account from that point forward.

---

### Is my data safe?

Yes. Three layers of safety:

1. Your PAN + bank details are transmitted **directly from your browser to Razorpay's encrypted KYC system**. Flamezo never sees your bank passwords, OTPs, or any login credentials.
2. The data Razorpay reads from us is sent over a TLS-encrypted connection authenticated with our API keys.
3. PAN and account numbers are stored encrypted at rest in our database (only visible to Razorpay-cleared system processes — not to support staff).

---

### Can I revoke or undo this?

Yes. Two options:

- **Pause direct payouts temporarily** — Contact support. We can set your `route_mode` to `flamezo_hold` so payments come back to us (we settle weekly as before). Your KYC stays valid for when you want to re-enable.
- **Permanently disconnect** — Contact Razorpay support directly to delete the Linked Account. After that, you'd need to re-do KYC if you ever want direct payouts again.

---

### Do I also need to set up Autopay?

**No, that's a separate thing.** Direct Bank Payouts (this guide) and Autopay are two independent setups:

| | Direct Bank Payouts | Autopay |
|---|---|---|
| **Page** | `/route-kyc` | `/autopay-setup` |
| **What it does** | Money flows to your bank directly | Authorizes Flamezo to auto-charge for monthly floor + cash Success Share |
| **You'd want it if…** | You want faster payouts (T+2 vs 7 days) | You don't want to manually top up wallet for floor recovery |

You can have neither, either, or both. They don't depend on each other.

---

## 📞 Need Help?

If anything in this guide doesn't match what you're seeing on the dashboard, or you get stuck mid-process:

- 📧 Email: **support@flamezo.in**
- 💬 WhatsApp: **+91-XXXXX-XXXXX** *(replace with your actual support number)*
- 🌐 Help Center: **flamezo.in/help**

When you contact support, please share:
1. Your **restaurant ID** (visible in your dashboard URL / settings)
2. A **screenshot of the dashboard hero card** showing the current status
3. The **exact error message** if any

---

## 📚 Glossary — Plain English

Just in case any term is unfamiliar:

| Term | What it actually means |
|---|---|
| **Route KYC** | Razorpay's process of verifying your identity + bank so they can send money directly to you |
| **Linked Account** | The Razorpay account they create on your behalf, linked to your bank |
| **Success Share** | The small percentage Flamezo retains on each order (3% new, 1.5% legacy). Same as "commission" — we call it Success Share because we only earn when you earn |
| **Settlement** | The act of money moving from Razorpay to your bank |
| **T+2** | Trade day + 2 business days. If you take an order on Monday, money arrives by Wednesday |
| **Mandate / Autopay** | Permission you give us to auto-charge a fixed monthly amount via UPI/Card. Separate from this KYC flow |
| **PAN** | Permanent Account Number — your tax ID (10 characters) |
| **IFSC** | Indian Financial System Code — identifies your bank branch (11 characters) |
| **NEFT** | National Electronic Funds Transfer — the way Flamezo currently moves money to you weekly (slower than Razorpay's direct route) |

---

> 🎯 **You're all set!** Most restaurants complete this entire process in under 5 minutes of active time + a 1–3 day automatic wait. Welcome to faster cash flow.
