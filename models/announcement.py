from odoo import fields, models


class ToriAnnouncement(models.Model):
    _name = 'tori.announcement'
    _description = 'Announcement'

    title = fields.Char(required=True)
    body = fields.Html()
    date = fields.Date(required=True)
    audience = fields.Selection(
        [('all', 'All'), ('teachers', 'Teachers'), ('students', 'Students')],
        default='all',
    )
    session_id = fields.Many2one('tori.session')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company, required=True)

