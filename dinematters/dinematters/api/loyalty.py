# Copyright (c) 2026, Dinematters and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt, cint, now_datetime, get_datetime_str
from dinematters.dinematters.utils.api_helpers import validate_restaurant_for_api
from dinematters.dinematters.utils.feature_gate import require_plan
from dinematters.dinematters.utils.customer_helpers import (
	normalize_phone, 
	get_or_create_customer,
	get_customer_token,
	validate_customer_session
)
import json
import random
import string

@frappe.whitelist(allow_guest=True)
@require_plan('DIAMOND')
def get_loyalty_summary(restaurant_id, phone):
	"""
	GET /api/method/dinematters.dinematters.api.loyalty.get_loyalty_summary
	Get customer's loyalty balance and history for a specific restaurant
	"""
	try:
		restaurant = validate_restaurant_for_api(restaurant_id)
		normalized_phone = normalize_phone(phone)
		if not normalized_phone:
			return {"success": False, "error": {"code": "INVALID_PHONE", "message": "Invalid phone number"}}
		
		# Production Auth Gate
		session_token = get_customer_token()
		if not validate_customer_session(normalized_phone, session_token):
			return {"success": False, "error": {"code": "SECURE_SESSION_INVALID", "message": "Authentication required"}}
		
		customer = get_or_create_customer(normalized_phone)
		
		# Get all point entries
		entries = frappe.get_all(
			"Restaurant Loyalty Entry",
			filters={"customer": customer.name, "restaurant": restaurant},
			fields=["transaction_type", "coins", "reason", "posting_date", "reference_doctype", "reference_name", "creation", "is_settled"],
			order_by="creation desc"
		)
		
		from dinematters.dinematters.utils.loyalty import get_loyalty_balance, get_loyalty_tier
		balance = get_loyalty_balance(customer.name, restaurant)
		pending_balance = get_loyalty_balance(customer.name, restaurant, include_pending=True) - balance
		tier = get_loyalty_tier(customer.name, restaurant)
		
		# Expiring soon (within 30 days)
		# We sum gross Earn coins expiring in the window, then cap at actual balance.
		# This prevents overstating the amount when coins have already been redeemed.
		from frappe.utils import add_days, today
		expiring_soon_filters = {
			"customer": customer.name,
			"restaurant": restaurant,
			"is_settled": 1,
			"transaction_type": "Earn",
			"expiry_date": ["between", [today(), add_days(today(), 30)]]
		}
		expiring_soon_entries = frappe.get_all("Restaurant Loyalty Entry", filters=expiring_soon_filters, fields=["coins"])
		gross_expiring = sum(e.coins for e in expiring_soon_entries)
		expiring_soon_balance = min(gross_expiring, balance)
		
		return {
			"success": True,
			"data": {
				"balance": balance,
				"pending_balance": pending_balance,
				"expiring_soon_balance": expiring_soon_balance,
				"tier": tier,
				"transactions": entries
			}
		}
	except Exception as e:
		frappe.log_error(f"Error in get_loyalty_summary: {str(e)}")
		return {"success": False, "error": {"code": "LOYALTY_FETCH_ERROR", "message": str(e)}}

@frappe.whitelist(allow_guest=True)
def get_loyalty_config(restaurant_id):
	"""Get loyalty configurations for admin and cart — only exposes safe frontend fields."""
	try:
		restaurant = validate_restaurant_for_api(restaurant_id)
		if not frappe.db.exists("Restaurant Loyalty Config", {"restaurant": restaurant}):
			return {"success": True, "data": None}

		prog_name = frappe.db.get_value("Restaurant Loyalty Config", {"restaurant": restaurant}, "name")
		config = frappe.db.get_value(
			"Restaurant Loyalty Config",
			prog_name,
			[
				"program_name", "points_per_inr", "coin_value_in_inr",
				"min_redemption_threshold", "min_billing_for_redemption",
				"loyalty_expiry_months", "earn_on_status",
				"share_reward_coins", "min_unique_opens_for_reward",
				"coins_per_unique_open", "max_opens_rewarded_per_share",
				"referral_order_reward_coins", "new_user_welcome_reward_coins",
				"welcome_coupon_discount",
				"tier_silver_threshold", "tier_gold_threshold",
				"tier_platinum_threshold", "birthday_bonus_coins"
			],
			as_dict=True
		)
		return {"success": True, "data": config}
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Loyalty Get Config Error")
		return {"success": False, "error": str(e)}

@frappe.whitelist(allow_guest=True)
@require_plan('DIAMOND')
def generate_referral_link(restaurant_id, phone, platform="WhatsApp"):
	"""
	POST /api/method/dinematters.dinematters.api.loyalty.generate_referral_link
	Generate or get a unique referral link for a customer
	"""
	try:
		restaurant = validate_restaurant_for_api(restaurant_id)
		normalized_phone = normalize_phone(phone)
		if not normalized_phone:
			return {"success": False, "error": {"code": "INVALID_PHONE", "message": "Invalid phone number"}}
			
		# Production Auth Gate
		session_token = get_customer_token()
		if not validate_customer_session(normalized_phone, session_token):
			return {"success": False, "error": {"code": "SECURE_SESSION_INVALID", "message": "Authentication required"}}
		
		customer = get_or_create_customer(normalized_phone)
		
		# Check if link already exists for this restaurant
		existing_link = frappe.db.get_value(
			"Referral Link",
			{"referrer": customer.name, "restaurant": restaurant},
			["name", "identifier"],
			as_dict=True
		)
		
		if existing_link:
			identifier = existing_link.identifier
		else:
			# Generate unique identifier / Personalized Slug
			name_part = customer.customer_name or customer.name
			# Slugify and take first part
			slug_base = "".join(e for e in name_part if e.isalnum()).lower()[:10]
			rand_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
			identifier = f"{slug_base}-{rand_part}"
			
			while frappe.db.exists("Referral Link", {"identifier": identifier}):
				rand_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
				identifier = f"{slug_base}-{rand_part}"
			
			link_doc = frappe.get_doc({
				"doctype": "Referral Link",
				"referrer": customer.name,
				"restaurant": restaurant,
				"identifier": identifier,
				"platform": platform,
				"is_active": 1,
				"rewarded_opens_in_cycle": 0
			})
			link_doc.insert(ignore_permissions=True)
		
		from dinematters.dinematters.utils.config_helpers import get_app_base_url
		base_url = get_app_base_url()
		referral_url = f"{base_url.rstrip('/')}/{restaurant_id}/invite/{identifier}"
		
		return {
			"success": True,
			"data": {
				"identifier": identifier,
				"link": referral_url
			}
		}
	except Exception as e:
		frappe.log_error(f"Error in generate_referral_link: {str(e)}")
		return {"success": False, "error": {"code": "REFERRAL_LINK_ERROR", "message": str(e)}}

@frappe.whitelist(allow_guest=True)
def track_referral_visit(identifier, ip_address=None, user_agent=None):
	"""
	POST /api/method/dinematters.dinematters.api.loyalty.track_referral_visit
	Track a visit to a referral link. ONLY records the visit — no coins awarded here.
	Coins are awarded in claim_referral_reward() after phone verification.
	"""
	try:
		# Auto-detect IP and User agent if not passed (Production Level Tracking)
		try:
			if not ip_address and frappe.request:
				ip_address = frappe.request.remote_addr
		except Exception:
			pass
		try:
			if not user_agent and frappe.request:
				user_agent = frappe.request.headers.get('User-Agent')
		except Exception:
			pass

		link_name = frappe.db.get_value("Referral Link", {"identifier": identifier}, "name")
		if not link_name:
			return {"success": False, "error": {"code": "LINK_NOT_FOUND", "message": "Invalid referral link"}}

		link_doc = frappe.get_doc("Referral Link", link_name)

		# Check if this identifier + IP has visited before
		is_unique = not frappe.db.exists("Referral Visit", {
			"referral_link": link_name,
			"ip_address": ip_address
		})

		visit_doc = frappe.get_doc({
			"doctype": "Referral Visit",
			"referral_link": link_name,
			"ip_address": ip_address,
			"user_agent": user_agent,
			"is_unique": 1 if is_unique else 0,
			"timestamp": now_datetime()
		})
		try:
			visit_doc.insert(ignore_permissions=True)
			frappe.db.commit() # Ensure visit is saved immediately
		except Exception as insert_err:
			# If DB unique constraint fires (concurrent duplicate request from same IP),
			# treat this visit as non-unique — no problem.
			err_str = str(insert_err).lower()
			if "duplicate" in err_str or "unique" in err_str:
				is_unique = False
				frappe.db.rollback()
			else:
				raise

		# NOTE: No coins awarded here. Rewards are deferred to claim_referral_reward()
		# which fires after the referee verifies their phone number. This prevents
		# bot/spam abuse where fake link clicks farm referrer coins.

		return {
			"success": True,
			"data": {
				"restaurant_id": link_doc.restaurant,
				"referral_id": identifier,
				"is_unique": is_unique
			}
		}
	except Exception as e:
		frappe.log_error("Referral Tracking Error", str(e))
		return {"success": False, "error": {"code": "TRACKING_ERROR", "message": str(e)}}


@frappe.whitelist(allow_guest=True)
@require_plan('DIAMOND')
def claim_referral_reward(restaurant_id, referral_id, phone):
	"""
	POST /api/method/dinematters.dinematters.api.loyalty.claim_referral_reward
	Called after phone verification to atomically award:
	  1. Welcome Bonus to the referee (new user)
	  2. Referral Share to the referrer (if within cycle limit)
	This is the fraud-safe approach — no coins until identity is verified.
	"""
	try:
		restaurant = validate_restaurant_for_api(restaurant_id)
		normalized_phone = normalize_phone(phone)
		if not normalized_phone:
			return {"success": False, "error": {"code": "INVALID_PHONE", "message": "Invalid phone number"}}

		# Auth gate — must have a valid session (post-OTP)
		session_token = get_customer_token()
		if not validate_customer_session(normalized_phone, session_token):
			return {"success": False, "error": {"code": "SECURE_SESSION_INVALID", "message": "Authentication required"}}

		# 1. Validate the referral link belongs to this restaurant
		link_info = frappe.db.get_value(
			"Referral Link",
			{"identifier": referral_id},
			["name", "referrer", "restaurant", "rewarded_opens_in_cycle"],
			as_dict=True
		)
		if not link_info:
			return {"success": False, "error": {"code": "LINK_NOT_FOUND", "message": "Invalid referral link"}}

		if link_info.restaurant != restaurant:
			return {"success": False, "error": {"code": "RESTAURANT_MISMATCH", "message": "Referral link does not belong to this restaurant"}}

		# 2. Get or create the referee customer
		referee = get_or_create_customer(normalized_phone)

		# 3. Idempotency: check if referee already claimed Welcome Bonus for this restaurant
		already_rewarded = frappe.db.exists("Restaurant Loyalty Entry", {
			"customer": referee.name,
			"restaurant": restaurant,
			"reason": "Welcome Bonus"
		})
		if already_rewarded:
			return {"success": False, "error": {"code": "ALREADY_CLAIMED", "message": "Welcome bonus already claimed"}}

		# 4. Prevent self-referral
		if link_info.referrer == referee.name:
			return {"success": False, "error": {"code": "SELF_REFERRAL", "message": "Cannot use your own referral link"}}

		# 5. Get loyalty config
		loyalty_prog = frappe.db.get_value(
			"Restaurant Loyalty Config",
			{"restaurant": restaurant, "is_active": 1},
			["new_user_welcome_reward_coins", "coins_per_unique_open", "max_opens_rewarded_per_share"],
			as_dict=True
		)
		if not loyalty_prog:
			return {"success": False, "error": {"code": "CONFIG_NOT_FOUND", "message": "Loyalty not configured"}}

		welcome_coins = int(loyalty_prog.new_user_welcome_reward_coins or 50)
		referral_share_coins = int(loyalty_prog.coins_per_unique_open or 2)
		max_limit = int(loyalty_prog.max_opens_rewarded_per_share or 7)
		current_cycle = int(frappe.db.get_value("Referral Link", link_info.name, "rewarded_opens_in_cycle") or 0)

		# 6. Award Welcome Bonus to referee
		credit_loyalty_points(
			customer=referee.name,
			restaurant=restaurant,
			coins=welcome_coins,
			reason="Welcome Bonus",
			ref_doctype="Referral Link",
			ref_name=link_info.name
		)

		# 7. Award Referral Share to referrer (if within cycle limit)
		referrer_coins_awarded = 0
		if current_cycle < max_limit:
			credit_loyalty_points(
				customer=link_info.referrer,
				restaurant=restaurant,
				coins=referral_share_coins,
				reason="Referral Share",
				ref_doctype="Referral Link",
				ref_name=link_info.name
			)
			referrer_coins_awarded = referral_share_coins
			frappe.db.set_value("Referral Link", link_info.name, "rewarded_opens_in_cycle", current_cycle + 1)

		# 8. Mark referral visit as converted (best-effort, not blocking)
		try:
			frappe.db.sql("""
				UPDATE `tabReferral Visit`
				SET status = 'Converted'
				WHERE referral_link = %s AND status != 'Converted'
				ORDER BY creation DESC LIMIT 1
			""", (link_info.name,))
		except Exception:
			pass

		frappe.db.commit()
		return {
			"success": True,
			"data": {
				"welcome_coins": welcome_coins,
				"referrer_coins": referrer_coins_awarded
			}
		}
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Claim Referral Reward Error")
		return {"success": False, "error": {"code": "CLAIM_ERROR", "message": str(e)}}

@frappe.whitelist(allow_guest=True)
def get_referral_details(identifier):
	"""
	GET /api/method/dinematters.dinematters.api.loyalty.get_referral_details
	Get basic details about a referral link for social sharing previews
	"""
	try:
		link_info = frappe.db.get_value(
			"Referral Link", 
			{"identifier": identifier}, 
			["referrer", "restaurant"], 
			as_dict=True
		)
		if not link_info:
			return {"success": False, "message": "Link not found"}
			
		referrer_full_name = frappe.db.get_value("Customer", link_info.referrer, "customer_name") or link_info.referrer
		# Swiggy/Zomato style: Show first name only for privacy
		referrer_name = referrer_full_name.split(' ')[0] if referrer_full_name else link_info.referrer
		restaurant_name = frappe.db.get_value("Restaurant", link_info.restaurant, "name")
		
		# Get restaurant config for images
		logo = frappe.db.get_value("Restaurant Config", {"restaurant": link_info.restaurant}, "logo")
		# Using logo as fallback for banner as ‘banner_image’ field doesn’t exist
		banner = logo 
		
		return {
			"success": True,
			"data": {
				"referrer": referrer_name,
				"restaurant_name": restaurant_name,
				"restaurant_id": link_info.restaurant,
				"logo": logo,
				"banner": banner
			}
		}
	except Exception as e:
		return {"success": False, "error": str(e)}
		
def reset_referral_cycle(customer, restaurant):
	"""
	Resets the rewarded_opens_in_cycle counter for all referral links 
	owned by a customer at a specific restaurant.
	Called after order placement to 'renew' the sharing limit.
	"""
	try:
		frappe.db.sql("""
			UPDATE `tabReferral Link` 
			SET rewarded_opens_in_cycle = 0 
			WHERE referrer = %s AND restaurant = %s
		""", (customer, restaurant))
		frappe.db.commit()
		return True
	except Exception as e:
		frappe.log_error(f"Error in reset_referral_cycle: {str(e)}")
		return False

def process_referral_welcome_bonus(customer, restaurant, referral_id):
	"""
	Awards the Welcome Bonus instantly upon signup/verification.
	Validates that the referral_id belongs to the specified restaurant.
	"""
	try:
		# 1. Validate the referral link
		link_info = frappe.db.get_value("Referral Link", {"identifier": referral_id}, ["name", "restaurant"], as_dict=True)
		if not link_info:
			return False
		
		# Strict Scoping: Referral must match the restaurant the user is currently joining
		if link_info.get("restaurant") != restaurant:
			return False
			
		# 2. Check if customer already received a Welcome Bonus for this restaurant
		# This prevents duplicate claims even if they re-verify
		from dinematters.dinematters.utils.loyalty import get_loyalty_balance
		already_rewarded = frappe.db.exists("Restaurant Loyalty Entry", {
			"customer": customer,
			"restaurant": restaurant,
			"reason": "Welcome Bonus"
		})
		
		if already_rewarded:
			return False
			
		# 3. Get loyalty config
		loyalty_prog = frappe.get_doc("Restaurant Loyalty Config", {"restaurant": restaurant, "is_active": 1})
		if not loyalty_prog:
			return False
			
		# 4. Award the Welcome Bonus
		coins = loyalty_prog.new_user_welcome_reward_coins or 50
		credit_loyalty_points(
			customer=customer,
			restaurant=restaurant,
			coins=coins,
			reason="Welcome Bonus",
			ref_doctype="Referral Link",
			ref_name=link_info.name
		)
		
		frappe.db.commit()
		return True
	except Exception as e:
		frappe.log_error(f"Error in process_referral_welcome_bonus: {str(e)}")
		return False

def credit_loyalty_points(customer, restaurant, coins, reason, ref_doctype=None, ref_name=None, transaction_type="Earn"):
	"""Helper function to create a Restaurant Loyalty Entry"""
	from dinematters.dinematters.utils.loyalty import add_loyalty_coins, redeem_loyalty_coins
	if transaction_type == "Earn":
		return add_loyalty_coins(customer, restaurant, coins, reason, ref_doctype, ref_name)
	else:
		return redeem_loyalty_coins(customer, restaurant, coins, reason, ref_doctype, ref_name)


@frappe.whitelist()
@require_plan('DIAMOND')
def update_loyalty_config(restaurant_id, config, enable_loyalty=None):
	"""Update loyalty configurations for admin"""
	try:
		# Correct logging: title is first, message (config) is second
		frappe.log_error("Loyalty API Update Call", f"Updating for {restaurant_id} with config: {config}")
		
		restaurant = validate_restaurant_for_api(restaurant_id, frappe.session.user)
		if isinstance(config, str):
			config = json.loads(config)
			
		# Handle Restaurant Loyalty Config record
		if frappe.db.exists("Restaurant Loyalty Config", {"restaurant": restaurant}):
			prog_name = frappe.db.get_value("Restaurant Loyalty Config", {"restaurant": restaurant}, "name")
			prog_doc = frappe.get_doc("Restaurant Loyalty Config", prog_name)
			prog_doc.update(config)
			prog_doc.save(ignore_permissions=True)
			frappe.log_error("Restaurant Loyalty Config Updated", f"Updated {prog_doc.name}")
		else:
			config["doctype"] = "Restaurant Loyalty Config"
			config["restaurant"] = restaurant
			prog_doc = frappe.get_doc(config)
			prog_doc.insert(ignore_permissions=True)
			frappe.log_error("Restaurant Loyalty Config Created", f"Created {prog_doc.name}")
		
		# Update Restaurant enable_loyalty
		if enable_loyalty is not None:
			frappe.db.set_value("Restaurant", restaurant, "enable_loyalty", 1 if enable_loyalty else 0)
			frappe.db.set_value("Restaurant Config", {"restaurant": restaurant}, "enable_loyalty", 1 if enable_loyalty else 0)
			
		frappe.db.commit()
		return {"success": True}
	except Exception as e:
		frappe.log_error("Loyalty Save Error", frappe.get_traceback())
		return {"success": False, "error": str(e)}

@frappe.whitelist()
@require_plan('DIAMOND')
def get_customer_insights(restaurant_id, search_query=None):
	"""
	Get list of customers with their points for a restaurant.
	"""
	try:
		restaurant = validate_restaurant_for_api(restaurant_id, frappe.session.user)

		# Get all customers who have ever had a loyalty entry at this restaurant
		# or placed an order, then compute all metrics in bulk SQL (no N+1).
		
		# Find customers via Restaurant Loyalty Entry
		customer_names = frappe.get_all(
			"Restaurant Loyalty Entry",
			filters={"restaurant": restaurant},
			pluck="customer",
			distinct=True
		)
		
		# Also find customers via Orders
		order_customers = frappe.get_all(
			"Order",
			filters={"restaurant": restaurant, "platform_customer": ["is", "set"]},
			pluck="platform_customer",
			distinct=True
		)
		
		all_customer_ids = list(set(customer_names + order_customers))

		if not all_customer_ids:
			return {"success": True, "data": []}

		if search_query:
			# Filter these IDs by customer name/phone
			matching_customers = frappe.get_all(
				"Customer",
				filters={
					"name": ["in", all_customer_ids],
					"or": [
						{"customer_name": ["like", f"%{search_query}%"]},
						{"phone": ["like", f"%{search_query}%"]}
					]
				},
				pluck="name"
			)
			all_customer_ids = matching_customers

		if not all_customer_ids:
			return {"success": True, "data": []}

		placeholders = ",".join(["%s"] * len(all_customer_ids))

		# ── Single SQL: net spendable balance per customer ────────────────────────
		balance_rows = frappe.db.sql(f"""
			SELECT
				customer,
				GREATEST(0, SUM(
					CASE
						WHEN transaction_type = 'Earn'
						 AND is_settled = 1
						 AND (expiry_date IS NULL OR expiry_date >= CURDATE())
						THEN coins
						WHEN transaction_type = 'Redeem'
						 AND is_settled = 1
						 AND (expiry_date IS NULL OR expiry_date >= CURDATE())
						THEN -coins
						ELSE 0
					END
				)) AS net_balance
			FROM `tabRestaurant Loyalty Entry`
			WHERE restaurant = %s AND customer IN ({placeholders})
			GROUP BY customer
		""", tuple([restaurant] + all_customer_ids), as_dict=True)
		balance_map = {r.customer: int(r.net_balance or 0) for r in balance_rows}

		# ── Single SQL: lifetime Earn coins per customer (for tier) ───────────────
		lifetime_rows = frappe.db.sql(f"""
			SELECT customer, COALESCE(SUM(coins), 0) AS lifetime_coins
			FROM `tabRestaurant Loyalty Entry`
			WHERE restaurant = %s AND customer IN ({placeholders}) AND transaction_type = 'Earn'
			GROUP BY customer
		""", tuple([restaurant] + all_customer_ids), as_dict=True)
		lifetime_map = {r.customer: int(r.lifetime_coins or 0) for r in lifetime_rows}

		# ── Single SQL: referral stats for all customers ──────────────────────────
		referral_rows = frappe.db.sql(f"""
			SELECT
				l.referrer,
				COALESCE(SUM(l.rewarded_opens_in_cycle), 0) AS cycle_opens,
				COALESCE(SUM(v_counts.unique_opens), 0) AS total_opens
			FROM `tabReferral Link` l
			LEFT JOIN (
				SELECT referral_link, COUNT(*) AS unique_opens
				FROM `tabReferral Visit`
				WHERE is_unique = 1
				GROUP BY referral_link
			) v_counts ON v_counts.referral_link = l.name
			WHERE l.restaurant = %s AND l.referrer IN ({placeholders})
			GROUP BY l.referrer
		""", tuple([restaurant] + all_customer_ids), as_dict=True)
		referral_map = {r.referrer: r for r in referral_rows}

		# ── Bulk fetch customer fields ─────────────────────────────────────────────
		customer_docs = frappe.get_all(
			"Customer",
			filters={"name": ["in", all_customer_ids]},
			fields=["name", "customer_name", "phone", "date_of_birth", "modified"]
		)

		# ── Tier thresholds (single config fetch) ─────────────────────────────────
		from dinematters.dinematters.utils.loyalty import get_loyalty_tier
		tier_config = frappe.db.get_value(
			"Restaurant Loyalty Config",
			{"restaurant": restaurant, "is_active": 1},
			["tier_silver_threshold", "tier_gold_threshold", "tier_platinum_threshold"],
			as_dict=True
		) or {}
		silver_t = int(tier_config.get("tier_silver_threshold") or 500)
		gold_t   = int(tier_config.get("tier_gold_threshold") or 2000)
		plat_t   = int(tier_config.get("tier_platinum_threshold") or 5000)

		def _tier_from_lifetime(lt):
			if lt >= plat_t:   return "Platinum"
			if lt >= gold_t:   return "Gold"
			if lt >= silver_t: return "Silver"
			return "Bronze"

		results = []
		for c in customer_docs:
			cid = c.name
			balance = balance_map.get(cid, 0)
			lifetime = lifetime_map.get(cid, 0)
			ref = referral_map.get(cid, frappe._dict(total_opens=0, cycle_opens=0))
			results.append({
				"id": cid,
				"name": c.customer_name or cid,
				"phone": c.phone,
				"birthday": str(c.date_of_birth) if c.date_of_birth else None,
				"balance": balance,
				"tier": _tier_from_lifetime(lifetime),
				"lifetime_coins": lifetime,
				"referral_opens": int(ref.total_opens or 0),
				"cycle_opens": int(ref.cycle_opens or 0),
				"last_active": c.modified
			})

		# Sort by balance descending
		results.sort(key=lambda x: x["balance"], reverse=True)

		return {"success": True, "data": results}
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Loyalty Insights Error")
		return {"success": False, "error": str(e)}

@frappe.whitelist()
@require_plan('DIAMOND')
def get_customer_transactions(restaurant_id, customer_id):
	"""
	Get all loyalty transactions for a specific customer and restaurant
	"""
	try:
		restaurant = validate_restaurant_for_api(restaurant_id, frappe.session.user)
		
		# Get all loyalty entries for this customer at this restaurant
		transactions = frappe.get_all(
			"Restaurant Loyalty Entry",
			filters={"customer": customer_id, "restaurant": restaurant},
			fields=["transaction_type", "coins", "reason", "posting_date", "creation", "reference_doctype", "reference_name"],
			order_by="creation desc"
		)
		
		return {"success": True, "data": transactions}
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Loyalty Transactions Error")
		return {"success": False, "error": str(e)}

@frappe.whitelist()
@require_plan('DIAMOND')
def adjust_customer_points(restaurant_id, customer_id, coins, reason, transaction_type="Earn"):
	"""
	Manually adjust customer points (for admin use).
	"""
	try:
		restaurant = validate_restaurant_for_api(restaurant_id, frappe.session.user)
		coins = cint(coins)
		
		if coins <= 0:
			return {"success": False, "error": "Coins must be greater than 0"}
			
		from dinematters.dinematters.api.loyalty import credit_loyalty_points
		credit_loyalty_points(customer_id, restaurant, coins, reason or "Manual Adjustment", transaction_type=transaction_type)
		
		return {
			"success": True, 
			"message": f"Successfully {transaction_type.lower()}ed {coins} coins"
		}
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Loyalty Adjustment Error")
		return {"success": False, "error": str(e)}
