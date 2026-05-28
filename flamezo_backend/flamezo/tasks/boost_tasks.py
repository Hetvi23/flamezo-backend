"""
Scheduled tasks for Flamezo Boost campaigns.

- sync_boost_performance: every 30 min — pull Meta insights for Live campaigns
- check_boost_campaigns_health: daily 9 AM — alert if guarantee at risk
- finalize_completed_boosts: midnight — complete expired campaigns, calculate guarantee
"""
import frappe
from frappe.utils import today, getdate, flt, now


def sync_boost_performance():
	"""Pull Meta campaign insights for all Live Boost campaigns (every 30 min)."""
	live_campaigns = frappe.get_all("Boost Campaign",
		filters={"status": "Live", "meta_campaign_id": ["is", "set"]},
		fields=["name", "meta_campaign_id", "coupons_redeemed"]
	)

	if not live_campaigns:
		return

	from flamezo_backend.flamezo.services.meta_ads import get_campaign_insights

	for campaign in live_campaigns:
		try:
			insights = get_campaign_insights(campaign.meta_campaign_id)
			updates = {
				"impressions": int(insights.get("impressions", 0)),
				"reach": int(insights.get("reach", 0)),
				"link_clicks": int(insights.get("clicks", 0)),
				"amount_spent_meta": flt(insights.get("spend", 0)),
			}
			redeemed = campaign.coupons_redeemed or 0
			if redeemed > 0:
				updates["cost_per_redemption"] = flt(updates["amount_spent_meta"]) / redeemed

			for field, value in updates.items():
				frappe.db.set_value("Boost Campaign", campaign.name, field, value,
									update_modified=False)
		except Exception as e:
			frappe.log_error(
				message=f"Campaign: {campaign.name}\nError: {str(e)}",
				title="Boost Performance Sync Error"
			)

	frappe.db.commit()


def check_boost_campaigns_health():
	"""Daily health check — alert admin if campaigns are underperforming (9 AM)."""
	live_campaigns = frappe.get_all("Boost Campaign",
		filters={"status": "Live", "is_first_campaign": 0},
		fields=["name", "campaign_name", "restaurant", "launch_date", "end_date",
				"guaranteed_redemptions", "coupons_redeemed", "campaign_duration"]
	)

	for campaign in live_campaigns:
		if not campaign.launch_date or not campaign.guaranteed_redemptions:
			continue

		days_total = int(campaign.campaign_duration or 14)
		launch_dt = getdate(str(campaign.launch_date))
		today_dt = getdate(today())
		days_elapsed = (today_dt - launch_dt).days if launch_dt and today_dt else 0
		days_elapsed = max(days_elapsed, 1)
		progress_pct = min(days_elapsed / days_total, 1.0)

		expected_by_now = int(campaign.guaranteed_redemptions * progress_pct)
		actual = campaign.coupons_redeemed or 0

		if actual < expected_by_now * 0.5:  # Less than 50% of expected
			frappe.log_error(
				message=(
					f"Campaign {campaign.name} ({campaign.campaign_name}) for {campaign.restaurant}\n"
					f"Guarantee: {campaign.guaranteed_redemptions} | Actual: {actual} | "
					f"Expected by now: {expected_by_now}\n"
					f"Days elapsed: {days_elapsed}/{days_total}"
				),
				title="Boost Campaign Guarantee At Risk"
			)


def finalize_completed_boosts():
	"""Midnight job — finalize expired campaigns and calculate guarantee compliance."""
	expired = frappe.get_all("Boost Campaign",
		filters={
			"status": "Live",
			"end_date": ["<=", today()]
		},
		fields=["name", "meta_campaign_id"]
	)

	for row in expired:
		try:
			# Pause on Meta
			if row.meta_campaign_id:
				from flamezo_backend.flamezo.services.meta_ads import pause_campaign
				try:
					pause_campaign(row.meta_campaign_id)
				except Exception:
					pass  # Campaign might already be paused

			# Deactivate linked coupon
			campaign = frappe.get_doc("Boost Campaign", row.name)
			if campaign.linked_coupon:
				frappe.db.set_value("Coupon", campaign.linked_coupon, "is_active", 0)

			# Mark completed (handles guarantee calculation)
			campaign.mark_completed()
			frappe.db.commit()

			frappe.logger().info(f"Boost campaign {row.name} finalized. "
								f"Redemptions: {campaign.coupons_redeemed}/{campaign.guaranteed_redemptions}")

		except Exception as e:
			frappe.log_error(
				message=f"Campaign: {row.name}\nError: {str(e)}",
				title="Boost Finalization Error"
			)

	frappe.db.commit()
