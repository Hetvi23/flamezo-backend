# Copyright (c) 2026, DineMatters and contributors
# For license information, please see license.txt
#
# ── DineMatters Platform-Wide Loyalty Constants ───────────────────────────────
#
# These values are FIXED by DineMatters and are NOT configurable by restaurants.
# The settlement model is: restaurants pay nothing in cash — instead, the cross-
# network customer discovery IS the settlement. A customer who earned cash at
# Restaurant A and redeems at Restaurant B is a net-new customer for Restaurant B.
# That's the DineMatters value proposition.
#
# To change these values, update them here only. The backend (loyalty.py) and
# the API (api/loyalty.py) both import from this single source of truth.
# ─────────────────────────────────────────────────────────────────────────────

PLATFORM_LOYALTY = {
    # ── Earning ───────────────────────────────────────────────────────────────
    # All restaurants on the DineMatters network earn at the same rate.
    # Earn mode is always "Percentage of Bill" — flat modes are not supported
    # in the centralized model to keep the experience predictable.
    "earn_type":            "Percentage of Bill",
    "earn_percentage":      10.0,     # 10% of bill amount → e.g., ₹1000 order earns ₹100 cash
    "min_order_to_earn":    100,      # Orders below ₹100 earn nothing (prevents micro-order farming)
    "max_coins_per_order":  1000,     # Hard cap per transaction (prevents whale abuse)

    # ── Redemption ────────────────────────────────────────────────────────────
    "min_redemption_threshold":   250,   # Customer must have at least ₹250 in wallet to redeem
    "min_billing_for_redemption": 200,   # Order must be ≥ ₹200 to allow redemption

    # ── Coin Value (non-negotiable) ───────────────────────────────────────────
    "coin_value_in_inr":  1,         # 1 DineMatters Cash = ₹1. Always.

    # ── Expiry ───────────────────────────────────────────────────────────────
    "loyalty_expiry_months": 6,      # Cash expires 6 months after earning

    # ── Referral & Growth ─────────────────────────────────────────────────────
    # When a customer shares their link and a new user verifies their phone:
    "welcome_reward_coins":         50,   # New user welcome bonus (referee gets ₹50)
    "referral_share_coins":         30,   # Referrer earns ₹30 per verified new open
    "max_opens_rewarded_per_share": 10,   # Max rewards per share cycle (resets on next order)

    # ── Platform Tiers (Global, based on lifetime earned cash) ────────────────
    "tier": {
        "silver":   500,    # ₹500+ lifetime earnings → Silver
        "gold":     2000,   # ₹2,000+ lifetime earnings → Gold
        "platinum": 5000,   # ₹5,000+ lifetime earnings → Platinum
    },
}


# Convenience helpers so callers don't have to dig into the dict

def get_earn_percentage() -> float:
    return float(PLATFORM_LOYALTY["earn_percentage"])

def get_max_coins_per_order() -> int:
    return int(PLATFORM_LOYALTY["max_coins_per_order"])

def get_min_order_to_earn() -> int:
    return int(PLATFORM_LOYALTY["min_order_to_earn"])

def get_min_redemption_threshold() -> int:
    return int(PLATFORM_LOYALTY["min_redemption_threshold"])

def get_min_billing_for_redemption() -> int:
    return int(PLATFORM_LOYALTY["min_billing_for_redemption"])

def get_expiry_months() -> int:
    return int(PLATFORM_LOYALTY["loyalty_expiry_months"])

def get_welcome_reward_coins() -> int:
    return int(PLATFORM_LOYALTY["welcome_reward_coins"])

def get_referral_share_coins() -> int:
    return int(PLATFORM_LOYALTY["referral_share_coins"])

def get_max_opens_rewarded_per_share() -> int:
    return int(PLATFORM_LOYALTY["max_opens_rewarded_per_share"])
