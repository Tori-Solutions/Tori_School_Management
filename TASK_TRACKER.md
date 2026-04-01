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
