# Remediation Backlog — tori_school_management

Priority: P0 = Blocker | P1 = High | P2 = Medium | P3 = Low  
Effort: S = Small (< 1h) | M = Medium (1-4h) | L = Large (4-8h) | XL = Extra Large (> 8h)

**Last updated**: 2026-04-03 — post-remediation sprint (commit `579a484`)

---

## ✅ Resolved — Sprint 1 & 2 (commit 579a484, 2026-04-03)

| # | Issue | Resolution |
|---|-------|-----------|
| B1 | Multi-company record rules for all models with `company_id` | Added ~25 rules in `security/record_rules.xml` |
| B2 | Wizard ACLs restricted from `base.group_user` to `group_education_admin` | Updated `security/ir.model.access.csv` |
| B4 | Backend MIME-type and extension validation on photo upload | Hardened `controllers/portal.py` |
| B5 | Move `test_assets.xml` from manifest `data` to `demo` key | Fixed in `__manifest__.py` |
| B6 | Create test suite covering security, fees, and company isolation | Added `tests/__init__.py` + `tests/test_security_and_fees.py` (4 tests, 0 failures) |
| C1 | Group hierarchy: admin implies teacher | Fixed in `security/security.xml` |
| C2 | Portal access revoke removes portal group from user | Fixed in `models/enrollment.py` |
| C3 | Attendance uniqueness constraint (enrollment + date + slot) | Added SQL constraint in `models/attendance.py` |
| C4 | Student read ACLs for 11 portal-relevant models | Added to `security/ir.model.access.csv` |
| C5 | Secure application status lookup | Input hardening in `controllers/portal.py` |
| C6 | Overdue cron uses batched `write()` | Fixed in `models/fee.py` |
| C7 | `_compute_dashboard_metrics` session-scoped with correct models | Fixed in `models/session.py` |
| D1 | Replace `len(One2many)` with `_read_group` in partner/enrollment computes | Fixed in `models/integration.py`, `models/enrollment.py` |
| D2 | `cron_generate_recurring_slips` batch-prefetch and batch-create | Fixed in `models/fee.py` |
| D7 | Fix `_compute_current_academic` to avoid N+1 | Fixed in `models/session.py` |
| D8 | Update manifest author | Fixed in `__manifest__.py` |
| —  | `base_automation` missing from manifest `depends` | Added to `__manifest__.py` |

---

## 🔴 P0 — Critical Blocker (Remaining)

| # | Issue | File(s) | Effort | Phase |
|---|-------|---------|--------|-------|
| B3 | Add CAPTCHA/honeypot to public admission form + rate limiting | `controllers/portal.py`, `website/templates/admission_form.xml` | M | Security |

**This is the only remaining item blocking production go-live.**

---

## 🟡 P2 — Medium Priority (Outstanding)

| # | Issue | File(s) | Effort | Phase |
|---|-------|---------|--------|-------|
| D3 | Convert Float amount fields to Monetary with `currency_id` | `models/fee.py`, `models/scholarship.py` | M | DataModel |
| D4 | Create views and menus for lesson, homework, discipline, community service, announcement, ID card | `views/` (new files) | L | Views/UX |
| D5 | Add search views with filters/group-by for enrollment, fee slip, assignment, attendance | `views/` (existing files) | M | Views/UX |
| D6 | Scope barcode attendance scanner service to attendance-only context | `static/src/js/barcode_attendance.js` | M | Views/UX |
| D9 | Split `dashboard.css` for backend vs frontend (don't load dark theme on website) | `static/src/css/`, `__manifest__.py` | S | Views/UX |
| D10 | Add record rules for student access to marksheet, book issue | `security/record_rules.xml` | M | Security |

---

## 🟢 P3 — Low Priority / Nice-to-Have

| # | Issue | File(s) | Effort | Phase |
|---|-------|---------|--------|-------|
| L1 | Add `Html(sanitize=True)` to `tori.id.card.design.template_html` | `models/id_card.py` | S | Security |
| L2 | Add `_order` to models that lack it (fee.slip, attendance, etc.) | Various model files | S | DataModel |
| L3 | Consolidate menu root definition (menus.xml vs dashboard_views.xml) | `views/menus.xml`, `views/dashboard_views.xml` | S | Views/UX |
| L4 | Optimize marksheet `_compute_result` to single-pass iteration | `models/marksheet.py` | S | Performance |
| L5 | Add student-facing record rules for marksheet, book issue | `security/record_rules.xml` | S | Security |
| L6 | Add `uninstall_hook` to clean up automations/crons cleanly | `__manifest__.py`, hooks.py | S | Infra |
| L7 | Consider adding `active` field on `tori.enrollment` for archival | `models/enrollment.py` | S | DataModel |
| L8 | Add proper error handling in `action_enroll` for partial failure | `models/admission.py` | M | BizLogic |
| L9 | Sync invoice payment status back to fee slip state | `models/fee.py` | M | BizLogic |
| L10 | Add migration scripts for field type changes (Float→Monetary) | `migrations/` | M | Infra |
| L11 | Set up CI/CD pipeline for automated upgrade + test validation | `.github/workflows/` | L | Infra |

---

## Suggested Sprint Plan

### Sprint 3 (Go-Live — one remaining blocker): B3
- Add reCAPTCHA or Odoo website CAPTCHA + honeypot field
- Target: 1 day

### Sprint 4 (Views + UX): D3–D6, D9–D10
- Missing views for 6 models, Float→Monetary, barcode scope
- Target: 3–4 days

### Sprint 5 (Polish): L1–L11
- Low priority items, CI/CD setup
- Ongoing
