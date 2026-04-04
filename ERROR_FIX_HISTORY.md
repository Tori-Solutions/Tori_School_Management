# Error Fix History (Odoo 19 Stabilization)

This file tracks the major errors fixed while stabilizing `tori_school_management`.

## 1) Invalid field on res.groups: category_id

Error pattern:

- XML parse or validation failure for group definition using `category_id`

Root cause:

- Field usage not valid in the target record/update context for this module state

Fix:

- Removed invalid `category_id` usage from security group XML

Impact:

- Security data loads without group-field validation failure

## 2) base.automation fields no longer valid (state/code)

Error pattern:

- Invalid field errors on `base.automation` for `state` and `code`

Root cause:

- Odoo 19 automation model no longer accepts direct executable code fields in that legacy format

Fix:

- Moved executable logic into dedicated `ir.actions.server`
- Linked automation records to server actions

Impact:

- Automation loads and executes in Odoo 19-compatible pattern

## 3) ir.cron invalid field: numbercall

Error pattern:

- Invalid field `numbercall` on cron records

Root cause:

- Field removed or unsupported in target Odoo version

Fix:

- Removed `numbercall` from cron XML records

Impact:

- Scheduled actions load successfully

## 4) Backend view type migration: tree -> list

Error pattern:

- View architecture/type validation errors for `tree`

Root cause:

- Odoo 19 uses `list` for list views and view mode definitions

Fix:

- Replaced `<tree>` with `<list>` in view XML files
- Updated `view_mode` entries from `tree` to `list`

Impact:

- List views and actions open correctly

## 5) Search view group-by validation issue

Error pattern:

- Invalid search view structure around grouped filters

Root cause:

- Legacy grouping syntax incompatible with stricter Odoo 19 validation

Fix:

- Updated search view to Odoo 19 style:
  - `<group name="group_by"> ... </group>`

Impact:

- Search/group-by works without parse errors

## 6) Forbidden OWL directives in standard backend form view

Error pattern:

- Backend view rejected directives such as `t-esc`

Root cause:

- OWL templating directives are not allowed in regular backend form arch definitions

Fix:

- Removed direct `t-esc` usage from dashboard form
- Replaced with model computed fields rendered via standard `<field>` tags

Impact:

- Dashboard form renders through standard Odoo arch parser

## 7) Form label validation error

Error pattern:

- `<label>` usage validation error when missing `for`

Root cause:

- Stricter form architecture validation in Odoo 19

Fix:

- Replaced invalid labels with `<div class="o_form_label">...` where appropriate

Impact:

- Form validation passes

## 8) App launcher visibility issues

Symptoms:

- Module installed but app tile not visible for admin/internal users

Root cause:

- Combination of menu/action/group setup and launcher metadata needing alignment

Fix:

- Loosened root menu access to internal users where required
- Set root menu action to dashboard action
- Added admin implication (`base.group_system` -> education admin)
- Added app icon and linked `web_icon` on root menu

Impact:

- Launcher visibility works with expected user roles

## 9) Owl lifecycle error: Missing 'card' template

Error pattern:

- `UncaughtPromiseError > OwlError`
- Cause: `Missing 'card' template.` in kanban parser

Root cause:

- Legacy kanban template name `kanban-box` remained in module views

Fix:

- Updated kanban templates to Odoo 19 format:
  - `<t t-name="card">` in Admissions and Assignments kanban views

Impact:

- Kanban views render correctly without Owl parser crash

## 10) RPC compute instability around dashboard counters

Error pattern:

- RPC/Owl failures from session dashboard metric compute path

Root cause:

- Unsafe compute access path under UI contexts and strict ACL boundaries

Fix:

- Hardened compute method for dashboard counters
- Removed problematic broad elevation pattern in compute logic
- Added guarded access handling with safe zero fallbacks

Impact:

- Dashboard counters compute robustly under restricted user contexts

## 11) Dashboard validation error (Missing 'name' field) upon OWL migration

Error pattern:

- `Missing required value for the field 'Name' (name). Model 'School Session' (tori.session)`

Root cause:

- Converting a generic `ir.actions.act_window` to an `ir.actions.client` for an OWL Javascript dashboard failed due to database caching. The UI assumed the user was trying to create a newly scheduled session instead of launching a client tag.

Fix:

- Overrode the action ID to `action_tori_dashboard_client`, clearing the Odoo Registry cache completely.
- Bound the root menu squarely to the clean client action.

Impact:

- Custom Javascript OWL Dashboard loads without attempting to build backend records.

## 12) Forbidden XML directives inside Form Archs

Error pattern:

- `Forbidden owl directive used in arch (t-if).` inside `<form>` elements.

Root cause:

- Utilizing raw QWeb variables (`<t t-if="X">`) inside pure backend forms during the UI/UX polish phase, throwing the stricter Odoo 19 XML parser into fatal traces.

Fix:

- Migrated UI conditional rendering into native backend attributes: `<field invisible="not X"/>`
- Scanned and cleared all forms of legacy templating loops to conform to `<list>`, `<form>`, and `<calendar>`.

Impact:

- Form and View XML imports bypass the backend parser natively without Server-Side 500 crashes.

## Validation summary used during fixes

Core validation command repeatedly used:

```powershell
python odoo/odoo-bin -c odoo.conf -u tori_school_management --stop-after-init
```

Expected result:

- Exit code 0
- No XML parse/model field errors
- No Owl runtime errors when opening related views after browser hard refresh

## 13) Website app discoverability gap for public education pages

Error pattern:

- Public routes existed but were not properly discoverable from Website navigation.

Root cause:

- Missing/partial website menu and page record coverage.

Fix:

- Added website page and menu records for admission-related public routes.
- Verified record creation through module upgrade and database checks.

Impact:

- Website users can access Admission and Application Status through website navigation, not just direct URLs.

## 14) Portal navigation inconsistency across /my pages

Error pattern:

- Portal pages rendered but lacked unified section-level navigation and breadcrumb continuity.

Root cause:

- No custom inheritance layer for `portal.portal_breadcrumbs` and `portal.portal_layout` for school-specific routes.

Fix:

- Added `website/templates/portal_navigation.xml`.
- Extended portal breadcrumbs for school pages.

## 22) Fresh install ParseError from menu action ordering

Error pattern:

- Fresh install failed with `External ID not found in the system: tori_school_management.action_lesson_plan`
- Parse error in `views/menus.xml` when loading menu items referencing actions not yet loaded.

Root cause:

- `views/menus.xml` loaded before new view files that define the corresponding `ir.actions.act_window` records.

Fix:

- Kept top-level menu tree in `views/menus.xml` and loaded it early.
- Moved action-bound feature menuitems into new `views/feature_menus.xml` loaded after view/action files.

Impact:

- Fresh install and upgrade both load cleanly.

## 23) Odoo 19 search view parser incompatibility for `<group>`

Error pattern:

- `Invalid view ... search definition`
- RNG errors for `expand` and `string` attributes on `<group>` inside `<search>`.

Root cause:

- Legacy search group syntax was used (`expand="0"`, `string="Group By"`) which is invalid for Odoo 19 search views.

Fix:

- Updated all search views to use a bare `<group>` with nested group-by filters.

Impact:

- Search views import cleanly in Odoo 19.

## 24) Invalid fee slip state sync value

Error pattern:

- Fee slip sync attempted to write `state='unpaid'`, which is not a valid value in `tori.fee.slip` state selection.

Root cause:

- Incorrect fallback mapping in account move payment-state sync logic.

Fix:

- Changed fallback to `state='sent'` when posted invoice returns to `not_paid`.

Impact:

- Payment-state sync remains valid and no selection mismatch can occur.
- Added portal section navigation tabs linked to `/my/*` routes.

Impact:

- Student/parent portal navigation is consistent and faster across dashboard, timetable, attendance, assignments, grades, library, transport, children, and fees pages.

## 15) Mobile portal navigation polish and XML regression fix

Error pattern:

- Initial mobile nav tweak introduced an XML closing-tag mismatch in `portal_navigation.xml` during update.

Root cause:

- Structural tag mismatch inside inherited template block while refactoring nav layout.

Fix:

- Corrected XML structure and revalidated module load.
- Added responsive portal nav styles in `static/src/css/dashboard.css`.
- Removed incompatible CSS properties flagged by diagnostics to keep frontend checks clean.

Impact:

- Portal navigation now behaves correctly on mobile and desktop, and module upgrades complete without XML parser errors.

## 16) Education app icon style mismatch in launcher

Error pattern:

- Education app tile looked visually inconsistent compared to standard Odoo app icons.

Root cause:

- Initial icon variant used a solid square background and did not blend with launcher card styling.

Fix:

- Replaced icon asset with transparent Odoo-style composition in `static/description/icon.png`.
- Kept root menu `web_icon` mapping to module icon path.

Impact:

- Education tile now appears consistent with other Odoo apps in launcher grid.

## 17) Test asset import failure due to strict XML schema

Error pattern:

- Module update failed with RelaxNG XML validation errors while loading test assets.

Root cause:

- Seed XML structure and content required strict Odoo parser compliance.

Fix:

- Rebuilt `data/test_assets.xml` in schema-compliant format.

---

## 18) KeyError: 'base.automation' on fresh install

Error pattern:

- `KeyError: 'base.automation'` during fresh install when loading `data/mail_templates.xml`.

Root cause:

- `base_automation` module was not listed under `depends` in `__manifest__.py`. The `ir.actions.server`
  records in `mail_templates.xml` reference the `base.automation` model, which requires the module to be loaded first.

Fix:

- Added `'base_automation'` to the `depends` list in `__manifest__.py`.

Impact:

- Fresh install completes without `KeyError`. Module now declares its dependency correctly.

---

## 19) ImportError: cannot import name 'SavepointCase' from 'odoo.tests'

Error pattern:

- Test loader crashed: `ImportError: cannot import name 'SavepointCase' from 'odoo.tests'`
  and subsequently from `odoo.tests.common`.

Root cause:

- Odoo 19 removed `SavepointCase` entirely. Only `TransactionCase` and `SingleTransactionCase` remain.

Fix:

- Changed test base class from `SavepointCase` to `TransactionCase`.
- Updated imports: `from odoo.tests import tagged` + `from odoo.tests.common import TransactionCase`.

Impact:

- Test module loads and test methods execute correctly.

---

## 20) Invalid field 'groups_id' in 'res.users'

Error pattern:

- `ValueError: Invalid field 'groups_id' in 'res.users'` during test `setUpClass`.

Root cause:

- Odoo 19 renamed the user groups many2many field from `groups_id` to `group_ids`.

Fix:

- Updated all `res.users` create calls in tests to use `'group_ids'` instead of `'groups_id'`.

Impact:

- Test users are created with correct group assignments.

---

## 21) NotNullViolation: account_return_reminder_day on test company create

Error pattern:

- `psycopg2.errors.NotNullViolation: null value in column "account_return_reminder_day" of relation "res_company"`
  during `setUpClass` when creating test companies with bare `Company.create({'name': ...})`.

Root cause:

- `account_reports` (enterprise) adds `account_return_reminder_day` as a `required=True, default=7`
  `Integer` field on `res.company`. When the module is installed in the DB but not in the active
  registry of the current test run, the ORM Python default is not applied and the DB NOT NULL
  constraint fires.

Fix:

- Detect columns that are `NOT NULL` without a DB-level default via `information_schema.columns`.
- Temporarily set a `DEFAULT` on those columns via `ALTER TABLE` before creating test companies.
- Remove the temporary defaults immediately after creation to leave schema state clean.

Impact:

- Test companies create successfully regardless of which enterprise modules are installed in the DB.
- Added HTML field typing where needed and validated against Odoo parser before upgrade.

Impact:

- Demo/test records now load successfully and can be reused for QA.

## 18) Public admission form coverage gap vs required intake process

Error pattern:

- Legacy public admission flow captured minimal fields only and did not match full school intake requirements.

Root cause:

- Website template and submit controller were still mapped to lightweight submission paths.

Fix:

- Expanded admission UI into multi-section intake form.
- Updated `/admission/submit` controller mapping for full application payload.
- Updated backend application form/list for complete field coverage.

Impact:

- Public and backend admissions now operate on a consistent full-profile application model.

## 19) Duplicate application creation risk

Error pattern:

- Users could submit multiple active applications for the same student context.

Root cause:

- No hard guard on duplicate key dimensions at create/update time.

Fix:

- Added normalized guardian phone derivation and indexed duplicate key checks.
- Enforced hard duplicate block using DOB + guardian phone + class + session.
- Added user-facing duplicate error route feedback in admission page.

Impact:

- Duplicate active applications are blocked deterministically.

## 20) Address flow divergence from standard Odoo Contacts

Error pattern:

- Admission address capture used custom fields that diverged from Contacts app address format.

Root cause:

- Public and backend forms were not aligned to `res.partner` address conventions.

Fix:

- Replaced address block with Contacts-style fields (`street`, `street2`, `city`, `state_id`, `country_id`, `zip`).
- Synced enrollment partner creation to these standard fields.

Impact:

- Address data now aligns cleanly with Contacts app and downstream ERP usage.

## 21) Admissions pipeline not fully visible/editable like CRM

Error pattern:

- Pipeline columns were incomplete and lacked stage management behavior.

Root cause:

- Pipeline relied on static `state` selection grouping rather than stage records.

Fix:

- Added `tori.application.stage` model with sequence, code, fold, and active flags.
- Migrated kanban grouping to `stage_id` with group create/edit/delete enabled.
- Added setup views/menu for stage administration.
- Added state-stage synchronization and data backfill.

## 22) Dashboard UX/data mismatch and disconnected quick navigation

Error pattern:

- Dashboard metrics rendered, but navigation and data sourcing were not optimized for reliability and operational flow.

Root cause:

- Frontend fetched multiple independent datasets with partial error handling and no unified payload.
- Quick actions were limited and not consistently mapped to backend actions.

Fix:

- Introduced backend payload method (`get_dashboard_payload`) for stats + operational widgets.
- Refactored dashboard JS to consume one payload and use explicit action-service routing.
- Redesigned dashboard layout for clearer decision flow (quick actions, pipeline health, attendance, fee alerts, notices).

Impact:

- Dashboard is more responsive, easier to scan, and consistently connected to target module actions.

## 23) Dashboard page could not scroll in client action context

Error pattern:

- Users could not scroll vertically after dashboard expansion.

Root cause:

- Client-action container required explicit scroll behavior for the custom dashboard root.

Fix:

- Added dedicated dashboard scroll class with `height: 100%`, `overflow-y: auto`, and `overflow-x: hidden`.

Impact:

- Full dashboard content is now reachable regardless of viewport height.

## 24) Duplicate enrollment records in live data and repeated creation path

Error pattern:

- Same student/session/company combinations appeared multiple times in enrollment list.

Root cause:

- No enforced DB uniqueness on enrollment key.
- Enrollment creation path from applications always created new rows.

Fix:

- Cleaned existing duplicates by merging to canonical rows and rewiring dependent references.
- Added DB uniqueness constraint on `(student_id, session_id, company_id)`.
- Added model-level duplicate check for user-facing validation.
- Updated application enrollment logic to reuse existing enrollment when found.

Impact:

- Existing duplicate rows removed and future duplicates blocked at both application and database levels.

Impact:

- Admissions pipeline now behaves like CRM with visible/editable stage columns and controlled sequence.

## 22) Student photo upload UX cleanup

Error pattern:

- Upload area displayed extra labels and birth-certificate attachment control not required by final UX.

Root cause:

- Earlier intake form retained non-final attachment block.

Fix:

- Removed public birth-certificate attachment upload control and related submit handling.
- Kept single top-right student photo upload box with no visible label text.
- Aligned backend form section accordingly.

Impact:

- Admission upload UX is simplified and consistent with requested design.
