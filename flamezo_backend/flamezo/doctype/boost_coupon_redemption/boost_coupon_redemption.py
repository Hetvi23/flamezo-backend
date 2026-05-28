import frappe
from frappe.model.document import Document
from frappe.utils import now


class BoostCouponRedemption(Document):
	def before_insert(self):
		if not self.redeemed_at:
			self.redeemed_at = now()
		self._increment_campaign_counter()

	def _increment_campaign_counter(self):
		"""Atomically increment coupons_redeemed on the parent Boost Campaign."""
		if self.boost_campaign:
			frappe.db.sql("""
				UPDATE `tabBoost Campaign`
				SET coupons_redeemed = coupons_redeemed + 1,
				    actual_redemptions = actual_redemptions + 1
				WHERE name = %s
			""", (self.boost_campaign,))
