import frappe
from frappe.model.document import Document
from frappe.utils import flt
import math


class Order(Document):
    def before_save(self):
        # Use the centralized pricing engine for production-level consistency
        from flamezo_backend.flamezo.utils.pricing import calculate_cart_totals
        
        # 2. Preparation: Determine if we should recalculate
        # For WhatsApp orders, we trust the frontend's calculated totals if provided,
        # otherwise we fallback to the central pricing engine.
        if getattr(self, "is_whatsapp_order", 0) and flt(self.total) > 0:
            # Update Platform Fee only
            rate = float(frappe.db.get_value("Restaurant", self.restaurant, "platform_fee_percent") or 3.0) / 100.0  # 3.0 default for new (legacy grandfathered at 1.5)
            self.platform_fee_amount = int(math.floor(float(self.total or 0) * rate * 100))
            return

        # Prepare items in the format expected by the utility
        pricing_items = []
        for item in self.get("order_items"):
            if not item.product_name and item.product:
                item.product_name = frappe.db.get_value("Menu Product", item.product, "product_name")
            
            pricing_items.append({
                "quantity": item.quantity or 1,
                "unitPrice": item.unit_price,
                "dishId": item.product
            })

        # Calculate totals
        result = calculate_cart_totals(
            restaurant=self.restaurant,
            items=pricing_items,
            coupon_code=self.coupon,
            loyalty_coins=flt(self.loyalty_coins_redeemed or 0),
            customer=self.platform_customer,
            delivery_type=self.order_type # Dine-in, Delivery, Takeaway
        )

        # Update self with calculated values
        self.subtotal = result["subtotal"]
        self.discount = result["discount"]
        self.loyalty_discount = result["loyaltyDiscount"]
        self.tax = result["tax"]
        self.cgst = result["cgst"]
        self.sgst = result["sgst"]
        self.tax_percent = result["taxRate"]
        self.delivery_fee = result["deliveryFee"]
        self.packaging_fee = result["packagingFee"]
        
        # Delivery breakdown for reporting
        details = result.get("deliveryDetails", {})
        self.delivery_courier_fee = flt(details.get("courier_fee", 0))
        self.delivery_markup = flt(details.get("markup", 0))
        self.logistics_platform_fee = flt(details.get("platform_fee", 0))
        
        self.total = result["total"]

        # 5. Update Platform Fee (Dynamic commission on GMV)
        # GMV = total amount paid by customer
        # Field is 'platform_fee_amount' (Int, Paise)
        rate = float(frappe.db.get_value("Restaurant", self.restaurant, "platform_fee_percent") or 1.5) / 100.0
        self.platform_fee_amount = int(math.floor(float(self.total or 0) * rate * 100))


    def on_update(self):
        """
        Post-save side effects.

        Commission (a.k.a. Success Share) is now owned by `commission_engine`
        (online orders → Razorpay Route split at capture time; cash orders →
        Commission Ledger Entry + wallet/online-netoff/autopay waterfall).
        The on_update hook in commission_engine fires from hooks.py and
        handles accrual + void. We keep only the *other* per-order side
        effects here.
        """
        # ── Loyalty Settlement ─────────────────────────────────────────────
        # Flip pending loyalty entries to is_settled=1 once the order has
        # reached a billable state, so the coins become spendable.
        if self.status in ["confirmed", "completed", "billed"] or self.payment_status == "completed":
            frappe.db.sql("""
                UPDATE `tabRestaurant Loyalty Entry`
                SET is_settled = 1
                WHERE customer = %s AND restaurant = %s
                  AND reference_doctype = 'Order' AND reference_name = %s
                  AND is_settled = 0
            """, (self.platform_customer, self.restaurant, self.name))

        # ── Cancellation: revert earned loyalty ────────────────────────────
        # Commission refund on cancellation is handled by
        # commission_engine.void_for_order (which also refunds wallet sweeps
        # made under the new model). Here we only roll back loyalty.
        if self.status == "cancelled":
            frappe.db.sql("""
                DELETE FROM `tabRestaurant Loyalty Entry`
                WHERE reference_doctype = 'Order' AND reference_name = %s
                  AND transaction_type = 'Earn'
            """, (self.name,))





