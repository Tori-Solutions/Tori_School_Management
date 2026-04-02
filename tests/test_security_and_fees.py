from odoo import fields
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('standard', 'at_install')
class TestSchoolManagementSecurityAndFees(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Company = cls.env['res.company']
        cls.Session = cls.env['tori.session']
        cls.AcademicYear = cls.env['tori.academic.year']
        cls.Class = cls.env['tori.class']
        cls.Subject = cls.env['tori.subject']
        cls.Section = cls.env['tori.section']
        cls.Enrollment = cls.env['tori.enrollment']
        cls.FeeStructure = cls.env['tori.fee.structure']
        cls.FeeElement = cls.env['tori.fee.element']
        cls.FeeSlip = cls.env['tori.fee.slip']
        cls.Assignment = cls.env['tori.assignment']
        cls.Term = cls.env['tori.term']

        cls.group_admin = cls.env.ref('tori_school_management.group_education_admin')
        cls.group_student = cls.env.ref('tori_school_management.group_education_student')
        cls.group_user = cls.env.ref('base.group_user')

        # Some enterprise modules (e.g. account_reports) add NOT NULL columns to res_company
        # without a DB-level default, relying on the ORM Python default. When those modules are
        # installed in the DB but their fields are not present in the current test run's registry
        # (e.g. missing enterprise license or selective load), raw Company.create() fails with a
        # NOT NULL violation. We add temporary column defaults at the DB level before creating test
        # companies and restore them immediately after.
        cls.env.cr.execute("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'res_company'
              AND is_nullable = 'NO'
              AND column_default IS NULL
              AND column_name NOT IN ('id', 'name', 'partner_id', 'sequence', 'create_uid', 'write_uid')
        """)
        cols_missing_default = [row[0] for row in cls.env.cr.fetchall()]
        safe_defaults = {
            'account_return_reminder_day': '7',
            'account_return_periodicity': "'monthly'",
        }
        for col in cols_missing_default:
            if col in safe_defaults:
                cls.env.cr.execute(
                    f'ALTER TABLE res_company ALTER COLUMN "{col}" SET DEFAULT {safe_defaults[col]}'
                )
        cls.company_a = cls.Company.create({'name': 'School Company A'})
        cls.company_b = cls.Company.create({'name': 'School Company B'})
        # Remove the temporary defaults to keep the schema state clean.
        for col in cols_missing_default:
            if col in safe_defaults:
                cls.env.cr.execute(
                    f'ALTER TABLE res_company ALTER COLUMN "{col}" DROP DEFAULT'
                )

        cls.admin_user = cls.env['res.users'].with_context(no_reset_password=True).create({
            'name': 'School Admin A',
            'login': 'school_admin_a_rules',
            'email': 'school_admin_a_rules@example.com',
            'company_id': cls.company_a.id,
            'company_ids': [(6, 0, [cls.company_a.id])],
            'group_ids': [(6, 0, [cls.group_user.id, cls.group_admin.id])],
        })

        cls.student_user = cls.env['res.users'].with_context(no_reset_password=True).create({
            'name': 'Student User A',
            'login': 'student_user_a_rules',
            'email': 'student_user_a_rules@example.com',
            'company_id': cls.company_a.id,
            'company_ids': [(6, 0, [cls.company_a.id])],
            'group_ids': [(6, 0, [cls.group_user.id, cls.group_student.id])],
        })
        cls.student_user.partner_id.is_student = True

        cls.session_a = cls.Session.create({
            'name': 'Session A',
            'start_date': fields.Date.from_string('2026-01-01'),
            'end_date': fields.Date.from_string('2026-12-31'),
            'company_id': cls.company_a.id,
            'branch_id': cls.company_a.id,
        })
        cls.session_b = cls.Session.create({
            'name': 'Session B',
            'start_date': fields.Date.from_string('2026-01-01'),
            'end_date': fields.Date.from_string('2026-12-31'),
            'company_id': cls.company_b.id,
            'branch_id': cls.company_b.id,
        })

        cls.academic_year_a = cls.AcademicYear.create({
            'title': 'AY-A',
            'session_id': cls.session_a.id,
            'start_date': fields.Date.from_string('2026-01-01'),
            'end_date': fields.Date.from_string('2026-12-31'),
        })
        cls.academic_year_b = cls.AcademicYear.create({
            'title': 'AY-B',
            'session_id': cls.session_b.id,
            'start_date': fields.Date.from_string('2026-01-01'),
            'end_date': fields.Date.from_string('2026-12-31'),
        })

        cls.term_a = cls.Term.create({
            'name': 'Term A',
            'academic_year_id': cls.academic_year_a.id,
            'weightage': 100.0,
            'start_date': fields.Date.from_string('2026-01-01'),
            'end_date': fields.Date.from_string('2026-06-30'),
        })

        cls.subject_a = cls.Subject.create({
            'name': 'Math A',
            'code': 'MATH-A',
            'company_id': cls.company_a.id,
        })
        cls.subject_b = cls.Subject.create({
            'name': 'Math B',
            'code': 'MATH-B',
            'company_id': cls.company_b.id,
        })

        cls.class_a = cls.Class.create({
            'name': 'Class A',
            'session_id': cls.session_a.id,
            'company_id': cls.company_a.id,
            'subject_ids': [(6, 0, [cls.subject_a.id])],
            'student_ids': [(6, 0, [cls.student_user.partner_id.id])],
        })
        cls.class_b = cls.Class.create({
            'name': 'Class B',
            'session_id': cls.session_b.id,
            'company_id': cls.company_b.id,
            'subject_ids': [(6, 0, [cls.subject_b.id])],
        })

        cls.section_a = cls.Section.create({
            'name': 'Section A',
            'class_id': cls.class_a.id,
        })
        cls.section_b = cls.Section.create({
            'name': 'Section B',
            'class_id': cls.class_b.id,
        })

        cls.enrollment_a = cls.Enrollment.create({
            'student_id': cls.student_user.partner_id.id,
            'session_id': cls.session_a.id,
            'academic_year_id': cls.academic_year_a.id,
            'class_id': cls.class_a.id,
            'section_id': cls.section_a.id,
            'company_id': cls.company_a.id,
            'state': 'active',
        })

        cls.assignment_a = cls.Assignment.create({
            'name': 'Assignment A',
            'assignment_type': 'homework',
            'class_id': cls.class_a.id,
            'section_id': cls.section_a.id,
            'subject_id': cls.subject_a.id,
            'teacher_id': cls.env.user.id,
            'term_id': cls.term_a.id,
            'deadline': fields.Datetime.now(),
        })
        cls.assignment_b = cls.Assignment.create({
            'name': 'Assignment B',
            'assignment_type': 'homework',
            'class_id': cls.class_b.id,
            'section_id': cls.section_b.id,
            'subject_id': cls.subject_b.id,
            'teacher_id': cls.env.user.id,
            'term_id': cls.term_a.id,
            'deadline': fields.Datetime.now(),
        })

        cls.fee_structure_a = cls.FeeStructure.create({
            'name': 'Fee Structure A',
            'class_id': cls.class_a.id,
            'session_id': cls.session_a.id,
            'company_id': cls.company_a.id,
        })
        cls.fee_structure_b = cls.FeeStructure.create({
            'name': 'Fee Structure B',
            'class_id': cls.class_b.id,
            'session_id': cls.session_b.id,
            'company_id': cls.company_b.id,
        })

        cls.recurring_element = cls.FeeElement.create({
            'fee_structure_id': cls.fee_structure_a.id,
            'name': 'Monthly Tuition',
            'amount': 1200.0,
            'fee_type': 'recurring',
            'recurring_interval': 'monthly',
        })
        cls.one_time_element = cls.FeeElement.create({
            'fee_structure_id': cls.fee_structure_a.id,
            'name': 'Admission Fee',
            'amount': 5000.0,
            'fee_type': 'one_time',
        })
        cls.FeeElement.create({
            'fee_structure_id': cls.fee_structure_b.id,
            'name': 'Monthly Tuition B',
            'amount': 900.0,
            'fee_type': 'recurring',
            'recurring_interval': 'monthly',
        })

        cls.enrollment_a.write({'fee_structure_id': cls.fee_structure_a.id})

    def test_company_isolation_rules_for_admin_user(self):
        class_records = self.Class.with_user(self.admin_user).search([])
        fee_structures = self.FeeStructure.with_user(self.admin_user).search([])

        self.assertEqual(class_records.ids, self.class_a.ids)
        self.assertEqual(fee_structures.ids, self.fee_structure_a.ids)

    def test_student_rules_limit_backend_visibility(self):
        assignments = self.Assignment.with_user(self.student_user).search([])
        classes = self.Class.with_user(self.student_user).search([])
        sections = self.Section.with_user(self.student_user).search([])
        subjects = self.Subject.with_user(self.student_user).search([])

        self.assertEqual(assignments.ids, self.assignment_a.ids)
        self.assertEqual(classes.ids, self.class_a.ids)
        self.assertEqual(sections.ids, self.section_a.ids)
        self.assertEqual(subjects.ids, self.subject_a.ids)

    def test_recurring_fee_cron_creates_missing_slip_once(self):
        self.FeeSlip.search([('enrollment_id', '=', self.enrollment_a.id)]).unlink()

        self.FeeSlip.cron_generate_recurring_slips()
        slips = self.FeeSlip.search([
            ('enrollment_id', '=', self.enrollment_a.id),
            ('fee_element_id', '=', self.recurring_element.id),
        ])
        self.assertEqual(len(slips), 1)
        self.assertEqual(slips.amount, 1200.0)

        self.FeeSlip.cron_generate_recurring_slips()
        slips = self.FeeSlip.search([
            ('enrollment_id', '=', self.enrollment_a.id),
            ('fee_element_id', '=', self.recurring_element.id),
        ])
        self.assertEqual(len(slips), 1)

    def test_recurring_fee_cron_ignores_one_time_elements(self):
        self.FeeSlip.search([('enrollment_id', '=', self.enrollment_a.id)]).unlink()

        self.FeeSlip.cron_generate_recurring_slips()
        one_time_slips = self.FeeSlip.search([
            ('enrollment_id', '=', self.enrollment_a.id),
            ('fee_element_id', '=', self.one_time_element.id),
        ])
        self.assertFalse(one_time_slips)
