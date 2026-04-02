from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    tori_application_count = fields.Integer(compute='_compute_tori_counts', string='Applications')
    tori_enrollment_count = fields.Integer(compute='_compute_tori_counts', string='Enrollments')

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
