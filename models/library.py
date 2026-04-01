from odoo import api, fields, models


class ToriLibraryBook(models.Model):
    _name = 'tori.library.book'
    _description = 'Library Book'

    name = fields.Char(required=True)
    isbn = fields.Char()
    author = fields.Char()
    total_copies = fields.Integer(default=1)
    available_copies = fields.Integer(compute='_compute_available', store=True)
    issue_ids = fields.One2many('tori.book.issue', 'book_id')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company, required=True)

    @api.depends('total_copies', 'issue_ids.state')
    def _compute_available(self):
        for rec in self:
            issued = len(rec.issue_ids.filtered(lambda i: i.state == 'issued'))
            rec.available_copies = max(rec.total_copies - issued, 0)


class ToriBookIssue(models.Model):
    _name = 'tori.book.issue'
    _description = 'Book Issue'

    book_id = fields.Many2one('tori.library.book', required=True)
    student_id = fields.Many2one('res.partner', required=True)
    issued_by = fields.Many2one('res.users')
    issue_date = fields.Date(required=True)
    due_date = fields.Date(required=True)
    return_date = fields.Date()
    state = fields.Selection(
        [('issued', 'Issued'), ('returned', 'Returned'), ('overdue', 'Overdue')],
        default='issued',
    )
    barcode_method = fields.Boolean(default=False)
    company_id = fields.Many2one(related='book_id.company_id', store=True, readonly=True)

    def action_return(self):
        self.write({'state': 'returned', 'return_date': fields.Date.today()})

