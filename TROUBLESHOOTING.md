# Troubleshooting

## App does not appear in launcher

Checks:

- User is internal (`base.group_user`) or system admin (`base.group_system`)
- Root menu has a valid action and `web_icon`
- Security group implication from system admin to education admin is loaded

Actions:

1. Upgrade module.
2. Hard refresh browser (`Ctrl+F5`).
3. Re-login if menu cache persists.

## ParseError during module update

Common causes in Odoo 19 migration:

- Using `<tree>` instead of `<list>`
- Invalid/removed fields for target model
- Non-compliant XML structure in data files

Fix strategy:

1. Validate changed XML files with Odoo parser expectations.
2. Replace deprecated tags/fields.
3. Re-run module upgrade.

## OwlError in backend kanban views

Symptoms:

- `UncaughtPromiseError > OwlError`
- `Missing 'card' template.`

Cause:

- Kanban template is not using `<t t-name="card">`.

Fix:

1. Update affected kanban template names to `card`.
2. Upgrade module.
3. Refresh browser assets.

## Admissions pipeline columns missing or not editable

Symptoms:

- All stage columns are not visible.
- Cannot manage stage order/fold behavior like CRM.

Checks:

- `tori.application.stage` records exist.
- Admissions kanban is grouped by `stage_id`.
- Stage setup action/menu is available for admins.

Fix strategy:

1. Verify `data/application_stage_data.xml` loaded.
2. Verify `views/application_stage_views.xml` is in manifest.
3. Re-run module upgrade.

## Duplicate application blocked unexpectedly

Symptoms:

- Public submission returns duplicate warning.

Cause:

- Hard duplicate key matched an existing active application:
  - Date of birth
  - Guardian phone (normalized)
  - Class
  - Session

Fix strategy:

1. Confirm guardian phone input and formatting.
2. Check existing application by reference from duplicate message.
3. Cancel stale duplicate if business process allows.

## Admission form submits but no application appears

Symptoms:

- Public form posts, but no `tori.student.application` record is created.

Checks:

- Route `/admission/submit` exists in `controllers/portal.py`.
- Form action in `website/templates/admission_form.xml` points to `/admission/submit`.
- Required fields are present:
  - First name
  - Date of birth
  - Guardian phone
  - Class
  - Session

Fix strategy:

1. Validate payload and required keys.
2. Re-upgrade module.
3. Inspect server logs for validation errors.

## Bangladesh district/thana dropdowns are empty

Symptoms:

- District/upazila selectors show no options (where used).

Checks:

- Data file `data/bd_location_data.xml` is loaded.
- Model ACLs allow read access for target user groups.

Fix strategy:

1. Upgrade module.
2. Verify counts in DB (`tori_bd_district`, `tori_bd_upazila`).
3. Refresh browser cache.

## State/Division selection does not filter by country

Symptoms:

- State list includes records from other countries.

Checks:

- State dropdown options include `data-country-id` in website template.
- JS filter binding runs after page load.

Fix strategy:

1. Ensure template script is loaded and error-free.
2. Hard refresh browser (`Ctrl+F5`).
3. Re-upgrade if template changes were recently made.

## Student photo upload issues

Symptoms:

- Upload rejected or no image saved.

Checks:

- File is image type and not above 2MB.
- Form uses `enctype="multipart/form-data"`.
- Controller receives `student_photo` and writes binary field.

Fix strategy:

1. Use smaller image file.
2. Retry and check server logs.
3. Confirm `student_photo` field exists in model/view.

## Website menu item not opening expected page

Symptoms:

- Website menu opens `#` or wrong path.

Checks:

- `website/website_pages.xml` has expected URL and parent hierarchy.
- `website.menu` records were refreshed after upgrade.

Fix strategy:

1. Correct URL/parent in website XML.
2. Upgrade module.
3. Clear browser cache.

## Portal navigation missing or not mobile friendly

Symptoms:

- `/my/*` pages render without school section tabs, or tabs overflow on small screens.

Checks:

- `website/templates/portal_navigation.xml` is loaded.
- Frontend CSS includes responsive nav rules in `static/src/css/dashboard.css`.

Fix strategy:

1. Validate template inheritance targets.
2. Rebuild/refresh frontend assets.
3. Re-run module upgrade.

## Dashboard cannot scroll

Symptoms:

- Dashboard loads but lower panels cannot be reached.

Checks:

- Dashboard root includes scroll class from frontend template.
- CSS includes vertical scrolling rule for dashboard container.

Fix strategy:

1. Re-upgrade module after dashboard XML/CSS updates.
2. Hard refresh browser (`Ctrl+F5`).
3. Confirm no custom browser extension/CSS is overriding overflow.

## Dashboard quick action opens wrong screen or fails

Symptoms:

- Quick action button does nothing or opens unrelated view.

Checks:

- Action IDs exist in `ir_model_data` for referenced module actions.
- Dashboard JS uses `action` service and valid fallback actions.

Fix strategy:

1. Verify action records are loaded from module views.
2. Re-upgrade module.
3. Re-test after hard refresh.

## Duplicate enrollment blocked or enrollment not created

Symptoms:

- Enrollment creation raises duplicate constraint error.

Cause:

- Student is already enrolled in the same session and company.

Fix strategy:

1. Open existing enrollment and update it instead of creating a new one.
2. Confirm session/company selection is correct.
3. Use application enroll action (which now reuses existing enrollment when present).

## Existing duplicate enrollments found in old data

Symptoms:

- Enrollment list shows repeated rows for same student/session/company.

Fix strategy:

1. Run controlled deduplication SQL with FK/M2M rewiring.
2. Verify duplicate groups query returns no rows.
3. Ensure DB uniqueness constraint exists on enrollment key.
