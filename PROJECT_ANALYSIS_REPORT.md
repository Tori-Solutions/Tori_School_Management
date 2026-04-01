# Analytical Progress Report: Tori School Management System

## 1. Executive Summary

This report summarizes the implementation status of `tori_school_management` on Odoo 19.

The module is now stabilized across backend, website, and portal layers, and includes:

- Core school operations
- Cross-app ERP integration (Contacts, HR, Accounting)
- Public admission intake and status lookup
- CRM-style admissions pipeline with editable stages
- Bangladesh location master data
- Duplicate-application prevention controls

Status: Completed and stable for pilot use.

## 2. Feature Completion Snapshot

### Completed: Academics and Core Operations

- Sessions, academic years, terms, classes, sections, and subjects
- Enrollments, attendance, assignments, marksheets, fee operations
- Library, transport, timetable, and announcements

### Completed: ERP Integrations

- Contacts (`res.partner`) extensions and relationship links
- HR (`hr.employee`) integration for teaching context
- Accounting (`account.move`) links for fee and scholarship flow

### Completed: Website and Portal Experience

- Public Admission page and Application Status page
- Public admission submit route writing to `tori.student.application`
- Portal breadcrumbs and section tabs for `/my/*` school routes
- Mobile-friendly horizontal tab scrolling in portal navigation

### Completed: Admissions Form Modernization

- Full multi-section website admission form implemented
- Student photo upload retained as box-only control
- Birth certificate attachment upload removed from website flow
- Address section aligned to Contacts-style fields:
  - `street`, `street2`, `city`, `state_id`, `country_id`, `zip`

### Completed: Bangladesh Location Master Data

- Added district/upazila master models:
  - `tori.bd.district`
  - `tori.bd.upazila`
- Loaded reference dataset:
  - `64` districts
  - `494` upazilas/thanas

### Completed: Duplicate Prevention

- Hard duplicate block implemented on application create/update
- Duplicate key:
  - Date of Birth
  - Normalized Guardian Phone
  - Class
  - Session
- Cancelled applications excluded from duplicate lock

### Completed: CRM-Style Admissions Pipeline

- Added stage model `tori.application.stage`
- Kanban grouped by stage records (not static selection)
- Stage columns visible and manageable like CRM
- Stage sequence and fold behavior configurable from Setup
- Default stage sequence verified:
  - 10 Draft
  - 20 Confirmed
  - 30 Enrolled
  - 100 Cancelled (folded)

### Completed: Dashboard UX and Backend Connectivity Upgrade

- Rebuilt dashboard data API as a single backend payload service
- Added quick action buttons wired to module actions
- Added admissions pipeline health summary and richer attendance/fees/notices widgets
- Improved card/list visual hierarchy for faster operational scanning
- Fixed dashboard client-action vertical scrolling behavior for long content

### Completed: Enrollment Data Integrity Controls

- Detected and removed existing duplicate enrollment groups
- Rewired dependent records to canonical enrollment rows during cleanup
- Added DB uniqueness protection for `(student_id, session_id, company_id)`
- Added model-level duplicate validation for clearer user feedback
- Updated application enrollment flow to reuse existing enrollment when applicable

### Completed: Test Asset Seeding

- Added curated dataset for QA and demos:
  - Academic structure
  - Students/parents
  - Applications/enrollments
  - Fees, attendance, assignments
  - Library and transport records

## 3. Technical Stabilization Notes

1. View and parser compatibility was maintained for Odoo 19 (`list`, `kanban card`, strict XML constraints).
2. Admissions schema was expanded while preserving compatibility with existing state-driven automations.
3. Stage/state synchronization logic was added to avoid regressions in dashboards, templates, and automations.
4. Controller flow now enforces required keys and duplicate safety before create.
5. Address data was unified to Contacts-native fields used by `res.partner` records.

## 4. Validation Snapshot

Primary module validation command:

```powershell
python d:/odoo/odoo/odoo-bin -c d:/odoo/odoo.conf -d MUloom -u tori_school_management --stop-after-init
```

Location dataset validation:

```sql
SELECT 'districts' AS item, COUNT(*) FROM tori_bd_district
UNION ALL
SELECT 'upazilas', COUNT(*) FROM tori_bd_upazila;
```

Pipeline sequence validation:

```sql
SELECT sequence, name, code, fold
FROM tori_application_stage
ORDER BY sequence, id;
```

Validated outcomes:

- Module upgrade completed successfully.
- No parser or schema errors in updated website/view/model files.
- District/upazila data loaded with expected counts.
- Stage order and fold settings loaded correctly.
- Duplicate protection path tested and active.
- Dashboard quick actions resolved to valid backend actions.
- Dashboard scroll behavior validated after UI expansion.
- Enrollment duplicate groups reduced to zero and DB uniqueness enforcement verified.

## 5. Current Pilot Readiness

The module is ready for pilot operations with stabilized admissions, portal UX, stage-driven pipeline management, and address/duplicate controls.

Recommended next checks during pilot:

1. Role-based UAT for admin, teacher, student, and parent personas.
2. Browser/device checks for public admission form and portal tabs.
3. Live process validation of application-to-enrollment conversion.
