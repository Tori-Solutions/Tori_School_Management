# Remediation Backlog — tori_school_management

Priority: P0 = Blocker | P1 = High | P2 = Medium | P3 = Low  
Effort: S = Small (< 1h) | M = Medium (1-4h) | L = Large (4-8h) | XL = Extra Large (> 8h)

## P0 — Critical Blockers (Must-Fix Before Go-Live)

| # | Issue | File(s) | Effort | Phase |
|---|-------|---------|--------|-------|
| B1 | Add multi-company record rules for all models with `company_id` (~25 rules) | `security/record_rules.xml` | L | Security |
| B2 | Restrict wizard ACLs from `base.group_user` to `group_education_admin` | `security/ir.model.access.csv` | S | Security |
| B3 | Add CAPTCHA/honeypot to public admission form + rate limiting | `controllers/portal.py`, `website/templates/admission_form.xml` | M | Security |
| B4 | Add backend MIME-type and extension validation on photo upload | `controllers/portal.py` | S | Security |
| B5 | Move `test_assets.xml` from manifest `data` to `demo` key | `__manifest__.py` | S | Infra |
| B6 | Create test suite: enrollment, fees, security, admissions | `tests/` (new) | XL | Infra |

## P1 — High Priority

| # | Issue | File(s) | Effort | Phase |
|---|-------|---------|--------|-------|
| C1 | Add group hierarchy: admin implies teacher | `security/security.xml` | S | Security |
| C2 | Fix portal access revoke to actually remove portal group from user | `models/enrollment.py` | S | BizLogic |
| C3 | Add attendance uniqueness constraint (enrollment + date + slot) | `models/attendance.py` | S | DataModel |
| C4 | Add student read ACLs for 11 portal-relevant models | `security/ir.model.access.csv` | S | Security |
| C5 | Secure application status lookup with verification factor | `controllers/portal.py`, portal template | M | Security |
| C6 | Fix overdue cron to use batched `write()` instead of per-field assignment | `models/fee.py` | S | BizLogic |
| C7 | Fix `_compute_dashboard_metrics` to be session-scoped and use correct models | `models/session.py` | M | Perf/BizLogic |

## P2 — Medium Priority

| # | Issue | File(s) | Effort | Phase |
|---|-------|---------|--------|-------|
| D1 | Replace `len(One2many)` with `read_group` in partner and enrollment computes | `models/integration.py`, `models/enrollment.py` | M | Performance |
| D2 | Optimize `cron_generate_recurring_slips` to batch-search and batch-create | `models/fee.py` | M | Performance |
| D3 | Convert Float amount fields to Monetary with currency_id | `models/fee.py`, `models/scholarship.py` | M | DataModel |
| D4 | Create views and menus for lesson, homework, discipline, community service, announcement, ID card | `views/` (new files) | L | Views/UX |
| D5 | Add search views with filters/group-by for enrollment, fee slip, assignment, attendance | `views/` (existing files) | M | Views/UX |
| D6 | Scope barcode attendance scanner service to attendance-only context | `static/src/js/barcode_attendance.js` | M | Views/UX |
| D7 | Fix timetable compute to use TZ-aware date + move imports to module level | `models/timetable.py` | S | BizLogic |
| D8 | Update manifest author from "Your Name" to actual author | `__manifest__.py` | S | Infra |
| D9 | Split `dashboard.css` for backend vs frontend (don't load dark theme on website) | `static/src/css/`, `__manifest__.py` | S | Views/UX |
| D10 | Add record rules for student access to attendance, fee_slips, marksheets | `security/record_rules.xml` | M | Security |

## P3 — Low Priority / Nice-to-Have

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

---

## Suggested Sprint Plan

### Sprint 1 (Go-Live Blockers): B1-B6
- All P0 items
- Target: 2-3 days with testing

### Sprint 2 (High Priority): C1-C7
- All P1 items
- Target: 1-2 days

### Sprint 3 (UX + Performance): D1-D10
- Medium priority items
- Target: 3-4 days

### Sprint 4 (Polish): L1-L10
- Low priority items
- Ongoing
