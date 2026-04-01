from odoo import api, fields, models


class ToriSubject(models.Model):
    _name = 'tori.subject'
    _description = 'Subject'

    name = fields.Char(required=True)
    code = fields.Char()
    credit_value = fields.Float(default=1.0, help='Used in credit-weighted GPA calculation')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company, required=True)


class ToriClass(models.Model):
    _name = 'tori.class'
    _description = 'Class'
    _inherit = ['mail.thread']

    name = fields.Char(required=True, tracking=True)
    session_id = fields.Many2one('tori.session', required=True)
    teacher_id = fields.Many2one('res.users')
    grade_scale_id = fields.Many2one('tori.grade.scale')
    subject_ids = fields.Many2many('tori.subject')
    section_ids = fields.One2many('tori.section', 'class_id')
    student_ids = fields.Many2many('res.partner', domain=[('is_student', '=', True)])
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company, required=True)

    @api.onchange('session_id')
    def _onchange_session(self):
        if self.session_id:
            self.company_id = self.session_id.company_id


class ToriSection(models.Model):
    _name = 'tori.section'
    _description = 'Class Section'

    name = fields.Char(required=True)
    class_id = fields.Many2one('tori.class', ondelete='cascade', required=True)
    company_id = fields.Many2one(related='class_id.company_id', store=True, readonly=True)


class ToriRoom(models.Model):
    _name = 'tori.room'
    _description = 'Room'

    name = fields.Char(required=True)
    capacity = fields.Integer()
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company, required=True)

