# Task Tracker

This file tracks major implementation tasks completed in `tori_school_management`.

## 2026-02-15

- Bootstrap module skeleton
- Added base manifest, initial models, security, and starter views for school operations.

## 2026-02-16

- Core operations expansion
- Completed admissions/enrollment, assignments, attendance, fees, and related core model wiring.

## 2026-03-29

- Website and portal baseline
- Added website templates, public routes, and first pass of portal rendering for school users.

## 2026-03-30

- Integration and stabilization pass
- Added cross-app integrations (Contacts/HR/Accounting), fixed migration compatibility issues, and improved view stability.

## 2026-03-31

- Website discoverability and portal UX
- Added website menu/page records for Admission and Application Status, and introduced school portal navigation tabs.

- Mobile portal polish and parser fixes
- Improved mobile nav scrolling behavior and resolved XML/CSS regressions.

- Documentation synchronization
- Updated README, project report, troubleshooting guide, and error history to reflect website/portal completion.

- Education app icon redesign
- Replaced launcher icon with Odoo-consistent style and updated menu icon binding.

- Test data population
- Added and loaded realistic test assets for admissions, enrollments, fees, attendance, library, and transport.

## 2026-04-01

- Full admission intake replication
- Implemented full multi-section student admission flow on website and backend application forms.

- Bangladesh location masters
- Added district and upazila models and loaded official-style Bangladesh master dataset.

- Hard duplicate prevention
- Enforced duplicate block using DOB + guardian phone + class + session, with public error feedback.

- Upload UX simplification
- Removed birth certificate upload from public form and kept a single top-right student photo upload box.

- Contacts-style address alignment
- Replaced custom address block with native Contacts fields and synced those fields to enrolled student contact.

- CRM-style admissions pipeline
- Migrated from static state grouping to editable stage model with sequence, fold, and setup management.

- Documentation refresh and tracking
- Updated all core markdown documentation files and introduced this ongoing task tracker.

- Dashboard UX overhaul and backend wiring
- Reworked dashboard layout, quick actions, payload API integration, and operational widgets (pipeline health, fee alerts, notices, attendance summary).

- Dashboard scrolling fix
- Added explicit vertical scroll handling for dashboard client action so full content is reachable.

- Enrollment duplicate cleanup and hard prevention
- Removed existing duplicate enrollment groups, rewired related records, added DB uniqueness and model validation, and updated enrollment flow to reuse existing records.

- Admissions kanban avatar polish
- Replaced stacked-text avatar behavior with clean photo/placeholder rendering and corrected card separator text behavior.

## 2026-04-02 / 2026-04-03

- Security hardening sprint
- Added ~25 multi-company record rules for all models with `company_id`.
- Restricted wizard ACLs to `group_education_admin` only.
- Fixed group hierarchy — admin now implies teacher.
- Added student read ACLs for 11 portal-relevant models.
- Added student-scoped backend record rules (enrollments, submissions, attendance, fee slips).
- Hardened portal admission controller with MIME-type, file size, and input validation.
- Fixed portal access revoke to actually remove `base.group_portal` from user.

- Performance optimization sprint
- Migrated all compute methods from deprecated `read_group` to `_read_group` API.
- Eliminated N+1 in recurring fee cron via bulk prefetch and batch create.
- Changed overdue fee cron to batched `write()` instead of per-field assignment.
- Session dashboard metrics now session-scoped and uses correct grouped queries.
- Current academic field computation optimized.

- Data model and infrastructure
- Added attendance uniqueness constraint (enrollment + date + timetable slot).
- Added `base_automation` to manifest `depends` (fixes fresh-install `KeyError`).
- Moved `test_assets.xml` from `data` to `demo` key in manifest.
- Updated manifest author to `Tori Solutions Ltd`.

- Test suite
- Added `tests/__init__.py` and `tests/test_security_and_fees.py`.
- 4 tests covering company isolation, student scoping, and recurring fee cron behavior.
- Resolved Odoo 19 compatibility issues: `TransactionCase` (not `SavepointCase`), `group_ids` (not `groups_id`).
- Handled enterprise module NOT NULL columns without DB defaults via temporary ALTER TABLE DEFAULT pattern.
- All 4 tests passing on both fresh install and upgrade validation.

- Documentation refresh
- Updated `analysis/PRODUCTION_READINESS_REPORT.md` with post-remediation scores (54% → 76%).
- Updated `analysis/REMEDIATION_BACKLOG.md` with resolved/outstanding items.
- Updated all core documentation files.

## 2026-04-04

- Final sprint completion (B3, D3-D10, L1-L11)
- Implemented public admission anti-bot stack: honeypot + CAPTCHA + IP rate limiting.
- Converted fee/scholarship amounts to Monetary fields and added migration backfill support.
- Added missing backend views/actions/menus for lesson, discipline, announcement, community service, and ID card.
- Added search views for enrollment, fee slip, assignment, and attendance.
- Scoped barcode scanning behavior to attendance context only.
- Split shared dashboard CSS into backend-only and portal-only assets.
- Added portal ownership rules for marksheet and book issue visibility.
- Added sanitized HTML for ID card templates and `_order` defaults across key models.
- Added `active` archive flag to enrollments.
- Hardened enrollment creation with savepoint and explicit UserError on failure.
- Added account.move payment-state sync back to fee slips.
- Added uninstall hook and GitHub Actions CI workflow.
- Fixed fresh-install load ordering issue by splitting feature menus into `views/feature_menus.xml` and loading base menus early.
- Fixed Odoo 19 search view parser compatibility (`<group>` in search views without legacy attributes).
- Validated module upgrade on `MULOOM` and fresh install on clean test DB.
