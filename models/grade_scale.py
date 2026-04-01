from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ToriGradeScale(models.Model):
    _name = 'tori.grade.scale'
    _description = 'Grade Scale'

    name = fields.Char(required=True)
    is_gpa_based = fields.Boolean(default=True)
    grade_line_ids = fields.One2many('tori.grade.line', 'grade_scale_id')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company, required=True)


class ToriGradeLine(models.Model):
    _name = 'tori.grade.line'
    _description = 'Grade Scale Line'

    grade_scale_id = fields.Many2one('tori.grade.scale', ondelete='cascade', required=True)
    grade_letter = fields.Char(required=True)
    min_percent = fields.Float(required=True)
    max_percent = fields.Float(required=True)
    gpa_points = fields.Float(default=0.0)
    company_id = fields.Many2one(related='grade_scale_id.company_id', store=True, readonly=True)

    @api.constrains('min_percent', 'max_percent')
    def _check_min_max(self):
        for rec in self:
            if rec.min_percent < 0 or rec.max_percent > 100 or rec.min_percent > rec.max_percent:
                raise ValidationError('Grade percentage range must be valid and between 0 and 100.')

    @api.constrains('min_percent', 'max_percent', 'grade_scale_id')
    def _check_overlap(self):
        for rec in self:
            others = rec.grade_scale_id.grade_line_ids.filtered(lambda l: l.id != rec.id)
            for other in others:
                if rec.min_percent <= other.max_percent and rec.max_percent >= other.min_percent:
                    raise ValidationError('Grade line ranges cannot overlap in the same grade scale.')

