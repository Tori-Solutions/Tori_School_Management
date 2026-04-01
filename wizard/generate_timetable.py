from odoo import fields, models


class ToriGenerateTimetableWizard(models.TransientModel):
    _name = 'tori.generate.timetable.wizard'
    _description = 'Generate Timetable Wizard'

    class_id = fields.Many2one('tori.class', required=True)
    section_id = fields.Many2one('tori.section')
    room_id = fields.Many2one('tori.room')
    start_time = fields.Float(default=9.0)
    slot_duration = fields.Float(default=1.0)

    def action_generate(self):
        self.ensure_one()
        days = ['mon', 'tue', 'wed', 'thu', 'fri']
        time_start = self.start_time
        timetable = self.env['tori.timetable.slot']
        for idx, subject in enumerate(self.class_id.subject_ids):
            day = days[idx % len(days)]
            start = time_start + (idx // len(days)) * self.slot_duration
            end = start + self.slot_duration
            timetable.create({
                'class_id': self.class_id.id,
                'section_id': self.section_id.id,
                'subject_id': subject.id,
                'teacher_id': self.class_id.teacher_id.id or self.env.user.id,
                'room_id': self.room_id.id,
                'day': day,
                'start_time': start,
                'end_time': end,
            })

