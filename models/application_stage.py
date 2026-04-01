from odoo import fields, models


class ToriApplicationStage(models.Model):
    _name = 'tori.application.stage'
    _description = 'Application Stage'
    _order = 'sequence, id'

    name = fields.Char(required=True, translate=True)
    sequence = fields.Integer(default=10, index=True)
    code = fields.Selection(
        [('draft', 'Draft'), ('confirm', 'Confirmed'), ('enrolled', 'Enrolled'), ('cancel', 'Cancelled')],
        required=True,
        default='draft',
        index=True,
    )
    fold = fields.Boolean(string='Folded in Kanban')
    active = fields.Boolean(default=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company, required=True, index=True)
