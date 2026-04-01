from odoo import fields, models


class ToriCommunityService(models.Model):
    _name = 'tori.community.service'
    _description = 'Community Service'

    enrollment_id = fields.Many2one('tori.enrollment', required=True)
    date = fields.Date()
    hours = fields.Float()
    description = fields.Text()
    state = fields.Selection([('pending', 'Pending'), ('approved', 'Approved')], default='pending')
    approved_by = fields.Many2one('res.users')
    company_id = fields.Many2one(related='enrollment_id.company_id', store=True, readonly=True)

