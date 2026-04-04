from odoo import fields, models


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
    amount = fields.Monetary(currency_field='currency_id')
    state = fields.Selection(
        [('draft', 'Draft'), ('approved', 'Approved'), ('paid', 'Paid')],
        default='draft',
    )
    vendor_bill_id = fields.Many2one('account.move', ondelete='restrict', index=True)
    company_id = fields.Many2one(related='enrollment_id.company_id', store=True, readonly=True)

    def action_approve(self):
        for rec in self:
            if not rec.vendor_bill_id:
                partner = rec.enrollment_id.student_id
                bill = self.env['account.move'].create({
                    'move_type': 'in_invoice',
                    'partner_id': partner.id,
                    'invoice_date': fields.Date.today(),
                    'invoice_line_ids': [(0, 0, {
                        'name': rec.name or 'Scholarship',
                        'quantity': 1.0,
                        'price_unit': rec.amount,
                    })],
                    'company_id': rec.company_id.id,
                })
                rec.vendor_bill_id = bill.id
            rec.state = 'approved'

    def action_mark_paid(self):
        self.write({'state': 'paid'})

