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
            results = rec.subject_result_ids
            if not results:
                rec.percentage = 0.0
                rec.gpa = 0.0
                rec.grade_letter = False
                continue

            total_credits = 0.0
            weighted_percent = 0.0
            weighted_gpa = 0.0
            scale = rec.enrollment_id.class_id.grade_scale_id
            grade_lines = scale.grade_line_ids if scale else self.env['tori.grade.line']

            # Single pass over subject results
            for sline in results:
                credit = sline.subject_id.credit_value or 1.0
                pct = ((sline.marks or 0.0) / (sline.total_marks or 1.0)) * 100.0

                # Lookup GPA from grade scale in this same pass
                gpa_pts = 0.0
                for gl in grade_lines:
                    if gl.min_percent <= pct <= gl.max_percent:
                        gpa_pts = gl.gpa_points
                        break

                weighted_percent += credit * pct
                weighted_gpa += credit * gpa_pts
                total_credits += credit

            if total_credits:
                final_pct = weighted_percent / total_credits
                final_gpa = weighted_gpa / total_credits
            else:
                final_pct = final_gpa = 0.0

            # Map final percentage to grade letter
            final_letter = False
            for gl in grade_lines:
                if gl.min_percent <= final_pct <= gl.max_percent:
                    final_letter = gl.grade_letter
                    break

            rec.percentage = final_pct
            rec.gpa = final_gpa
            rec.grade_letter = final_letter


class ToriSubjectResult(models.Model):
    _name = 'tori.subject.result'
    _description = 'Subject Result'

    marksheet_id = fields.Many2one('tori.marksheet', required=True, ondelete='cascade')
    subject_id = fields.Many2one('tori.subject', required=True)
    marks = fields.Float(default=0.0)
    total_marks = fields.Float(default=100.0)
    company_id = fields.Many2one(related='marksheet_id.company_id', store=True, readonly=True)

