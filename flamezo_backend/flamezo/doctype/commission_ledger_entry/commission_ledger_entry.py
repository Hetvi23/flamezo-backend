"""
Commission Ledger Entry — represents an outstanding commission liability for a
cash / pay-at-counter order. One entry per order. Settlement is recorded as
child rows in the `settlements` table; this header maintains running totals.

Invariant:  total_owed_paise == base_commission_paise + gst_paise
            outstanding_paise == max(0, total_owed_paise - settled_paise)
            status            ∈ outstanding | partial | settled | voided
"""

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime


class CommissionLedgerEntry(Document):
    def before_insert(self):
        if not self.accrued_at:
            self.accrued_at = now_datetime()
        self._recompute_totals()

    def before_save(self):
        self._recompute_totals()
        self._sync_status()

    def _recompute_totals(self):
        base = int(self.base_commission_paise or 0)
        gst = int(self.gst_paise or 0)
        total = base + gst
        self.total_owed_paise = total
        settled = sum(int(s.amount_paise or 0) for s in (self.settlements or []))
        self.settled_paise = settled
        self.outstanding_paise = max(0, total - settled)

    def _sync_status(self):
        if self.status == "voided":
            return
        if self.outstanding_paise <= 0 and (self.settled_paise or 0) >= (self.total_owed_paise or 0):
            self.status = "settled"
            if not self.settled_at:
                self.settled_at = now_datetime()
        elif (self.settled_paise or 0) > 0:
            self.status = "partial"
            self.settled_at = None
        else:
            self.status = "outstanding"
            self.settled_at = None
