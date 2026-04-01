from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ToriTimetableSlot(models.Model):
    _name = 'tori.timetable.slot'
    _description = 'Timetable Slot'

    class_id = fields.Many2one('tori.class', required=True)
    section_id = fields.Many2one('tori.section')
    subject_id = fields.Many2one('tori.subject', required=True)
    teacher_id = fields.Many2one('res.users', required=True)
    room_id = fields.Many2one('tori.room')
    day = fields.Selection(
        [
            ('mon', 'Monday'),
            ('tue', 'Tuesday'),
            ('wed', 'Wednesday'),
            ('thu', 'Thursday'),
            ('fri', 'Friday'),
            ('sat', 'Saturday'),
            ('sun', 'Sunday'),
        ]
    )
    start_time = fields.Float()
    end_time = fields.Float()
    start_datetime = fields.Datetime(compute='_compute_datetimes', store=True)
    end_datetime = fields.Datetime(compute='_compute_datetimes', store=True)
    company_id = fields.Many2one(related='class_id.company_id', store=True, readonly=True)

    @api.depends('day', 'start_time', 'end_time')
    def _compute_datetimes(self):
        import datetime
        from odoo.tools.date_utils import relativedelta
        # Map day to weekday integer (Monday is 0, Sunday is 6)
        day_map = {'mon': 0, 'tue': 1, 'wed': 2, 'thu': 3, 'fri': 4, 'sat': 5, 'sun': 6}
        for rec in self:
            if not rec.day:
                rec.start_datetime = False
                rec.end_datetime = False
                continue
                
            # Base the calendar on the current week for recurrent visualization
            today = datetime.date.today()
            target_date = today + relativedelta(weekday=day_map[rec.day])
            
            s_hours, s_minutes = divmod(rec.start_time * 60, 60)
            e_hours, e_minutes = divmod(rec.end_time * 60, 60)
            
            rec.start_datetime = datetime.datetime.combine(target_date, datetime.time(int(s_hours), int(s_minutes)))
            rec.end_datetime = datetime.datetime.combine(target_date, datetime.time(int(e_hours), int(e_minutes)))

    @api.constrains('start_time', 'end_time')
    def _check_times(self):
        for rec in self:
            if rec.start_time >= rec.end_time:
                raise ValidationError('Start time must be less than end time.')

    @api.constrains('teacher_id', 'day', 'start_time', 'end_time')
    def _check_teacher_overlap(self):
        for rec in self:
            if not rec.teacher_id or not rec.day:
                continue
            overlap_domain = [
                ('id', '!=', rec.id),
                ('teacher_id', '=', rec.teacher_id.id),
                ('day', '=', rec.day),
                ('start_time', '<', rec.end_time),
                ('end_time', '>', rec.start_time),
            ]
            if self.search_count(overlap_domain):
                raise ValidationError('Teacher cannot be assigned to overlapping timetable slots.')

