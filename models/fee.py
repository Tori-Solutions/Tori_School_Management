from odoo import api, fields, models


class ToriFeeStructure(models.Model):
    _name = 'tori.fee.structure'
    _description = 'Fee Structure'

    name = fields.Char(required=True)
    class_id = fields.Many2one('tori.class')
    session_id = fields.Many2one('tori.session')
    fee_element_ids = fields.One2many('tori.fee.element', 'fee_structure_id')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company, required=True)


class ToriFeeElement(models.Model):
    _name = 'tori.fee.element'
    _description = 'Fee Element'

    fee_structure_id = fields.Many2one('tori.fee.structure', ondelete='cascade')
    name = fields.Char(required=True)
    amount = fields.Float()
    fee_type = fields.Selection([('one_time', 'One Time'), ('recurring', 'Recurring')], default='one_time')
    recurring_interval = fields.Selection(
        [('monthly', 'Monthly'), ('quarterly', 'Quarterly'), ('yearly', 'Yearly')],
        default='monthly',
    )
    late_fee_amount = fields.Float()
    grace_days = fields.Integer(default=7)
    company_id = fields.Many2one(related='fee_structure_id.company_id', store=True, readonly=True)


class ToriFeeSlip(models.Model):
    _name = 'tori.fee.slip'
    _description = 'Fee Slip'
    _inherit = ['mail.thread']

    enrollment_id = fields.Many2one('tori.enrollment', required=True)
    fee_structure_id = fields.Many2one('tori.fee.structure')
    fee_element_id = fields.Many2one('tori.fee.element')
    amount = fields.Float(tracking=True)
    due_date = fields.Date(tracking=True)
    paid_date = fields.Date()
    late_fee_applied = fields.Float()
    state = fields.Selection(
        [('draft', 'Draft'), ('sent', 'Sent'), ('paid', 'Paid'), ('overdue', 'Overdue')],
        default='draft',
        tracking=True,
    )
    invoice_id = fields.Many2one('account.move')
    company_id = fields.Many2one(related='enrollment_id.company_id', store=True, readonly=True)

    def action_send(self):
        self.write({'state': 'sent'})

    def action_mark_paid(self):
        self.write({'state': 'paid', 'paid_date': fields.Date.today()})

    def action_create_invoice(self):
        for rec in self:
            if rec.invoice_id:
                continue
            partner = rec.enrollment_id.parent_id or rec.enrollment_id.student_id
            invoice = self.env['account.move'].create({
                'move_type': 'out_invoice',
                'partner_id': partner.id,
                'invoice_date': fields.Date.today(),
                'invoice_line_ids': [(0, 0, {
                    'name': rec.fee_element_id.name or rec.fee_structure_id.name or rec.enrollment_id.name,
                    'quantity': 1.0,
                    'price_unit': rec.amount,
                })],
                'company_id': rec.company_id.id,
            })
            rec.invoice_id = invoice.id

    @api.model
    def cron_mark_overdue_and_apply_late_fee(self):
        today = fields.Date.today()
        slips = self.search([('state', 'in', ['draft', 'sent']), ('due_date', '<', today)])
        for slip in slips:
            element = slip.fee_element_id
            grace_days = element.grace_days if element else 0
            if slip.due_date and (today - slip.due_date).days > grace_days:
                values = {'state': 'overdue'}
                if element and element.late_fee_amount and not slip.late_fee_applied:
                    values.update({
                        'late_fee_applied': element.late_fee_amount,
                        'amount': slip.amount + element.late_fee_amount,
                    })
                slip.write(values)

    @api.model
    def cron_generate_recurring_slips(self):
        today = fields.Date.today()
        enrollments = self.env['tori.enrollment'].search([
            ('state', '=', 'active'),
            ('fee_structure_id', '!=', False),
        ])

        recurring_element_ids = enrollments.mapped('fee_structure_id.fee_element_ids').filtered(
            lambda element: element.fee_type == 'recurring'
        )
        existing_keys = set()
        if enrollments and recurring_element_ids:
            existing_slips = self.search([
                ('enrollment_id', 'in', enrollments.ids),
                ('fee_element_id', 'in', recurring_element_ids.ids),
                ('due_date', '>=', today),
                ('state', 'in', ['draft', 'sent', 'overdue']),
            ])
            existing_keys = {
                (slip.enrollment_id.id, slip.fee_element_id.id)
                for slip in existing_slips
            }

        create_vals = []
        for enrollment in enrollments:
            for element in enrollment.fee_structure_id.fee_element_ids.filtered(lambda e: e.fee_type == 'recurring'):
                key = (enrollment.id, element.id)
                if key in existing_keys:
                    continue
                create_vals.append({
                    'enrollment_id': enrollment.id,
                    'fee_structure_id': enrollment.fee_structure_id.id,
                    'fee_element_id': element.id,
                    'amount': enrollment._get_prorated_amount(element.amount),
                    'due_date': today,
                })
                existing_keys.add(key)

        if create_vals:
            self.create(create_vals)


class ToriEnrollmentFeeHook(models.Model):
    _inherit = 'tori.enrollment'

    def _get_prorated_amount(self, amount):
        self.ensure_one()
        if not self.is_mid_term or not self.academic_year_id.start_date:
            return amount
        start = self.academic_year_id.start_date
        end = self.academic_year_id.end_date or fields.Date.today()
        today = fields.Date.today()
        total_days = max((end - start).days, 1)
        remaining_days = max((end - today).days, 1)
        return round(amount * (remaining_days / total_days), 2)

    def action_generate_fee_slips(self):
        slip_model = self.env['tori.fee.slip']
        for rec in self:
            if not rec.fee_structure_id:
                continue
            for element in rec.fee_structure_id.fee_element_ids:
                amount = rec._get_prorated_amount(element.amount)
                slip_model.create({
                    'enrollment_id': rec.id,
                    'fee_structure_id': rec.fee_structure_id.id,
                    'fee_element_id': element.id,
                    'amount': amount,
                    'due_date': fields.Date.today(),
                })

