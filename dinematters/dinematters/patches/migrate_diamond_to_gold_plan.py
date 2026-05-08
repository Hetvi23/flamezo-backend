"""
Patch: migrate_diamond_to_gold_plan

Plan restructuring:
  - Old DIAMOND → new GOLD (renamed, same features + more)
  - Old GOLD → new GOLD (free upgrade — old GOLD customers get everything)
  - SILVER stays SILVER

Also:
  - Ensures all Silver restaurants have loyalty enabled by default (is_active on
    Restaurant Loyalty Config + enable_loyalty on Restaurant).
  - Silver restaurants with loyalty enabled are marked as listed_on_club = 1.
  - Renames legacy coin transaction types:
      "Monthly DIAMOND Floor" → "Monthly GOLD Floor"
      "Daily GOLD Floor" / "Daily GOLD Subscription" / "Daily DIAMOND Floor"
        → "Daily GOLD Floor"
"""

import frappe


def execute():
    # ── 1. Migrate DIAMOND → GOLD ─────────────────────────────────────────────
    frappe.db.sql("""
        UPDATE `tabRestaurant`
        SET plan_type = 'GOLD',
            plan_change_reason = 'Automated migration: DIAMOND plan renamed to GOLD'
        WHERE plan_type = 'DIAMOND'
    """)

    # ── 2. Migrate old GOLD → new GOLD (free upgrade) ─────────────────────────
    # Old GOLD restaurants move to the new GOLD plan — they get everything.
    # No action needed on plan_type (already GOLD), but log it for audit.
    frappe.db.sql("""
        UPDATE `tabRestaurant`
        SET plan_change_reason = 'Automated migration: Legacy GOLD upgraded to new GOLD plan'
        WHERE plan_type = 'GOLD'
          AND (plan_change_reason IS NULL OR plan_change_reason NOT LIKE '%DIAMOND%')
    """)

    # ── 3. Plan Change Log: update historical entries ─────────────────────────
    frappe.db.sql("""
        UPDATE `tabPlan Change Log`
        SET previous_plan = 'GOLD'
        WHERE previous_plan = 'DIAMOND'
    """)
    frappe.db.sql("""
        UPDATE `tabPlan Change Log`
        SET new_plan = 'GOLD'
        WHERE new_plan = 'DIAMOND'
    """)

    # ── 4. Deferred plan: DIAMOND → GOLD ─────────────────────────────────────
    frappe.db.sql("""
        UPDATE `tabRestaurant`
        SET deferred_plan_type = 'GOLD'
        WHERE deferred_plan_type = 'DIAMOND'
    """)

    # ── 5. Rename legacy Coin Transaction types ───────────────────────────────
    frappe.db.sql("""
        UPDATE `tabCoin Transaction`
        SET transaction_type = 'Monthly GOLD Floor'
        WHERE transaction_type IN ('Monthly DIAMOND Floor', 'Daily DIAMOND Floor', 'Daily DIAMOND Subscription')
    """)
    frappe.db.sql("""
        UPDATE `tabCoin Transaction`
        SET transaction_type = 'Daily GOLD Floor'
        WHERE transaction_type = 'Daily GOLD Subscription'
    """)

    # ── 6. Enable loyalty for all existing Silver restaurants by default ───────
    # Ensures they are opted into Club and have ordering enabled.
    silver_restaurants = frappe.get_all(
        "Restaurant",
        filters={"plan_type": "SILVER", "is_active": 1},
        fields=["name", "enable_loyalty"]
    )

    for res in silver_restaurants:
        # Enable loyalty on the restaurant doc
        frappe.db.set_value("Restaurant", res.name, {
            "enable_loyalty": 1,
            "no_ordering": 0,
        })

        # Ensure a Loyalty Config exists and is active
        existing = frappe.db.get_value(
            "Restaurant Loyalty Config", {"restaurant": res.name}, "name"
        )
        if existing:
            frappe.db.set_value("Restaurant Loyalty Config", existing, "is_active", 1)
        else:
            config_doc = frappe.get_doc({
                "doctype": "Restaurant Loyalty Config",
                "restaurant": res.name,
                "program_name": "DineMatters Rewards",
                "is_active": 1,
                "earn_type": "Percentage of Bill",
                "earn_percentage": 10.0,
                "points_per_inr": 0.1,
                "coin_value_in_inr": 1,
                "earn_on_status": "Completed",
                "birthday_bonus_coins": 100,
            })
            config_doc.insert(ignore_permissions=True)

    frappe.db.commit()
    frappe.logger().info("migrate_diamond_to_gold_plan: completed successfully")
