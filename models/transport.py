from odoo import fields, models


class ToriTransportRoute(models.Model):
    _name = 'tori.transport.route'
    _description = 'Transport Route'

    name = fields.Char(required=True)
    vehicle_id = fields.Many2one('tori.vehicle', required=True)
    driver_id = fields.Many2one('tori.driver', required=True)
    stop_ids = fields.One2many('tori.transport.stop', 'route_id')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company, required=True)


class ToriTransportStop(models.Model):
    _name = 'tori.transport.stop'
    _description = 'Transport Stop'

    name = fields.Char(required=True)
    route_id = fields.Many2one('tori.transport.route', ondelete='cascade')
    sequence = fields.Integer()
    arrival_time = fields.Float()
    company_id = fields.Many2one(related='route_id.company_id', store=True, readonly=True)


class ToriVehicle(models.Model):
    _name = 'tori.vehicle'
    _description = 'Vehicle'

    name = fields.Char(required=True)
    reg_number = fields.Char()
    capacity = fields.Integer()
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company, required=True)


class ToriDriver(models.Model):
    _name = 'tori.driver'
    _description = 'Driver'

    name = fields.Char(required=True)
    license_no = fields.Char()
    partner_id = fields.Many2one('res.partner')
    phone = fields.Char()
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company, required=True)


class ToriStudentTransport(models.Model):
    _name = 'tori.student.transport'
    _description = 'Student Transport'

    enrollment_id = fields.Many2one('tori.enrollment', required=True)
    route_id = fields.Many2one('tori.transport.route', required=True)
    stop_id = fields.Many2one('tori.transport.stop', required=True)
    trip_type = fields.Selection([('pickup', 'Pickup'), ('drop', 'Drop'), ('both', 'Both')], default='both')
    trip_attendance = fields.Selection([('present', 'Present'), ('absent', 'Absent')], default='present')
    trip_date = fields.Date()
    company_id = fields.Many2one(related='enrollment_id.company_id', store=True, readonly=True)

