from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ToriFeeStructure(models.Model):
    _name = 'tori.fee.structure'
    _description = 'Fee Structure'

    name = fields.Char(required=True)
    class_id = fields.Many2one('tori.class')
    session_id = fields.Many2one('tori.session')
    fee_element_ids = fields.One2many('tori.fee.element', 'fee_structure_id')
    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id,
        required=True,
    )
    sale_journal_id = fields.Many2one(
        'account.journal',
        domain="[('type', '=', 'sale'), ('company_id', '=', company_id)]",
        check_company=True,
        help='Optional sales journal used when creating fee invoices.',
    )
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company, required=True)


class ToriFeeElement(models.Model):
    _name = 'tori.fee.element'
    _description = 'Fee Element'

    fee_structure_id = fields.Many2one('tori.fee.structure', ondelete='cascade')
    name = fields.Char(required=True)
    currency_id = fields.Many2one(
        'res.currency',
        related='fee_structure_id.currency_id',
        store=True, readonly=True,
    )
    amount = fields.Monetary(currency_field='currency_id')
    income_account_id = fields.Many2one(
        'account.account',
        domain="[('deprecated', '=', False)]",
        help='Income account used for invoice lines generated from this fee element.',
    )
    tax_ids = fields.Many2many(
        'account.tax',
        domain="[('type_tax_use', '=', 'sale')]",
        help='Sales taxes applied when this fee element is invoiced.',
    )
    fee_type = fields.Selection([('one_time', 'One Time'), ('recurring', 'Recurring')], default='one_time')
    recurring_interval = fields.Selection(
        [('monthly', 'Monthly'), ('quarterly', 'Quarterly'), ('yearly', 'Yearly')],
        default='monthly',
    )
    late_fee_amount = fields.Monetary(currency_field='currency_id')
    grace_days = fields.Integer(default=7)
    company_id = fields.Many2one(related='fee_structure_id.company_id', store=True, readonly=True)


class ToriFeeSlip(models.Model):
    _name = 'tori.fee.slip'
    _description = 'Fee Slip'
    _inherit = ['mail.thread']
    _order = 'due_date desc, id desc'

    enrollment_id = fields.Many2one('tori.enrollment', required=True, index=True)
    fee_structure_id = fields.Many2one('tori.fee.structure', index=True)
    fee_element_id = fields.Many2one('tori.fee.element', index=True)
    currency_id = fields.Many2one(
        'res.currency',
        related='enrollment_id.company_id.currency_id',
        store=True, readonly=True,
    )
    base_amount = fields.Monetary(currency_field='currency_id', tracking=True)
    scholarship_discount = fields.Monetary(currency_field='currency_id', readonly=True)
    amount = fields.Monetary(currency_field='currency_id', tracking=True)
    due_date = fields.Date(tracking=True)
    paid_date = fields.Date()
    late_fee_applied = fields.Monetary(currency_field='currency_id')
    state = fields.Selection(
        [('draft', 'Draft'), ('sent', 'Sent'), ('paid', 'Paid'), ('overdue', 'Overdue')],
        default='draft',
        tracking=True,
    )
    invoice_id = fields.Many2one('account.move', ondelete='restrict', index=True)
    company_id = fields.Many2one(related='enrollment_id.company_id', store=True, readonly=True)

    @api.onchange('enrollment_id')
    def _onchange_enrollment_id(self):
        for rec in self:
            if rec.enrollment_id and not rec.fee_structure_id:
                rec.fee_structure_id = rec.enrollment_id.fee_structure_id

    @api.onchange('fee_structure_id')
    def _onchange_fee_structure_id(self):
        for rec in self:
            if rec.fee_element_id and rec.fee_element_id.fee_structure_id != rec.fee_structure_id:
                rec.fee_element_id = False

    @api.onchange('fee_element_id')
    def _onchange_fee_element_id(self):
        for rec in self:
            if rec.fee_element_id and not rec.fee_structure_id:
                rec.fee_structure_id = rec.fee_element_id.fee_structure_id
            if rec.fee_element_id and not rec.base_amount:
                rec.base_amount = rec.fee_element_id.amount

    @api.constrains('fee_structure_id', 'fee_element_id', 'enrollment_id')
    def _check_fee_links(self):
        for rec in self:
            if rec.fee_element_id and rec.fee_structure_id and rec.fee_element_id.fee_structure_id != rec.fee_structure_id:
                raise ValidationError('Fee element must belong to the selected fee structure.')
            if rec.enrollment_id and rec.fee_structure_id and rec.enrollment_id.fee_structure_id and rec.enrollment_id.fee_structure_id != rec.fee_structure_id:
                raise ValidationError('Fee structure must match the enrollment fee structure.')

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._initialize_base_amount()
        records._recompute_amounts()
        return records

    def write(self, vals):
        res = super().write(vals)
        recompute_fields = {
            'enrollment_id', 'fee_structure_id', 'fee_element_id', 'base_amount', 'late_fee_applied', 'due_date'
        }
        if not self.env.context.get('skip_tori_fee_recompute') and recompute_fields.intersection(vals):
            self._recompute_amounts()
        return res

    def _initialize_base_amount(self):
        for rec in self.filtered(lambda slip: not slip.base_amount and not slip.base_amount == 0.0):
            if rec.fee_element_id:
                rec.base_amount = rec.fee_element_id.amount
            else:
                rec.base_amount = rec.amount or 0.0

    def _recompute_amounts(self):
        for rec in self:
            base_amount = rec.base_amount
            if base_amount is False:
                base_amount = (rec.amount or 0.0) - (rec.late_fee_applied or 0.0)
            base_amount = max(base_amount, 0.0)
            discount = 0.0
            if rec.enrollment_id:
                discount = rec.enrollment_id._get_applicable_scholarship_discount(
                    rec.fee_element_id,
                    base_amount,
                    rec.due_date or fields.Date.today(),
                )
            net_amount = max(base_amount - discount, 0.0) + (rec.late_fee_applied or 0.0)
            update_vals = {}
            if rec.base_amount != base_amount:
                update_vals['base_amount'] = base_amount
            if rec.scholarship_discount != discount:
                update_vals['scholarship_discount'] = discount
            if rec.amount != net_amount:
                update_vals['amount'] = net_amount
            if update_vals:
                rec.with_context(skip_tori_fee_recompute=True).write(update_vals)

    def _prepare_invoice_line_vals(self):
        self.ensure_one()
        element = self.fee_element_id
        line_vals = {
            'name': element.name or self.fee_structure_id.name or self.enrollment_id.name,
            'quantity': 1.0,
            'price_unit': self.amount,
        }
        if element.income_account_id:
            line_vals['account_id'] = element.income_account_id.id
        if element.tax_ids:
            line_vals['tax_ids'] = [(6, 0, element.tax_ids.ids)]
        return line_vals

    def action_send(self):
        self.write({'state': 'sent'})

    def action_mark_paid(self):
        self.write({'state': 'paid', 'paid_date': fields.Date.today()})

    def action_create_invoice(self):
        for rec in self:
            if rec.invoice_id:
                continue
            rec._recompute_amounts()
            if rec.amount <= 0:
                raise ValidationError('Cannot create an invoice with zero or negative amount.')
            partner = rec.enrollment_id.parent_id or rec.enrollment_id.student_id
            journal = rec.fee_structure_id.sale_journal_id or self.env['account.journal'].search([
                ('type', '=', 'sale'),
                ('company_id', '=', rec.company_id.id),
            ], limit=1)
            if not journal:
                raise ValidationError('Please configure a sales journal for the company or fee structure before invoicing.')
            invoice_vals = {
                'move_type': 'out_invoice',
                'partner_id': partner.id,
                'invoice_date': fields.Date.today(),
                'invoice_line_ids': [(0, 0, rec._prepare_invoice_line_vals())],
                'journal_id': journal.id,
                'company_id': rec.company_id.id,
                'tori_fee_slip_id': rec.id,
                'invoice_origin': rec.display_name,
                'ref': 'Fee Slip %s' % rec.display_name,
            }
            invoice = self.env['account.move'].with_company(rec.company_id).create(invoice_vals)
            rec.write({'invoice_id': invoice.id, 'state': 'sent'})

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
                    values['late_fee_applied'] = element.late_fee_amount
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
                    'base_amount': enrollment._get_prorated_amount(element.amount),
                    'due_date': today,
                })
                existing_keys.add(key)

        if create_vals:
            self.create(create_vals)


class ToriEnrollmentFeeHook(models.Model):
    _inherit = 'tori.enrollment'

    def _get_applicable_scholarship_discount(self, fee_element, base_amount, on_date):
        self.ensure_one()
        scholarships = self.scholarship_ids.filtered(
            lambda scholarship: scholarship.state in ('approved', 'paid') and scholarship._is_active_on(on_date)
        )
        discount = 0.0
        for scholarship in scholarships:
            if scholarship._applies_to_fee_element(fee_element):
                discount += scholarship._compute_discount(base_amount)
        return min(discount, max(base_amount, 0.0))

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
            existing_keys = set(
                slip_model.search([
                    ('enrollment_id', '=', rec.id),
                    ('state', 'in', ['draft', 'sent', 'overdue']),
                ]).mapped('fee_element_id').ids
            )
            for element in rec.fee_structure_id.fee_element_ids:
                if element.id in existing_keys:
                    continue
                amount = rec._get_prorated_amount(element.amount)
                slip_model.create({
                    'enrollment_id': rec.id,
                    'fee_structure_id': rec.fee_structure_id.id,
                    'fee_element_id': element.id,
                    'base_amount': amount,
                    'due_date': fields.Date.today(),
                })


class AccountMoveExtension(models.Model):
    """Sync invoice payment state back to linked fee slips."""
    _inherit = 'account.move'

    def _tori_sync_fee_slip_state(self):
        slip_model = self.env['tori.fee.slip']
        for move in self:
            slips = slip_model.search([('invoice_id', '=', move.id)])
            if not slips:
                continue
            if move.payment_state in ('paid', 'in_payment'):
                slips.filtered(lambda s: s.state != 'paid').write({'state': 'paid'})
            elif move.payment_state == 'not_paid' and move.state == 'posted':
                slips.filtered(lambda s: s.state == 'paid').write({'state': 'sent'})

    def write(self, vals):
        res = super().write(vals)
        if 'payment_state' in vals:
            self._tori_sync_fee_slip_state()
        return res

