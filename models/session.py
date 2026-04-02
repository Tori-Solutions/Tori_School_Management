from odoo import api, fields, models
from odoo.exceptions import AccessError, ValidationError


class ToriSession(models.Model):
    _name = 'tori.session'
    _description = 'School Session'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(required=True, tracking=True)
    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)
    state = fields.Selection(
        [('draft', 'Draft'), ('in_progress', 'In Progress'), ('done', 'Done')],
        default='draft',
        tracking=True,
    )
    academic_year_ids = fields.One2many('tori.academic.year', 'session_id')
    branch_id = fields.Many2one('res.company', default=lambda self: self.env.company, required=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company, required=True)
    total_application_count = fields.Integer(compute='_compute_dashboard_metrics', readonly=True)
    total_enrollment_count = fields.Integer(compute='_compute_dashboard_metrics', readonly=True)
    total_student_count = fields.Integer(compute='_compute_dashboard_metrics', readonly=True)
    total_faculty_count = fields.Integer(compute='_compute_dashboard_metrics', readonly=True)
    today_assignment_count = fields.Integer(compute='_compute_dashboard_metrics', readonly=True)

    def _compute_dashboard_metrics(self):
        today = fields.Date.context_today(self)
        session_ids = self.ids
        company_ids = self.mapped('company_id').ids

        application_counts = {}
        enrollment_counts = {}
        student_counts = {}
        faculty_counts = {}
        assignment_counts = {}

        if session_ids:
            try:
                application_counts = {
                    session.id: count
                    for session, count in self.env['tori.student.application']._read_group(
                        [('session_id', 'in', session_ids)],
                        ['session_id'],
                        ['__count'],
                    )
                    if session
                }
            except AccessError:
                application_counts = {}

            try:
                enrollment_counts = {
                    session.id: count
                    for session, count in self.env['tori.enrollment']._read_group(
                        [('session_id', 'in', session_ids)],
                        ['session_id'],
                        ['__count'],
                    )
                    if session
                }
                for session, student, _count in self.env['tori.enrollment']._read_group(
                    [('session_id', 'in', session_ids)],
                    ['session_id', 'student_id'],
                    ['__count'],
                ):
                    if session and student:
                        student_counts[session.id] = student_counts.get(session.id, 0) + 1
            except AccessError:
                enrollment_counts = {}
                student_counts = {}

            try:
                faculty_counts = {
                    company.id: count
                    for company, count in self.env['hr.employee']._read_group(
                        [('is_teacher', '=', True), ('company_id', 'in', company_ids)],
                        ['company_id'],
                        ['__count'],
                    )
                    if company
                }
            except AccessError:
                faculty_counts = {}

            try:
                assignments = self.env['tori.assignment'].search([
                    ('class_id.session_id', 'in', session_ids),
                    ('deadline', '>=', today),
                ])
                for assignment in assignments:
                    session_id = assignment.class_id.session_id.id
                    assignment_counts[session_id] = assignment_counts.get(session_id, 0) + 1
            except AccessError:
                assignment_counts = {}

        for rec in self:
            rec.total_application_count = application_counts.get(rec.id, 0)
            rec.total_enrollment_count = enrollment_counts.get(rec.id, 0)
            rec.total_student_count = student_counts.get(rec.id, 0)
            rec.total_faculty_count = faculty_counts.get(rec.company_id.id, 0)
            rec.today_assignment_count = assignment_counts.get(rec.id, 0)

    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        for rec in self:
            if rec.start_date and rec.end_date and rec.start_date > rec.end_date:
                raise ValidationError('Session start date must be before end date.')


class ToriAcademicYear(models.Model):
    _name = 'tori.academic.year'
    _description = 'Academic Year'

    title = fields.Char(required=True)
    session_id = fields.Many2one('tori.session', required=True, ondelete='cascade')
    start_date = fields.Date()
    end_date = fields.Date()
    term_ids = fields.One2many('tori.term', 'academic_year_id')
    company_id = fields.Many2one(related='session_id.company_id', store=True, readonly=True)

    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        for rec in self:
            if rec.start_date and rec.end_date and rec.start_date > rec.end_date:
                raise ValidationError('Academic year start date must be before end date.')


class ToriTerm(models.Model):
    _name = 'tori.term'
    _description = 'Academic Term'

    name = fields.Char(required=True)
    academic_year_id = fields.Many2one('tori.academic.year', required=True, ondelete='cascade')
    weightage = fields.Float(
        required=True,
        help='% contribution to annual result. All terms in a year must sum to 100.',
    )
    start_date = fields.Date()
    end_date = fields.Date()
    company_id = fields.Many2one(related='academic_year_id.company_id', store=True, readonly=True)

    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        for rec in self:
            if rec.start_date and rec.end_date and rec.start_date > rec.end_date:
                raise ValidationError('Term start date must be before end date.')

    @api.constrains('weightage', 'academic_year_id')
    def _check_total_weightage(self):
        for rec in self:
            if not rec.academic_year_id:
                continue
            total = sum(rec.academic_year_id.term_ids.mapped('weightage'))
            if round(total, 2) > 100.0:
                raise ValidationError('Term weightage total cannot exceed 100 for an academic year.')
            if rec.academic_year_id.term_ids and len(rec.academic_year_id.term_ids) > 1 and round(total, 2) != 100.0:
                # Enforce exact sum once multiple terms are defined.
                raise ValidationError('All term weightages in an academic year must sum to 100.')

