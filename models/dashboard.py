from odoo import api, fields, models


class ToriDashboard(models.AbstractModel):
    _name = 'tori.dashboard'
    _description = 'Tori Dashboard Stats'

    @api.model
    def _safe_count(self, model_name, domain=None):
        try:
            return self.env[model_name].search_count(domain or [])
        except Exception:
            return 0

    @api.model
    def _safe_search_read(self, model_name, domain, field_names, limit=5, order='id desc'):
        try:
            return self.env[model_name].search_read(domain, field_names, limit=limit, order=order)
        except Exception:
            return []

    @api.model
    def _compute_stats(self):
        today = fields.Date.context_today(self)
        stats = {
            'total_students': 0,
            'total_faculty': 0,
            'total_enrollments': 0,
            'pending_apps': 0,
            'overdue_fees': 0,
            'attendance_pct': 0,
            'present_today': 0,
            'late_today': 0,
            'absent_today': 0,
            'attendance_total_today': 0,
            'today_notices': 0,
        }

        stats['total_students'] = self._safe_count('res.partner', [('is_student', '=', True)])

        # `is_teacher` may not exist in all DBs/environments.
        try:
            employee_model = self.env['hr.employee']
            employee_domain = [('is_teacher', '=', True)] if 'is_teacher' in employee_model._fields else []
            stats['total_faculty'] = employee_model.search_count(employee_domain)
        except Exception:
            stats['total_faculty'] = 0

        stats['total_enrollments'] = self._safe_count('tori.enrollment', [('state', '=', 'active')])
        stats['pending_apps'] = self._safe_count('tori.student.application', [('state', 'in', ['draft', 'confirm'])])
        stats['overdue_fees'] = self._safe_count('tori.fee.slip', [('state', '=', 'overdue')])
        stats['today_notices'] = self._safe_count('tori.announcement', [('date', '=', today)])

        try:
            attendance_model = self.env['tori.student.attendance']
            total_today = attendance_model.search_count([('date', '=', today)])
            present_today = attendance_model.search_count([('date', '=', today), ('status', '=', 'present')])
            late_today = attendance_model.search_count([('date', '=', today), ('status', '=', 'late')])
            absent_today = attendance_model.search_count([('date', '=', today), ('status', '=', 'absent')])

            stats['attendance_total_today'] = total_today
            stats['present_today'] = present_today
            stats['late_today'] = late_today
            stats['absent_today'] = absent_today
            if total_today:
                stats['attendance_pct'] = round(((present_today + late_today) / total_today) * 100)
        except Exception:
            pass

        return stats

    @api.model
    def get_dashboard_stats(self):
        return self._compute_stats()

    @api.model
    def get_dashboard_payload(self):
        stats = self._compute_stats()

        recent_applications = self._safe_search_read(
            'tori.student.application',
            [('state', '!=', 'cancel')],
            ['name', 'student_name', 'state', 'class_id', 'stage_id', 'write_date'],
            limit=6,
            order='write_date desc',
        )

        fee_alerts = self._safe_search_read(
            'tori.fee.slip',
            [('state', 'in', ['overdue', 'sent'])],
            ['enrollment_id', 'amount', 'due_date', 'state'],
            limit=6,
            order='due_date asc',
        )

        announcements = self._safe_search_read(
            'tori.announcement',
            [('date', '=', fields.Date.context_today(self))],
            ['title', 'body', 'audience', 'date'],
            limit=6,
            order='id desc',
        )

        pipeline = []
        try:
            grouped = self.env['tori.student.application'].read_group(
                [('state', '!=', 'cancel')],
                ['stage_id'],
                ['stage_id'],
                lazy=False,
            )
            pipeline = [
                {
                    'stage': row['stage_id'][1] if row.get('stage_id') else 'Unassigned',
                    'count': row.get('__count', 0),
                }
                for row in grouped
            ]
        except Exception:
            pipeline = []

        return {
            'stats': stats,
            'recent_applications': recent_applications,
            'fee_alerts': fee_alerts,
            'announcements_today': announcements,
            'pipeline': pipeline,
            'generated_on': fields.Datetime.now(),
        }
