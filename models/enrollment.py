from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_student = fields.Boolean(default=False)
    is_parent = fields.Boolean(default=False)


class ToriEnrollment(models.Model):
    _name = 'tori.enrollment'
    _description = 'Enrollment'
    _inherit = ['mail.thread']

    _uniq_tori_enrollment_student_session_company = models.Constraint(
        'unique(student_id, session_id, company_id)',
        'A student can only have one enrollment per session in the same company.',
    )

    name = fields.Char(compute='_compute_name', store=True)
    student_id = fields.Many2one('res.partner', required=True, domain=[('is_student', '=', True)])
    session_id = fields.Many2one('tori.session', required=True)
    academic_year_id = fields.Many2one('tori.academic.year', required=True)
    class_id = fields.Many2one('tori.class', required=True)
    section_id = fields.Many2one('tori.section')
    subject_ids = fields.Many2many('tori.subject')
    fee_structure_id = fields.Many2one('tori.fee.structure')
    is_mid_term = fields.Boolean(default=False)
    state = fields.Selection(
        [('active', 'Active'), ('inactive', 'Inactive'), ('graduated', 'Graduated')],
        default='active',
        tracking=True,
    )

    parent_id = fields.Many2one('res.partner', string='Parent')
    portal_access_level = fields.Selection([('full', 'Full'), ('limited', 'Limited')], default='limited')
    portal_access_granted = fields.Boolean(default=False)

    attendance_ids = fields.One2many('tori.student.attendance', 'enrollment_id')
    fee_slip_ids = fields.One2many('tori.fee.slip', 'enrollment_id')
    submission_ids = fields.One2many('tori.submission', 'enrollment_id')
    marksheet_ids = fields.One2many('tori.marksheet', 'enrollment_id')
    scholarship_ids = fields.One2many('tori.scholarship', 'enrollment_id')
    transport_ids = fields.One2many('tori.student.transport', 'enrollment_id')

    attendance_count = fields.Integer(compute='_compute_counts')
    fee_slip_count = fields.Integer(compute='_compute_counts')
    marksheet_count = fields.Integer(compute='_compute_counts')
    submission_count = fields.Integer(compute='_compute_counts')

    company_id = fields.Many2one('res.company', default=lambda self: self.env.company, required=True)

    def _compute_counts(self):
        for rec in self:
            rec.attendance_count = len(rec.attendance_ids)
            rec.fee_slip_count = len(rec.fee_slip_ids)
            rec.marksheet_count = len(rec.marksheet_ids)
            rec.submission_count = len(rec.submission_ids)

    def action_view_attendance(self):
        return {
            'name': 'Attendance',
            'view_mode': 'list,form',
            'res_model': 'tori.student.attendance',
            'domain': [('enrollment_id', '=', self.id)],
            'type': 'ir.actions.act_window',
        }

    def action_view_fee_slips(self):
        return {
            'name': 'Fee Slips',
            'view_mode': 'list,form',
            'res_model': 'tori.fee.slip',
            'domain': [('enrollment_id', '=', self.id)],
            'type': 'ir.actions.act_window',
        }

    def action_view_marksheets(self):
        return {
            'name': 'Marksheets',
            'view_mode': 'list,form',
            'res_model': 'tori.marksheet',
            'domain': [('enrollment_id', '=', self.id)],
            'type': 'ir.actions.act_window',
        }

    def action_view_assignments(self):
        return {
            'name': 'Submissions',
            'view_mode': 'list,form',
            'res_model': 'tori.submission',
            'domain': [('enrollment_id', '=', self.id)],
            'type': 'ir.actions.act_window',
        }

    @api.depends('student_id', 'class_id', 'session_id')
    def _compute_name(self):
        for rec in self:
            pieces = [rec.student_id.name or '', rec.class_id.name or '', rec.session_id.name or '']
            rec.name = ' / '.join([p for p in pieces if p])

    @api.constrains('academic_year_id', 'session_id')
    def _check_year_in_session(self):
        for rec in self:
            if rec.academic_year_id and rec.academic_year_id.session_id != rec.session_id:
                raise ValidationError('Academic year must belong to selected session.')

    @api.constrains('student_id', 'session_id', 'company_id')
    def _check_duplicate_enrollment(self):
        for rec in self:
            if not rec.student_id or not rec.session_id or not rec.company_id:
                continue
            duplicate_domain = [
                ('id', '!=', rec.id),
                ('student_id', '=', rec.student_id.id),
                ('session_id', '=', rec.session_id.id),
                ('company_id', '=', rec.company_id.id),
            ]
            if self.search_count(duplicate_domain):
                raise ValidationError(
                    'Duplicate enrollment detected: this student is already enrolled in the selected session.'
                )

    def unlink(self):
        for rec in self:
            if rec.fee_slip_ids or rec.marksheet_ids:
                raise ValidationError('Cannot delete enrollment with fee slips or marksheets.')
        return super().unlink()

    def action_grant_parent_portal_access(self):
        portal_group = self.env.ref('base.group_portal')
        for rec in self:
            if rec.parent_id and rec.parent_id.user_ids:
                rec.parent_id.user_ids.write({'groups_id': [(4, portal_group.id)]})
                rec.portal_access_granted = True

    def action_revoke_parent_portal_access(self):
        for rec in self:
            rec.portal_access_granted = False

