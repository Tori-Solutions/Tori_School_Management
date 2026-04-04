from odoo import fields, models


class ToriDisciplineRecord(models.Model):
    _name = 'tori.discipline.record'
    _description = 'Discipline Record'
    _order = 'date desc'

    enrollment_id = fields.Many2one('tori.enrollment', required=True)
    date = fields.Date(required=True)
    category = fields.Char()
    description = fields.Text()
    action_taken = fields.Text()
    reported_by = fields.Many2one('res.users')
    company_id = fields.Many2one(related='enrollment_id.company_id', store=True, readonly=True)

