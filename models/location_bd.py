from odoo import fields, models


class ToriBdDistrict(models.Model):
    _name = 'tori.bd.district'
    _description = 'Bangladesh District'
    _order = 'name'

    name = fields.Char(required=True, index=True)
    code = fields.Char(index=True)
    source_id = fields.Integer(index=True)
    upazila_ids = fields.One2many('tori.bd.upazila', 'district_id')


class ToriBdUpazila(models.Model):
    _name = 'tori.bd.upazila'
    _description = 'Bangladesh Upazila/Thana'
    _order = 'name'

    name = fields.Char(required=True, index=True)
    code = fields.Char(index=True)
    source_id = fields.Integer(index=True)
    district_id = fields.Many2one('tori.bd.district', required=True, ondelete='restrict', index=True)