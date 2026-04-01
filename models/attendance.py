from odoo import fields, models


class ToriStudentAttendance(models.Model):
    _name = 'tori.student.attendance'
    _description = 'Student Attendance'

    enrollment_id = fields.Many2one('tori.enrollment', required=True, ondelete='cascade')
    date = fields.Date(required=True)
    timetable_slot_id = fields.Many2one('tori.timetable.slot')
    status = fields.Selection(
        [('present', 'Present'), ('absent', 'Absent'), ('late', 'Late'), ('excused', 'Excused')],
        default='present',
    )
    method = fields.Selection([('manual', 'Manual'), ('barcode', 'Barcode'), ('qr', 'QR Kiosk')], default='manual')
    marked_by = fields.Many2one('res.users')
    company_id = fields.Many2one(related='enrollment_id.company_id', store=True, readonly=True)

