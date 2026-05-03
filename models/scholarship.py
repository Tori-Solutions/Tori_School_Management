from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ToriScholarship(models.Model):
    _name = 'tori.scholarship'
    _description = 'Scholarship'

    enrollment_id = fields.Many2one('tori.enrollment', required=True)
    name = fields.Char()
    currency_id = fields.Many2one(
        'res.currency',
        related='enrollment_id.company_id.currency_id',
        store=True, readonly=True,
    )
    discount_type = fields.Selection(
        [('fixed', 'Fixed Amount'), ('percent', 'Percentage')],
        default='fixed',
        required=True,
    )
    percent_discount = fields.Float()
    amount = fields.Monetary(currency_field='currency_id')
    apply_scope = fields.Selection(
        [('all', 'All Fee Elements'), ('selected', 'Selected Fee Elements')],
        default='all',
        required=True,
    )
    fee_element_ids = fields.Many2many('tori.fee.element', string='Applicable Fee Elements')
    start_date = fields.Date()
    end_date = fields.Date()
    state = fields.Selection(
        [('draft', 'Draft'), ('approved', 'Approved'), ('paid', 'Paid')],
        default='draft',
    )
    vendor_bill_id = fields.Many2one('account.move', ondelete='restrict', index=True)
    company_id = fields.Many2one(related='enrollment_id.company_id', store=True, readonly=True)

    @api.constrains('discount_type', 'amount', 'percent_discount', 'start_date', 'end_date')
    def _check_discount_fields(self):
        for rec in self:
            if rec.discount_type == 'fixed' and rec.amount < 0:
                raise ValidationError('Fixed scholarship amount cannot be negative.')
            if rec.discount_type == 'percent' and (rec.percent_discount < 0 or rec.percent_discount > 100):
                raise ValidationError('Scholarship percentage must be between 0 and 100.')
            if rec.start_date and rec.end_date and rec.end_date < rec.start_date:
                raise ValidationError('Scholarship end date cannot be before start date.')

    def _is_active_on(self, on_date):
        self.ensure_one()
        effective_date = on_date or fields.Date.today()
        if self.start_date and effective_date < self.start_date:
            return False
        if self.end_date and effective_date > self.end_date:
            return False
        return True

    def _applies_to_fee_element(self, fee_element):
        self.ensure_one()
        if self.apply_scope == 'all':
            return True
        return bool(fee_element and fee_element in self.fee_element_ids)

    def _compute_discount(self, base_amount):
        self.ensure_one()
        if base_amount <= 0:
            return 0.0
        if self.discount_type == 'percent':
            return base_amount * (self.percent_discount / 100.0)
        return min(self.amount, base_amount)

    def _refresh_related_fee_slips(self):
        slip_model = self.env['tori.fee.slip']
        for rec in self:
            slips = slip_model.search([
                ('enrollment_id', '=', rec.enrollment_id.id),
                ('state', 'in', ['draft', 'sent', 'overdue']),
                ('invoice_id', '=', False),
            ])
            slips._recompute_amounts()

    def action_approve(self):
        for rec in self:
            rec.state = 'approved'
        self._refresh_related_fee_slips()

    def action_mark_paid(self):
        self.write({'state': 'paid'})

    def write(self, vals):
        res = super().write(vals)
        if {'state', 'discount_type', 'amount', 'percent_discount', 'apply_scope', 'fee_element_ids', 'start_date', 'end_date'}.intersection(vals):
            self._refresh_related_fee_slips()
        return res

    def unlink(self):
        enrollment_ids = self.mapped('enrollment_id').ids
        res = super().unlink()
        if enrollment_ids:
            self.env['tori.fee.slip'].search([
                ('enrollment_id', 'in', enrollment_ids),
                ('state', 'in', ['draft', 'sent', 'overdue']),
                ('invoice_id', '=', False),
            ])._recompute_amounts()
        return res

