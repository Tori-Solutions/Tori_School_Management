from odoo import api, fields, models


class ToriAssignment(models.Model):
    _name = 'tori.assignment'
    _description = 'Assignment'
    _inherit = ['mail.thread']

    name = fields.Char(required=True)
    assignment_type = fields.Selection(
        [('homework', 'Homework'), ('project', 'Project'), ('exam', 'Exam'), ('quiz', 'Quiz')],
        default='homework',
    )
    class_id = fields.Many2one('tori.class', required=True)
    section_id = fields.Many2one('tori.section')
    subject_id = fields.Many2one('tori.subject', required=True)
    teacher_id = fields.Many2one('res.users', required=True)
    term_id = fields.Many2one('tori.term', required=True)
    deadline = fields.Datetime()
    total_marks = fields.Float(default=100.0)
    instructions = fields.Html()
    attachment_ids = fields.Many2many('ir.attachment')
    submission_ids = fields.One2many('tori.submission', 'assignment_id')
    company_id = fields.Many2one(related='class_id.company_id', store=True, readonly=True)


class ToriSubmission(models.Model):
    _name = 'tori.submission'
    _description = 'Assignment Submission'

    assignment_id = fields.Many2one('tori.assignment', required=True, ondelete='cascade')
    enrollment_id = fields.Many2one('tori.enrollment', required=True)
    submission_date = fields.Datetime()
    attachment_ids = fields.Many2many('ir.attachment')
    marks = fields.Float()
    grade = fields.Char(compute='_compute_grade', store=True)
    feedback = fields.Text()
    state = fields.Selection(
        [('pending', 'Pending'), ('submitted', 'Submitted'), ('graded', 'Graded')],
        default='pending',
    )
    company_id = fields.Many2one(related='enrollment_id.company_id', store=True, readonly=True)

    @api.depends('marks', 'assignment_id.total_marks', 'enrollment_id.class_id.grade_scale_id.grade_line_ids')
    def _compute_grade(self):
        for rec in self:
            rec.grade = False
            if not rec.assignment_id.total_marks:
                continue
            percent = (rec.marks / rec.assignment_id.total_marks) * 100.0 if rec.marks else 0.0
            scale = rec.enrollment_id.class_id.grade_scale_id
            if scale:
                line = scale.grade_line_ids.filtered(lambda l: l.min_percent <= percent <= l.max_percent)[:1]
                rec.grade = line.grade_letter if line else False

    def action_submit(self):
        self.write({'state': 'submitted', 'submission_date': fields.Datetime.now()})

    def action_grade(self):
        self.write({'state': 'graded'})

