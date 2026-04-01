from odoo import fields, models


class ToriLessonPlan(models.Model):
    _name = 'tori.lesson.plan'
    _description = 'Lesson Plan'

    class_id = fields.Many2one('tori.class', required=True)
    subject_id = fields.Many2one('tori.subject', required=True)
    teacher_id = fields.Many2one('res.users', required=True)
    lesson_date = fields.Date(required=True)
    objectives = fields.Text()
    content = fields.Html()
    homework_ids = fields.One2many('tori.homework', 'lesson_plan_id')
    company_id = fields.Many2one(related='class_id.company_id', store=True, readonly=True)


class ToriHomework(models.Model):
    _name = 'tori.homework'
    _description = 'Homework'

    lesson_plan_id = fields.Many2one('tori.lesson.plan', ondelete='cascade')
    description = fields.Text(required=True)
    deadline = fields.Date()
    attachment_ids = fields.Many2many('ir.attachment')
    company_id = fields.Many2one(related='lesson_plan_id.company_id', store=True, readonly=True)

