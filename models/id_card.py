from odoo import fields, models


class ToriIdCard(models.Model):
    _name = 'tori.id.card'
    _description = 'ID Card'

    enrollment_id = fields.Many2one('tori.enrollment', required=True)
    design_id = fields.Many2one('tori.id.card.design')
    barcode = fields.Char(related='enrollment_id.student_id.barcode')
    company_id = fields.Many2one(related='enrollment_id.company_id', store=True, readonly=True)


class ToriIdCardDesign(models.Model):
    _name = 'tori.id.card.design'
    _description = 'ID Card Design'

    name = fields.Char()
    orientation = fields.Selection([('horizontal', 'Horizontal'), ('vertical', 'Vertical')], default='horizontal')
    template_html = fields.Html(sanitize=True, sanitize_attributes=True, strip_style=False)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company, required=True)

