# Tori School Management

Education management addon for Odoo 19.

## Scope

This module provides school operations in one app:

- Admissions and student applications
- Sessions, classes, sections, and enrollments
- Attendance and assignments
- Fees, scholarships, transport, library, and timetable
- Portal pages for student and parent workflows
- Reports, automation, and notifications
- Core ERP integration with Contacts (`res.partner`), HR (`hr.employee`), and Accounting (`account.move`)
- Website integration with public admission/status pages and authenticated portal routes

## Latest Implemented Updates

### 2026-04-03 — Security Hardening, Performance, and Test Suite (commit 579a484)

- **Security**: Added multi-company record rules for all models with `company_id` (~25 rules).
- **Security**: Restricted wizard ACLs from `base.group_user` to `group_education_admin`.
- **Security**: Added student read ACLs for 11 portal-relevant models.
- **Security**: Group hierarchy fixed — admin now implies teacher.
- **Security**: Portal access revoke correctly removes `base.group_portal` from user.
- **Security**: Portal admission controller hardened with MIME-type and input validation.
- **Security**: Student-facing backend record rules added (own enrollments, submissions, attendance, fee slips).
- **Performance**: Migrated all compute methods from deprecated `read_group` API to `_read_group`.
- **Performance**: Recurring fee cron N+1 eliminated with bulk prefetch and batch create.
- **Performance**: Overdue fee cron changed from per-field assignment to batched `write()`.
- **Performance**: Session dashboard metrics query is now session-scoped and grouped correctly.
- **Data model**: Attendance uniqueness constraint added (enrollment + date + timetable slot).
- **Infrastructure**: `base_automation` added to manifest `depends` (fixes fresh-install `KeyError`).
- **Infrastructure**: `test_assets.xml` moved from `data` to `demo` in manifest.
- **Infrastructure**: Author updated in manifest.
- **Tests**: Full test suite added (`tests/` package) — 4 tests, 0 failures on clean install.
  - Company isolation rules
  - Student backend visibility scoping
  - Recurring fee cron creates missing slip exactly once
  - Recurring fee cron ignores one-time elements

- Website and portal integration completed with Admission and Application Status pages.
- Portal navigation improved with breadcrumbs, section tabs, and mobile horizontal scrolling.
- Education app icon refreshed to match Odoo app launcher style.
- Comprehensive test asset dataset added for demo and QA (session/class/students/enrollments/fees/library/transport).
- Public admission form expanded to full multi-section intake flow.
- Public upload area simplified to student photo box only (birth certificate attachment removed from website form).
- Bangladesh location master data added (`64` districts and `494` upazilas/thanas).
- Hard duplicate prevention added for applications using DOB + guardian phone + class + session.
- Address intake aligned with standard Contacts-style fields (street/street2/city/state/country/zip).
- Admissions pipeline migrated to CRM-style editable stages with visible kanban columns.
- Dashboard redesigned with improved UX, quick-action shortcuts, and backend-connected data cards.
- Dashboard data service upgraded to a single payload API for stats, pipeline health, fee alerts, and notices.
- Dashboard vertical scroll behavior fixed for long-content layouts inside client action containers.
- Enrollment duplicates cleaned from live data and hard prevention added with DB uniqueness + model checks.
- Enrollment creation flow hardened to reuse existing student/session enrollment instead of creating duplicates.
- Admissions kanban avatar rendering fixed with clean no-photo placeholder and stable text separators.

## Technical Notes

- Target version: Odoo 19
- Addon name: `tori_school_management`
- Addons path expected to include `d:/odoo/custom_addons`

## Main Folders

- `models/`: business logic, computed fields, integrations, and stage/location masters
- `views/`: backend form/list/kanban/search/dashboard and stage setup views
- `security/`: groups, ACL, and record rules
- `controllers/`: portal and website HTTP routes
- `data/`: automations, cron, seed data, location data, and stage data
- `report/`: QWeb reports
- `website/`: website templates and page/menu XML records

## Documentation Index

- `INSTALLATION.md`: install, upgrade, and validation steps
- `TROUBLESHOOTING.md`: common runtime, data, and UI issues
- `ERROR_FIX_HISTORY.md`: consolidated migration and stabilization fixes
- `PROJECT_ANALYSIS_REPORT.md`: phase-by-phase implementation report
- `TASK_TRACKER.md`: dated task history with short implementation notes
