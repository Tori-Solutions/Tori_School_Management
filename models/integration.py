from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    tori_application_count = fields.Integer(compute='_compute_tori_counts', string='Applications')
    tori_enrollment_count = fields.Integer(compute='_compute_tori_counts', string='Enrollments')

    enrollment_ids = fields.One2many('tori.enrollment', 'student_id', string='Enrollments')

    tori_current_class_id = fields.Many2one(
        'tori.class', string='Current Class',
        compute='_compute_current_academic', store=True,
    )
    tori_current_section_id = fields.Many2one(
        'tori.section', string='Current Section',
        compute='_compute_current_academic', store=True,
    )
    tori_current_session_id = fields.Many2one(
        'tori.session', string='Current Session',
        compute='_compute_current_academic', store=True,
    )
    tori_current_enrollment_state = fields.Selection(
        [('active', 'Active'), ('inactive', 'Inactive'), ('graduated', 'Graduated')],
        string='Enrollment Status',
        compute='_compute_current_academic', store=True,
    )

    @api.depends(
        'enrollment_ids',
        'enrollment_ids.class_id',
        'enrollment_ids.section_id',
        'enrollment_ids.session_id',
        'enrollment_ids.state',
    )
    def _compute_current_academic(self):
        for partner in self:
            # Pick the most recent active enrollment; fall back to any latest enrollment
            active = partner.enrollment_ids.filtered(lambda e: e.state == 'active')
            enrollment = active[:1] if active else partner.enrollment_ids[:1]
            partner.tori_current_class_id = enrollment.class_id if enrollment else False
            partner.tori_current_section_id = enrollment.section_id if enrollment else False
            partner.tori_current_session_id = enrollment.session_id if enrollment else False
            partner.tori_current_enrollment_state = enrollment.state if enrollment else False

    def _compute_tori_counts(self):
        for partner in self:
            partner.tori_application_count = self.env['tori.student.application'].search_count([('student_partner_id', '=', partner.id)])
            partner.tori_enrollment_count = self.env['tori.enrollment'].search_count([('student_id', '=', partner.id)])

    def action_view_tori_applications(self):
        self.ensure_one()
        return {
            'name': 'Applications',
            'view_mode': 'list,form',
            'res_model': 'tori.student.application',
            'domain': [('student_partner_id', '=', self.id)],
            'type': 'ir.actions.act_window',
        }

    def action_view_tori_enrollments(self):
        self.ensure_one()
        return {
            'name': 'Enrollments',
            'view_mode': 'list,form',
            'res_model': 'tori.enrollment',
            'domain': [('student_id', '=', self.id)],
            'type': 'ir.actions.act_window',
        }

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    is_teacher = fields.Boolean(string="Is a Teacher", default=False)
    tori_class_count = fields.Integer(compute='_compute_tori_class_count', string='Classes')

    def _compute_tori_class_count(self):
        for employee in self:
            if employee.user_id:
                employee.tori_class_count = self.env['tori.class'].search_count([('teacher_id', '=', employee.user_id.id)])
            else:
                employee.tori_class_count = 0

    def action_view_tori_classes(self):
        self.ensure_one()
        return {
            'name': 'Classes',
            'view_mode': 'list,form',
            'res_model': 'tori.class',
            'domain': [('teacher_id', '=', self.user_id.id)] if self.user_id else [('id', '=', 0)],
            'type': 'ir.actions.act_window',
        }

class AccountMove(models.Model):
    _inherit = 'account.move'

    tori_fee_slip_id = fields.Many2one('tori.fee.slip', string='Fee Slip', readonly=True)
