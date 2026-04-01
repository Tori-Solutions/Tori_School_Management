from odoo import api, fields, models


class ToriMarksheet(models.Model):
    _name = 'tori.marksheet'
    _description = 'Marksheet'

    enrollment_id = fields.Many2one('tori.enrollment', required=True)
    term_id = fields.Many2one('tori.term', required=True)
    percentage = fields.Float(compute='_compute_result', store=True)
    gpa = fields.Float(compute='_compute_result', store=True)
    grade_letter = fields.Char(compute='_compute_result', store=True)
    subject_result_ids = fields.One2many('tori.subject.result', 'marksheet_id')
    company_id = fields.Many2one(related='enrollment_id.company_id', store=True, readonly=True)

    @api.depends(
        'subject_result_ids.marks',
        'subject_result_ids.total_marks',
        'subject_result_ids.subject_id.credit_value',
        'enrollment_id.class_id.grade_scale_id.grade_line_ids',
    )
    def _compute_result(self):
        for rec in self:
            weighted_percent = 0.0
            weighted_gpa = 0.0
            total_credits = 0.0
            for line in rec.subject_result_ids:
                credit = line.subject_id.credit_value or 1.0
                pct = ((line.marks or 0.0) / (line.total_marks or 1.0)) * 100.0
                weighted_percent += credit * pct
                total_credits += credit
            rec.percentage = weighted_percent / total_credits if total_credits else 0.0

            scale = rec.enrollment_id.class_id.grade_scale_id
            line = False
            if scale:
                line = scale.grade_line_ids.filtered(
                    lambda g: g.min_percent <= rec.percentage <= g.max_percent
                )[:1]
            rec.grade_letter = line.grade_letter if line else False
            rec.gpa = line.gpa_points if line else 0.0
            if total_credits and scale:
                # Credit-weighted GPA at subject-line level when possible.
                weighted_gpa_points = 0.0
                for sline in rec.subject_result_ids:
                    credit = sline.subject_id.credit_value or 1.0
                    pct = ((sline.marks or 0.0) / (sline.total_marks or 1.0)) * 100.0
                    gl = scale.grade_line_ids.filtered(lambda g: g.min_percent <= pct <= g.max_percent)[:1]
                    weighted_gpa_points += credit * (gl.gpa_points if gl else 0.0)
                rec.gpa = weighted_gpa_points / total_credits


class ToriSubjectResult(models.Model):
    _name = 'tori.subject.result'
    _description = 'Subject Result'

    marksheet_id = fields.Many2one('tori.marksheet', required=True, ondelete='cascade')
    subject_id = fields.Many2one('tori.subject', required=True)
    marks = fields.Float(default=0.0)
    total_marks = fields.Float(default=100.0)
    company_id = fields.Many2one(related='marksheet_id.company_id', store=True, readonly=True)

