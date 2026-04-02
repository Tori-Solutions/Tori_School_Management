# Tori School Management Installation Guide

This guide covers full installation, upgrade, and backend architecture for:

- Module: tori_school_management
- Odoo version: 19
- Typical workspace root: D:/odoo

## 1) What You Need Before Installing

### 1.1 Platform prerequisites

- Odoo 19 source available locally
- PostgreSQL running and reachable
- Python virtual environment for Odoo runtime
- Custom addons directory available in Odoo config

### 1.2 Required module dependencies (auto-installed by Odoo if available)

From module manifest:

- base
- mail
- portal
- website
- account
- hr
- web
- base_automation

### 1.3 Python dependencies

Install Odoo requirements first:

PowerShell:
python D:/odoo/odoo/odoo-bin --version
pip install -r D:/odoo/odoo/requirements.txt

Optional but recommended:

- pdfminer.six (better PDF attachment indexing)
- phonenumbers (phone validation support)

PowerShell:
pip install pdfminer.six phonenumbers

## 2) Database and Odoo Configuration

### 2.1 Ensure addons path includes custom addons

In odoo.conf, addons_path must include:

- D:/odoo/custom_addons
- D:/odoo/odoo/addons
- D:/odoo/enterprise

### 2.2 Verify database credentials

Your odoo.conf db_host, db_port, db_user, db_password must match PostgreSQL.

Quick test (PowerShell):

$env:PGPASSWORD='your_db_password'; psql -h localhost -p 5432 -U odoo -d MUloom -c "select 1;"

## 3) Install the Module

You can install either from UI or CLI.

### 3.1 Install from Apps UI

1. Start Odoo server.
2. Open Apps.
3. Search for Education Management System.
4. Click Install.

### 3.2 Install from CLI (recommended for reproducible setup)

PowerShell:
python D:/odoo/odoo/odoo-bin -c D:/odoo/odoo.conf -d MUloom -i tori_school_management --stop-after-init

Expected result:

- Module loads successfully
- No ParseError / OwlError / invalid field errors

## 4) Upgrade Workflow (for Any Code/Data Change)

Run this after model, view, security, data, controller, JS, or CSS changes:

PowerShell:
python D:/odoo/odoo/odoo-bin -c D:/odoo/odoo.conf -d MUloom -u tori_school_management --stop-after-init

If frontend changed, perform hard refresh in browser:

- Ctrl + F5

## 5) What Loads During Installation

The module loads in this order (important for stability):

1. Security:
   - security/security.xml (groups: teacher defined before admin; admin implies teacher)
   - security/ir.model.access.csv (includes student ACLs for portal-relevant models; wizards restricted to admin)
   - security/record_rules.xml (multi-company isolation + student-scoped rules)
2. Data:
   - mail templates + automations + crons
   - Bangladesh location master data
   - application stages
   - stage backfill
3. Backend views/actions/menus
4. Reports
5. Website templates/pages
6. Web assets (dashboard JS/XML/CSS and scanner JS)
7. Demo data (test_assets.xml — only on databases created with demo)

## 6) First-Time Functional Setup Checklist

After install, verify these in UI:

1. Education app visible in launcher.
2. Dashboard opens.
3. Admissions > Applications shows CRM-like stages.
4. Setup > Application Stages exists and is editable.
5. Website routes are reachable:
   - /admission
   - /edu/application/status
6. Portal pages available for permitted users under /my/* routes.

### 6.1 User roles

Main groups:

- Education Administrator
- Education Teacher
- Education Student

Note: System administrators are auto-implied into Education Administrator.

## 7) Backend Architecture: How It Works

## 7.1 Main backend domains

- Academic structure:
  - Sessions, Academic Years, Terms
  - Classes, Sections, Subjects, Rooms
- Admissions:
  - Enquiries
  - Student Applications
  - Stage-driven pipeline
- Student lifecycle:
  - Enrollments
  - Attendance
  - Assignments/Submissions
  - Marksheets/Results
- Finance:
  - Fee Structures/Elements/Slips
  - Scholarship handling
  - Accounting move integration
- Operations:
  - Timetable
  - Library
  - Transport

## 7.2 Admissions to Enrollment flow

1. Public form submits to /admission/submit.
2. Controller writes tori.student.application.
3. Duplicate block enforced on:
   - date_of_birth
   - guardian_phone_normalized
   - class_id
   - session_id
4. Staff confirms/enrolls application.
5. On enroll action:
   - student partner is created/linked
   - parent partner is created/linked
   - existing enrollment for same student/session/company is reused when present
   - new enrollment is created only when needed
   - fee structure is attached
   - fee slips are generated only if none exist

## 7.3 Enrollment duplicate prevention (critical)

Protection is implemented at two layers:

1. ORM constraint (model-level validation)
2. Database unique constraint on:
   - (student_id, session_id, company_id)

This prevents duplicate enrollment rows in both UI and direct DB write scenarios.

## 7.4 Pipeline engine

- Pipeline uses stage model tori.application.stage, not fixed-only state grouping.
- Stages are sequence-driven and fold-aware.
- Stage and legacy state stay synchronized for compatibility with automations/reports.

## 7.5 Security model

- ACL matrix defined in security/ir.model.access.csv.
- Record rules enforce scoped access such as:
  - teachers: own classes/records
  - students: own enrollments/submissions
  - parents/portal: granted enrollments only

## 7.6 Automations and schedulers

From data/mail_templates.xml:

- Application state mail automation
- Scholarship approved vendor bill automation
- Fee overdue cron
- Recurring fee generation cron

## 7.7 Dashboard backend integration

Dashboard client action reads a single backend payload from tori.dashboard and displays:

- KPI cards (students, faculty, enrollments, pending applications, overdue fees)
- pipeline health
- attendance summary
- fee alerts
- notices

Quick-action buttons route to valid backend module actions.

## 8) Validation Commands (Recommended)

### 8.1 Upgrade validation

PowerShell:
python D:/odoo/odoo/odoo-bin -c D:/odoo/odoo.conf -d MUloom -u tori_school_management --stop-after-init

### 8.4 Run test suite

PowerShell:
python D:/odoo/odoo/odoo-bin -c D:/odoo/odoo.conf -d <testdb> -u tori_school_management --test-enable --test-tags tori_school_management --stop-after-init --no-http

Expected: `0 failed, 0 error(s) of 4 tests`

### 8.3 Bangladesh location data validation

PowerShell:
$env:PGPASSWORD='123123'; psql -h localhost -p 5432 -U odoo -d MUloom -c "SELECT 'districts' AS item, COUNT(*) FROM tori_bd_district UNION ALL SELECT 'upazilas', COUNT(*) FROM tori_bd_upazila;"

Expected:

- districts = 64
- upazilas = 494

### 8.5 Stage sequence validation

PowerShell:
$env:PGPASSWORD='123123'; psql -h localhost -p 5432 -U odoo -d MUloom -c "SELECT sequence, name, code, fold FROM tori_application_stage ORDER BY sequence, id;"

### 8.6 Enrollment duplicate validation

No duplicate groups should exist:

PowerShell:
$env:PGPASSWORD='123123'; psql -h localhost -p 5432 -U odoo -d MUloom -c "SELECT student_id, session_id, company_id, COUNT(*) AS cnt FROM tori_enrollment GROUP BY student_id, session_id, company_id HAVING COUNT(*) > 1;"

Constraint should exist:

PowerShell:
$env:PGPASSWORD='123123'; psql -h localhost -p 5432 -U odoo -d MUloom -c "SELECT conname, pg_get_constraintdef(oid) FROM pg_constraint WHERE conrelid='tori_enrollment'::regclass AND contype IN ('u','p') ORDER BY conname;"

## 9) Common Operational Commands

Start Odoo server:

PowerShell:
python D:/odoo/odoo/odoo-bin -c D:/odoo/odoo.conf -d MUloom

Update only this module:

PowerShell:
python D:/odoo/odoo/odoo-bin -c D:/odoo/odoo.conf -d MUloom -u tori_school_management --stop-after-init

Save current config via CLI:

PowerShell:
python D:/odoo/odoo/odoo-bin -c D:/odoo/odoo.conf --save

## 10) Production Notes

- Disable test seed data in production if not required.
- Use backup before every module upgrade.
- Keep role assignment strict (admin vs teacher vs student vs portal).
- Monitor cron jobs and mail queue after go-live.
- Re-run validation commands after major schema or workflow changes.
