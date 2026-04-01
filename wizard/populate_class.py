from odoo import fields, models


class ToriPopulateClassWizard(models.TransientModel):
    _name = 'tori.populate.class.wizard'
    _description = 'Populate Class Wizard'

    class_id = fields.Many2one('tori.class', required=True)
    enrollment_ids = fields.Many2many('tori.enrollment', required=True)

    def action_populate(self):
        self.ensure_one()
        students = self.enrollment_ids.mapped('student_id').ids
        self.class_id.student_ids = [(6, 0, list(set(self.class_id.student_ids.ids + students)))]

