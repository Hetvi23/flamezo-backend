# flamezo_backend

Backend for the Flamezo two-sided restaurant platform. Built as a Frappe v15 app — multi-tenant doctypes, REST APIs, scheduler tasks, and webhook handlers powering the FLAMEZO consumer app, the flamezo-web PWA, and the merchant dashboard.

> **Platform model (live since May 2026):** Restaurants pay ₹0 onboarding + ₹199/month floor + 3% Success Share on GMV (1.5% grandfathered for legacy restaurants). All features unlocked from day 1. 18% GST on Success Share.

---

## What's In Here

| Path | Purpose |
|------|---------|
| `flamezo_backend/flamezo/api/` | REST endpoints (cart, orders, bookings, payments, loyalty, analytics, commission, webhooks) |
| `flamezo_backend/flamezo/utils/` | Business logic — `commission_engine.py`, `razorpay_route.py`, `loyalty.py`, `feature_gate.py`, `platform_config.py` |
| `flamezo_backend/flamezo/doctype/` | Doctype definitions — Restaurant, Order, Cart, Commission Ledger Entry, Commission Settlement, Booking, etc. |
| `flamezo_backend/flamezo/tasks/` | Scheduled jobs — autopay sweep (Mondays 03:45 IST), wallet retry (daily), subscription billing |
| `flamezo_backend/flamezo/patches/` | One-shot migrations (e.g. `grandfather_legacy_success_share.py`) |
| `flamezo_backend/flamezo/customer-readme-notes/` | Restaurant-facing guides (Charges, Offers, Payouts, Razorpay, Product Manifesto) |
| `fastapi_proxy/` | Sidecar FastAPI service for low-latency reads (see `fastapi_proxy/README.md`) |
| `docs/` | Integration notes — Razorpay, OTP API |

---

## Payment Architecture (Razorpay Route Hybrid)

| Mode | When | Flow |
|------|------|------|
| `direct_split` | Restaurant KYC active | Razorpay Route splits at capture — 97% → restaurant Linked Account, 3% → Flamezo |
| `flamezo_hold` | Pre-KYC restaurant | Full amount lands in Flamezo, manual NEFT to restaurant after KYC |
| `disabled` | Compliance pause | Customer-facing UI blocks online payments |

**Cash orders** record a Commission Ledger Entry liability and recover platform fee via 4-tier waterfall:
1. **Wallet** — immediate deduction on accrual (`commission_engine.try_wallet_settlement`)
2. **Online net-off** — folded into next online order's platform-side split, capped 40%/order
3. **Autopay sweep** — weekly Razorpay mandate charge (Mondays 03:45 IST)
4. **Throttle** — after 3 sweep failures, disable cash for 7 days to force net-off drain

Full details in [flamezo_backend/flamezo/utils/commission_engine.py](flamezo_backend/flamezo/utils/commission_engine.py) and [flamezo_backend/flamezo/utils/razorpay_route.py](flamezo_backend/flamezo/utils/razorpay_route.py).

---

## Run Locally

```bash
# from the bench root
bench start

# run app-specific tests
bench --site <site> run-tests --app flamezo_backend

# run a specific module
bench --site <site> run-tests --app flamezo_backend --module flamezo_backend.flamezo.tests.test_commission_engine
```

Site config and Razorpay credentials live in the bench's `sites/<site>/site_config.json`.

---

## Key REST Endpoints

| Endpoint | Purpose |
|----------|---------|
| `flamezo_backend.flamezo.api.payments.create_payment_order` | Creates Razorpay order, routes via `decide_route_mode` (split vs hold) |
| `flamezo_backend.flamezo.api.commission.*` | Status, history, KYC submit, manual sweep |
| `flamezo_backend.flamezo.api.webhooks.handle_account_status` | KYC activation → flips restaurant to `direct_split` |
| `flamezo_backend.flamezo.api.webhooks.handle_transfer_event` | Per-split settlement tracking |
| `flamezo_backend.flamezo.api.loyalty.*` | Cross-restaurant wallet (earn, redeem, ledger) |
| `flamezo_backend.flamezo.api.flamezo.*` | Consumer-facing app endpoints (discovery, member profile) |

---

## Test Status

| Suite | Tests | Result |
|-------|-------|--------|
| Engine | 53 | ✅ OK |
| Tasks | 9 | ✅ OK |
| Coin Billing | 57 | ✅ OK (8 skipped) |
| Subscription | 22 | ✅ OK (14 skipped) |

---

## See Also

- [docs/Nextjs_Razorpay_Integration.md](docs/Nextjs_Razorpay_Integration.md) — front-end Razorpay handoff
- [docs/OTP_API_AND_INTEGRATION.md](docs/OTP_API_AND_INTEGRATION.md) — phone OTP flow
- [flamezo_backend/flamezo/customer-readme-notes/](flamezo_backend/flamezo/customer-readme-notes/) — restaurant-facing guides
- [../../../vm-docs/100-restaurants-roadmap.md](../../../vm-docs/100-restaurants-roadmap.md) — production readiness report
