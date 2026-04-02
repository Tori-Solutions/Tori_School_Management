from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    application_ids = fields.One2many('tori.student.application', 'student_partner_id', string='Application Records')
    tori_application_count = fields.Integer(compute='_compute_tori_counts', string='Applications', store=True)
    tori_enrollment_count = fields.Integer(compute='_compute_tori_counts', string='Enrollments', store=True)

    enrollment_ids = fields.One2many('tori.enrollment', 'student_id', string='Enrollment Records')

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
        'application_ids',
        'enrollment_ids',
        'enrollment_ids.class_id',
        'enrollment_ids.section_id',
        'enrollment_ids.session_id',
        'enrollment_ids.state',
    )
    def _compute_current_academic(self):
        current_enrollment_by_partner = {}
        partner_ids = self.ids

        if partner_ids:
            active_enrollments = self.env['tori.enrollment'].search([
                ('student_id', 'in', partner_ids),
                ('state', '=', 'active'),
            ], order='student_id, id desc')
            for enrollment in active_enrollments:
                current_enrollment_by_partner.setdefault(enrollment.student_id.id, enrollment)

            missing_partner_ids = [partner_id for partner_id in partner_ids if partner_id not in current_enrollment_by_partner]
            if missing_partner_ids:
                latest_enrollments = self.env['tori.enrollment'].search([
                    ('student_id', 'in', missing_partner_ids),
                ], order='student_id, id desc')
                for enrollment in latest_enrollments:
                    current_enrollment_by_partner.setdefault(enrollment.student_id.id, enrollment)

        for partner in self:
            enrollment = current_enrollment_by_partner.get(partner.id)
            partner.tori_current_class_id = enrollment.class_id if enrollment else False
            partner.tori_current_section_id = enrollment.section_id if enrollment else False
            partner.tori_current_session_id = enrollment.session_id if enrollment else False
            partner.tori_current_enrollment_state = enrollment.state if enrollment else False

    @api.depends('application_ids', 'enrollment_ids')
    def _compute_tori_counts(self):
        application_counts = {
            student_partner.id: count
            for student_partner, count in self.env['tori.student.application']._read_group(
                [('student_partner_id', 'in', self.ids)],
                ['student_partner_id'],
                ['__count'],
            )
            if student_partner
        }
        enrollment_counts = {
            student.id: count
            for student, count in self.env['tori.enrollment']._read_group(
                [('student_id', 'in', self.ids)],
                ['student_id'],
                ['__count'],
            )
            if student
        }
        for partner in self:
            partner.tori_application_count = application_counts.get(partner.id, 0)
            partner.tori_enrollment_count = enrollment_counts.get(partner.id, 0)

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
