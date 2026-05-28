import frappe
from frappe.model.document import Document
from frappe.utils import flt, today, add_days, now


PACKAGE_CONFIG = {
	"Growth": {"budget": 2000, "ad_spend_pct": 0.70, "fee_pct": 0.30},
	"Boost":  {"budget": 5000, "ad_spend_pct": 0.70, "fee_pct": 0.30},
	"Scale":  {"budget": 10000, "ad_spend_pct": 0.70, "fee_pct": 0.30},
}

GRADE_MULTIPLIERS = {"A": 1.0, "B": 0.8, "C": 0.6, "D": 0.0}
REDEMPTIONS_PER_1K_SPEND = 12
MIN_DAILY_BUDGET_PAISA = 10000  # ₹100 minimum for Meta optimization


class BoostCampaign(Document):
	def validate(self):
		self._compute_budget_split()
		self._compute_coupon_fields()
		self._validate_coordinates()
		self._validate_daily_budget()
		self._set_first_campaign_flag()
		self._compute_guarantee()

	def _compute_budget_split(self):
		config = PACKAGE_CONFIG.get(self.package_tier)
		if not config:
			return
		self.budget_total = flt(config["budget"])
		self.ad_spend_allocated = flt(self.budget_total * config["ad_spend_pct"])
		self.flamezo_fee = flt(self.budget_total * config["fee_pct"])
		self.gst_on_fee = flt(self.flamezo_fee * 0.18)

	def _compute_coupon_fields(self):
		if not self.coupon_code and self.restaurant:
			self.coupon_code = self._generate_unique_coupon_code()
		self.coupon_discount = flt(self.offer_amount)
		self.coupon_min_order = flt(self.offer_amount) * 2 if flt(self.offer_amount) > 0 else 0
		duration = int(self.campaign_duration or 14)
		self.coupon_valid_days = duration + 7

	def _generate_unique_coupon_code(self):
		"""Generate a unique coupon code, retrying on collision."""
		import random
		import string
		restaurant_short = (self.restaurant or "XX")[:8].upper().replace("-", "")
		for _ in range(50):
			suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
			candidate = f"BOOST-{restaurant_short}-{suffix}"
			if not frappe.db.exists("Boost Campaign", {"coupon_code": candidate}):
				return candidate
		frappe.throw("Failed to generate unique coupon code. Please try again.")

	def _validate_coordinates(self):
		"""Ensure restaurant has GPS coordinates set — required for geo-targeting."""
		if self.status == "Draft":
			return  # Don't block draft creation
		if not self.restaurant_lat or not self.restaurant_lng:
			frappe.throw(
				"Restaurant GPS coordinates are required for Boost campaigns. "
				"Please set latitude and longitude in Restaurant settings."
			)

	def _validate_daily_budget(self):
		"""Ensure daily budget meets Meta's minimum for effective optimization."""
		duration = int(self.campaign_duration or 14)
		daily_paisa = int(flt(self.ad_spend_allocated) / duration * 100)
		if daily_paisa < MIN_DAILY_BUDGET_PAISA and self.ad_spend_allocated > 0:
			min_inr = MIN_DAILY_BUDGET_PAISA / 100
			frappe.throw(
				f"Daily ad budget (₹{daily_paisa / 100:.0f}) is below Meta's minimum "
				f"of ₹{min_inr:.0f}/day. Increase the package or reduce duration."
			)

	def _set_first_campaign_flag(self):
		if self.is_new():
			existing = frappe.db.count("Boost Campaign", filters={
				"restaurant": self.restaurant,
				"status": ["not in", ["Draft", "Cancelled", "Failed"]],
			})
			self.is_first_campaign = 1 if existing == 0 else 0

	def _compute_guarantee(self):
		if self.is_first_campaign:
			self.guaranteed_redemptions = 0
			return
		grade = self.location_grade or "A"
		multiplier = GRADE_MULTIPLIERS.get(grade, 1.0)
		ad_spend_k = flt(self.ad_spend_allocated) / 1000
		self.guaranteed_redemptions = int(ad_spend_k * REDEMPTIONS_PER_1K_SPEND * multiplier)

	def get_daily_budget_paisa(self):
		"""Daily budget in paisa for Meta API (Meta uses smallest currency unit)."""
		duration = int(self.campaign_duration or 14)
		daily = flt(self.ad_spend_allocated) / duration
		return int(daily * 100)

	def mark_live(self):
		self.status = "Live"
		self.launch_date = today()
		self.end_date = add_days(today(), int(self.campaign_duration or 14))
		# Activate the linked coupon now that campaign is actually live
		if self.linked_coupon:
			frappe.db.set_value("Coupon", self.linked_coupon, "is_active", 1)
		self.save(ignore_permissions=True)

	def mark_completed(self):
		self.status = "Completed"
		self.completed_at = now()
		self.actual_redemptions = self.coupons_redeemed
		if self.guaranteed_redemptions > 0 and self.actual_redemptions >= self.guaranteed_redemptions:
			self.guarantee_met = 1
		elif self.guaranteed_redemptions > 0:
			deficit = self.guaranteed_redemptions - self.actual_redemptions
			cpr = flt(self.cost_per_redemption) or (flt(self.amount_spent_meta) / max(self.actual_redemptions, 1))
			self.topup_credit_amount = flt(deficit * cpr * 1.2)
		self.save(ignore_permissions=True)

	def mark_paused(self):
		self.status = "Paused"
		self.paused_at = now()
		self.save(ignore_permissions=True)

	def mark_resumed(self):
		self.status = "Live"
		self.paused_at = ""
		self.save(ignore_permissions=True)
