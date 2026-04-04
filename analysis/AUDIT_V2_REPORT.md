# Audit V2 Report - tori_school_management

Date: 2026-04-04  
Database audited: `MULOOM`

## A) Required System Info (collected before analysis)

1. CPU / RAM / Disk:
- CPU logical cores: 8
- RAM total: ~7.73 GB
- RAM available at capture: ~521 MB
- Disks (local):
  - C: 30.43 GB free / 158.35 GB total
  - D: 37.03 GB free / 64.00 GB total
  - E: 39.90 GB free / 81.57 GB total
  - F: 91.05 GB free / 172.03 GB total

2. PostgreSQL version:
- 18.1

3. wkhtmltopdf version:
- 0.12.6 (with patched qt)

4. Odoo worker setup (`odoo.conf`):
- `workers`: not explicitly set (defaults to 0 in Odoo, threaded/single-process mode)
- `max_cron_threads = 2`
- `db_maxconn = 64`
- `limit_time_real = 1200`
- `proxy_mode = False`

5. Database size:
- `MULOOM`: 75 MB

6. Number of `tori_*` tables:
- 44

7. Row counts (core tables):
- `tori_enrollment`: 0
- `tori_student_attendance`: 0
- `tori_fee_slip`: 0

---

## B) Phase-by-Phase Findings

## Phase 1 - Concurrency and Locking

### Findings
- Attendance duplicate protection exists at DB level via unique constraint on `(enrollment_id, date, timetable_slot_id)`.
- Attendance scan endpoint does a read-then-create pattern and relies on uniqueness for race safety.
- Public admission rate limiting uses in-process memory, explicitly documented as not suitable for multi-worker/distributed deployment.
- Fee crons are configured daily, reducing high-frequency overlap risk but with no explicit idempotency lock token.

### Evidence
- `models/attendance.py`: unique constraint declaration.
- `controllers/portal.py`: `_is_rate_limited` with module-level dict+lock and comment indicating Redis/PostgreSQL should replace in multi-worker.
- `data/mail_templates.xml`: `cron_tori_fee_overdue`, `cron_tori_fee_recurring`, both daily.

### Risk
- Moderate under scaled deployment: in-memory limiter bypassed across workers/hosts.
- Low-to-moderate for attendance race UX: duplicate attempts can still produce integrity conflicts under simultaneous scans.

### Recommendation
- Replace in-process limiter with Redis/PostgreSQL-backed limiter.
- Wrap attendance create in explicit `try/except` for duplicate key and return deterministic success message.
- Add advisory lock or functional idempotency key for recurring fee generation in high-scale environments.

Status: **Partially hardened**

---

## Phase 2 - DB Performance and Query Health

### Findings
- Attendance lookup plan uses the composite unique index efficiently.
- No lock waits observed at sample time.
- `tori_fee_slip` shows more sequential scans than index scans in stats baseline (small dataset, but pattern worth watching).
- FK index audit reports many potential missing indexes across `tori_*` tables; however, many are low-impact relational columns (`create_uid`, `write_uid`, some company fields) and should be triaged, not blindly added.
- No `tori_*` table is missing a primary key.

### Evidence
- `EXPLAIN (ANALYZE, BUFFERS)` on attendance lookup uses `tori_student_attendance_uniq_*` index.
- `pg_stat_activity`/`pg_locks`: no contention at capture.
- `pg_stat_user_tables`: `tori_fee_slip` has high `seq_scan` relative to `idx_scan`.
- PK audit query: zero tables without PK.

### Risk
- Current runtime risk: Low (very low data volume).
- Future risk: Medium if high-volume production data grows without targeted indexing strategy.

### Recommendation
- Add only workload-backed indexes first:
  - `tori_fee_slip(enrollment_id, state, due_date)`
  - `tori_submission(enrollment_id, assignment_id)`
  - `tori_marksheet(enrollment_id, term_id)`
- Re-run EXPLAIN with real production cardinalities before adding broad FK indexes.
- Enable periodic slow-query review using PostgreSQL logs (`log_min_duration_statement`).

Status: **Needs production-volume revalidation**

---

## Phase 3 - Security, Access, and IDOR

### Findings
- Positive: Portal/student record rules exist for marksheets, book issues, submissions, attendance, enrollments, fee slips.
- Risk: `/my/announcements` uses `sudo().search([])` and can leak all announcements beyond intended tenant/role scope.
- Risk: Assignment submit route validates `enrollment_id` ownership but does not verify `assignment_id` belongs to that enrollment's class/session.
- Risk: Public application status endpoint can be brute-forced (reference + phone) and has no explicit rate limiting.
- Data lifecycle: `invoice_id` and `vendor_bill_id` Many2one fields do not specify `ondelete='restrict'`, reducing explicit referential intent.

### Evidence
- `security/record_rules.xml`: portal/student rules present (including D10 additions).
- `controllers/portal.py`: `/my/announcements` route performs `sudo().search([])`.
- `controllers/portal.py`: `/my/assignments/submit/<assignment_id>/<enrollment_id>` checks only enrollment ownership.
- `controllers/portal.py`: `/edu/application/status` has no limiter.
- `models/fee.py`: `invoice_id = fields.Many2one('account.move')`.
- `models/scholarship.py`: `vendor_bill_id = fields.Many2one('account.move')`.

### Risk
- Security risk: Medium.
- Data integrity risk: Medium.

### Recommendation
- Remove `sudo()` on announcements route or constrain by strict domain and company context.
- Validate assignment ownership: assignment class/session must match enrollment context.
- Add route-level rate limiting and attempt throttling for application status lookup.
- Set explicit `ondelete='restrict'` on accounting links and add tested unlink behavior.

Status: **Action required before strict go-live**

---

## Phase 4 - Mobile UX and Accessibility

### Findings
- Static review only; no Lighthouse/WebPageTest/browser-run evidence collected in this run.
- Frontend assets include dedicated portal stylesheet; templates are present.

### Risk
- Unknown real-world mobile/a11y quality due to missing objective metrics.

### Recommendation
- Execute measured audit:
  - Lighthouse mobile performance/accessibility/best-practices/SEO
  - Core Web Vitals from representative pages
  - Manual keyboard and screen-reader checks

Status: **Not executed (evidence gap)**

---

## Phase 5 - Disaster Recovery and Operations

### Findings
- No backup/restore drill evidence collected from running environment.
- Existing project docs already list backup policy as operational pending item.

### Risk
- Operational continuity risk: High if backups/drills are not enforced outside code.

### Recommendation
- Define and validate:
  - RPO/RTO targets
  - Automated DB backup schedule + retention
  - Restore drill runbook and monthly restore tests
  - Attachment/file-store backup consistency

Status: **Not validated (critical operational gap)**

---

## Phase 6 - Domain Compliance (BD school ops)

### Findings
- BD district/upazila seed data file loads as regular data (not marked noupdate), so later upgrades can overwrite local admin edits.
- Admission model uses `birth_certificate_attachment_id` linked to `ir.attachment`; no custom access-control wrapper noted in this review.
- Good: guardian phone normalization and duplicate-key checks are implemented in admissions flow.

### Risk
- Master data governance risk: Medium.
- Attachment privacy risk: Medium (depends on global attachment rules and deployment hardening).

### Recommendation
- Protect location master data by loading under noupdate where appropriate and provide controlled extension mechanism.
- Validate attachment ACL and ownership policies for sensitive student documents.

Status: **Partially compliant, requires policy hardening**

---

## Phase 7 - Operational Readiness and Observability

### Findings
- Logging exists in selected areas (hooks, migration, admission rate-limit warnings), but business-critical lifecycle logging is limited.
- System memory headroom is low at capture (~521 MB available).
- `workers` not set in `odoo.conf`; with production concurrency this may become a bottleneck.

### Risk
- Reliability risk: Medium.
- Throughput risk under load: Medium-to-high (depending on user concurrency).

### Recommendation
- Add structured logs for fee generation, overdue processing, attendance scan exceptions, and portal submission anomalies.
- Size workers based on CPU/RAM and test (`workers`, `limit_memory_soft/hard`, `db_maxconn`).
- Introduce alerting for cron failures and error spikes.

Status: **Needs operational tuning**

---

## C) Risk Register (Prioritized)

| Severity | ID | Risk | Impact | Likelihood | Owner | Mitigation |
|---|---|---|---|---|---|---|
| High | R1 | DR/restore process unvalidated | Prolonged outage/data loss | Medium | Ops | Backup policy + regular restore drills |
| High | R2 | App status endpoint brute-force surface | PII leakage via enumeration | Medium | Dev/Sec | Add limiter + attempt lockout + audit logs |
| Medium | R3 | `sudo().search([])` announcements | Cross-company/role information leak | Medium | Dev | Remove sudo or restrict domain/company |
| Medium | R4 | Assignment submit cross-context integrity gap | Invalid submissions, data corruption | Medium | Dev | Validate assignment-class/session to enrollment |
| Medium | R5 | In-memory rate limiter only | Spam protection bypass in scaled setup | High (if scaled) | Dev/Ops | Redis/DB-backed distributed limiter |
| Medium | R6 | Explicit accounting link ondelete rules absent | Data lifecycle surprises | Low-Med | Dev | Set `ondelete='restrict'` + tests |
| Medium | R7 | Low memory headroom + workers unset | Latency/instability under load | Medium | Ops | Capacity tuning and load test |

---

## D) Final GO / NO-GO Verdict

Verdict: **NO-GO for strict production cutover** (until critical gaps are closed).

Reasoning:
- Core module load and base behavior are stable.
- But security/operational evidence is incomplete for production assurance:
  - Unvalidated DR/restore controls.
  - Security hardening gaps in selected portal/public flows.
  - No objective mobile/performance evidence from production-like load.

Conditional GO path:
- Close R1-R4 at minimum, then execute focused re-audit and smoke test cycle.

---

## E) Sprint 6 Backlog (Actionable)

1. Security hardening
- Enforce assignment-context validation on submit route.
- Remove broad `sudo()` from announcements route and apply scoped domain.
- Add public status endpoint throttling and abuse telemetry.

2. Data lifecycle integrity
- Add `ondelete='restrict'` for accounting link fields (`invoice_id`, `vendor_bill_id`) and tests.

3. Performance and indexing
- Add 2-3 high-value indexes from workload patterns.
- Enable DB slow-query logging and monthly EXPLAIN review.

4. Operations and resilience
- Implement backup retention + restore drill runbook.
- Add cron failure alerts and log aggregation.
- Tune workers/memory limits based on measured load tests.

5. Compliance hardening
- Mark master location seed data as protected (`noupdate`) where needed.
- Validate attachment ACL and PII handling policy for admission documents.

6. Validation gates
- Run portal role-based security tests (student, parent, teacher, admin).
- Run mobile Lighthouse + a11y checks and record baseline scores.
- Re-run module upgrade and targeted functional smoke tests.
