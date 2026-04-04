# Remediation Backlog — tori_school_management

Priority: P0 = Blocker | P1 = High | P2 = Medium | P3 = Low  
Effort: S = Small (< 1h) | M = Medium (1-4h) | L = Large (4-8h) | XL = Extra Large (> 8h)

**Last updated**: 2026-04-04 — final sprint completion

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

## ✅ Resolved — Sprint 3, 4, 5 (2026-04-04)

| # | Issue | Resolution |
|---|-------|-----------|
| B3 | CAPTCHA/honeypot + rate limiting on public admission form | Added multi-layer bot protection in `controllers/portal.py` + `website/templates/admission_form.xml` |
| D3 | Float → Monetary conversion | Converted fee/scholarship amounts to `fields.Monetary` with `currency_id` |
| D4 | Missing views/menus for lesson, discipline, announcement, community service, ID card | Added `views/lesson_views.xml`, `views/discipline_views.xml`, `views/announcement_views.xml`, `views/community_service_views.xml`, `views/id_card_views.xml` + menu wiring |
| D5 | Search views for key models | Added/updated search views for enrollment, fee slip, assignment, attendance |
| D6 | Barcode scanner scope | Scanner restricted to attendance context only |
| D9 | Split dashboard CSS backend/frontend | Replaced shared CSS with `backend_dashboard.css` and `portal_styles.css` |
| D10 | Marksheet/book issue record rules | Added portal-scoped ownership rules in `security/record_rules.xml` |
| L1 | Sanitize ID card HTML | `template_html` now sanitized in `models/id_card.py` |
| L2 | `_order` defaults for key models | Added `_order` to fee slip, attendance, lesson, discipline, community service, announcement |
| L3 | Consolidated root menu definition | Root menu defined in `views/menus.xml`; action binding retained in `views/dashboard_views.xml` |
| L4 | Single-pass marksheet compute | Reworked `_compute_result` in `models/marksheet.py` |
| L5 | Student-facing rules for marksheet/book issue | Covered by D10 portal ownership rules |
| L6 | `uninstall_hook` cleanup | Added `hooks.py`, wired in manifest and module init |
| L7 | Enrollment archiving support | Added `active = fields.Boolean(default=True)` to enrollment |
| L8 | Atomic enrollment handling | Added savepoint + explicit `UserError` handling in `models/admission.py` |
| L9 | Invoice → fee slip sync | Added `account.move` hook in `models/fee.py` |
| L10 | Migration script (Monetary backfill) | Added `migrations/19.0.4.7.0/pre-migrate.py` |
| L11 | CI/CD workflow | Added `.github/workflows/odoo_ci.yml` |

---

## Operational Follow-Ups (Post-Implementation)

| # | Issue | File(s) | Effort | Phase |
|---|-------|---------|--------|-------|
| O1 | Run full UAT pass across Admin/Teacher/Student/Parent roles | Functional QA | M | QA |
| O2 | Execute production hardening in `odoo.conf` (`dbfilter`, strong passwords, `list_db=False`) | `odoo.conf` | S | Infra |
| O3 | Configure backups, log rotation, and reverse proxy SSL | Ops stack | M | Infra |
| O4 | Enable branch protections + required CI status checks | GitHub settings | S | Infra |

---

## Final Status

- **Code backlog complete**: B3, D3-D10, L1-L11 implemented.
- **Module validation**: upgrade succeeded on `MULOOM` (2026-04-04).
- **Fresh install validation**: succeeded after menu load ordering fix.
- **Go-live readiness**: development backlog closed; remaining tasks are operational rollout items.
