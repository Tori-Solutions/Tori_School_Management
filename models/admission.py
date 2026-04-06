import re

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class ToriAdmissionEnquiry(models.Model):
    _name = 'tori.admission.enquiry'
    _description = 'Admission Enquiry'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(required=True, tracking=True)
    email = fields.Char()
    phone = fields.Char()
    class_id = fields.Many2one('tori.class')
    session_id = fields.Many2one('tori.session')
    state = fields.Selection(
        [('draft', 'New'), ('in_progress', 'In Progress'), ('done', 'Done'), ('cancel', 'Cancelled')],
        default='draft',
        tracking=True,
    )
    application_id = fields.Many2one('tori.student.application', readonly=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company, required=True)

    def action_create_application(self):
        self.ensure_one()
        application = self.env['tori.student.application'].create({
            'enquiry_id': self.id,
            'session_id': self.session_id.id,
            'class_id': self.class_id.id,
            'student_name': self.name,
            'email': self.email,
            'phone': self.phone,
            'company_id': self.company_id.id,
        })
        self.application_id = application.id
        self.state = 'in_progress'
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'tori.student.application',
            'res_id': application.id,
            'view_mode': 'form',
        }


class ToriStudentApplication(models.Model):
    _name = 'tori.student.application'
    _description = 'Student Application'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(default='New', readonly=True, copy=False)
    student_name = fields.Char(required=True)
    student_full_name_bn = fields.Char(string='Student Full Name (Bangla)')
    date_of_birth = fields.Date()
    birth_certificate_no = fields.Char()
    birth_certificate_attachment_id = fields.Many2one('ir.attachment')
    student_photo = fields.Binary(attachment=True)
    student_photo_filename = fields.Char()
    student_category = fields.Selection(
        [('learn', 'Learn'), ('regular', 'Regular')],
        default='learn',
    )
    nationality = fields.Char(default='Bangladeshi')
    blood_group = fields.Selection(
        [
            ('a+', 'A+'),
            ('a-', 'A-'),
            ('b+', 'B+'),
            ('b-', 'B-'),
            ('ab+', 'AB+'),
            ('ab-', 'AB-'),
            ('o+', 'O+'),
            ('o-', 'O-'),
        ]
    )
    gender = fields.Selection([('male', 'Male'), ('female', 'Female'), ('other', 'Other')])
    religion = fields.Selection(
        [('islam', 'Islam'), ('hindu', 'Hindu'), ('christian', 'Christian'), ('other', 'Other')]
    )
    transport_mode = fields.Selection(
        [('guardian_own', 'Guardian Own'), ('school_bus', 'School Bus')],
        default='guardian_own',
    )

    academic_year_id = fields.Many2one('tori.academic.year')
    class_roll = fields.Char()
    academic_version = fields.Selection(
        [('general', 'General'), ('madrasah', 'Madrasah'), ('english_medium', 'English Medium')],
        default='general',
    )
    group_stream = fields.Selection(
        [('general', 'General'), ('science', 'Science'), ('arts', 'Arts'), ('commerce', 'Commerce')],
        default='general',
    )
    shift = fields.Selection([('morning', 'Morning'), ('day', 'Day'), ('evening', 'Evening')])
    admission_date = fields.Date(default=fields.Date.context_today)
    previous_school_info = fields.Char()

    father_name = fields.Char()
    father_name_bn = fields.Char(string='Father Name (Bangla)')
    father_company = fields.Char()
    father_income = fields.Float()
    father_education = fields.Char()
    father_occupation = fields.Char()
    father_designation = fields.Char()
    father_phone = fields.Char()
    father_email = fields.Char()
    father_nid = fields.Char(string='Father NID')

    mother_name = fields.Char()
    mother_name_bn = fields.Char(string='Mother Name (Bangla)')
    mother_mobile = fields.Char()
    mother_education = fields.Char()
    mother_occupation = fields.Char()
    mother_designation = fields.Char()
    mother_company = fields.Char()

    guardian_name = fields.Char()
    guardian_email = fields.Char()
    guardian_phone = fields.Char()
    guardian_phone_normalized = fields.Char(readonly=True, copy=False, index=True)
    guardian_relationship = fields.Char()
    guardian_address = fields.Char()

    street = fields.Char()
    street2 = fields.Char()
    city = fields.Char()
    state_id = fields.Many2one('res.country.state', string='State/Division')
    zip = fields.Char()
    country_id = fields.Many2one('res.country', default=lambda self: self.env.ref('base.bd', raise_if_not_found=False))

    present_address = fields.Text()
    present_district = fields.Char(string='Present District (Text)')
    present_city = fields.Char(string='Present City/Thana (Text)')
    present_district_id = fields.Many2one('tori.bd.district', string='Present District')
    present_upazila_id = fields.Many2one('tori.bd.upazila', string='Present City/Thana')
    permanent_address = fields.Text()
    permanent_district = fields.Char(string='Permanent District (Text)')
    permanent_city = fields.Char(string='Permanent City/Thana (Text)')
    permanent_district_id = fields.Many2one('tori.bd.district', string='Permanent District')
    permanent_upazila_id = fields.Many2one('tori.bd.upazila', string='Permanent City/Thana')

    email = fields.Char()
    phone = fields.Char()
    enquiry_id = fields.Many2one('tori.admission.enquiry')
    session_id = fields.Many2one('tori.session', required=True)
    class_id = fields.Many2one('tori.class', required=True)
    section_id = fields.Many2one('tori.section')
    student_partner_id = fields.Many2one('res.partner')
    stage_id = fields.Many2one(
        'tori.application.stage',
        string='Stage',
        default=lambda self: self._default_stage_id(),
        tracking=True,
        index=True,
        copy=False,
        group_expand='_read_group_stage_ids',
    )
    state = fields.Selection(
        [('draft', 'Draft'), ('confirm', 'Confirmed'), ('enrolled', 'Enrolled'), ('cancel', 'Cancelled')],
        default='draft',
        tracking=True,
    )
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company, required=True)

    @api.model
    def _normalize_phone(self, phone):
        digits = re.sub(r'\D+', '', phone or '')
        if digits.startswith('880'):
            digits = digits[3:]
        if len(digits) == 10 and digits.startswith('1'):
            digits = '0%s' % digits
        if digits.startswith('01') and len(digits) > 11:
            digits = digits[-11:]
        return digits

    @api.model
    def _apply_derived_fields(self, vals):
        if 'guardian_phone' in vals and 'guardian_phone_normalized' not in vals:
            vals['guardian_phone_normalized'] = self._normalize_phone(vals.get('guardian_phone')) or False

        if vals.get('state_id') and not vals.get('country_id'):
            state = self.env['res.country.state'].browse(vals['state_id'])
            vals['country_id'] = state.country_id.id
        elif 'state_id' in vals and not vals.get('state_id'):
            if 'country_id' not in vals:
                vals['country_id'] = False

        if vals.get('present_district_id'):
            vals['present_district'] = self.env['tori.bd.district'].browse(vals['present_district_id']).name
        elif 'present_district_id' in vals and not vals.get('present_district_id'):
            vals['present_district'] = False

        if vals.get('present_upazila_id'):
            vals['present_city'] = self.env['tori.bd.upazila'].browse(vals['present_upazila_id']).name
        elif 'present_upazila_id' in vals and not vals.get('present_upazila_id'):
            vals['present_city'] = False

        if vals.get('permanent_district_id'):
            vals['permanent_district'] = self.env['tori.bd.district'].browse(vals['permanent_district_id']).name
        elif 'permanent_district_id' in vals and not vals.get('permanent_district_id'):
            vals['permanent_district'] = False

        if vals.get('permanent_upazila_id'):
            vals['permanent_city'] = self.env['tori.bd.upazila'].browse(vals['permanent_upazila_id']).name
        elif 'permanent_upazila_id' in vals and not vals.get('permanent_upazila_id'):
            vals['permanent_city'] = False

    @api.model
    def _default_stage_id(self):
        company_id = self.env.company.id
        stage = self.env['tori.application.stage'].search([
            ('code', '=', 'draft'),
            ('company_id', '=', company_id),
        ], order='sequence, id', limit=1)
        if not stage:
            stage = self.env['tori.application.stage'].search([
                ('code', '=', 'draft'),
            ], order='sequence, id', limit=1)
        return stage.id

    @api.model
    def _read_group_stage_ids(self, stages, domain, order=None):
        return self.env['tori.application.stage'].search([], order=order or 'sequence, id')

    @api.model
    def _get_stage_for_state(self, state_code, company_id=False):
        if not state_code:
            return self.env['tori.application.stage']

        Stage = self.env['tori.application.stage']
        if company_id:
            stage = Stage.search([
                ('code', '=', state_code),
                ('company_id', '=', company_id),
            ], order='sequence, id', limit=1)
            if stage:
                return stage

        return Stage.search([
            ('code', '=', state_code),
        ], order='sequence, id', limit=1)

    @api.model
    def _sync_state_stage_values(self, vals):
        if vals.get('stage_id'):
            stage = self.env['tori.application.stage'].browse(vals['stage_id'])
            vals['state'] = stage.code
            return

        state_code = vals.get('state')
        if state_code:
            stage = self._get_stage_for_state(state_code, vals.get('company_id'))
            if stage:
                vals['stage_id'] = stage.id

    @api.model
    def _backfill_stage_ids(self):
        records = self.search([('stage_id', '=', False)])
        for rec in records:
            stage = rec._get_stage_for_state(rec.state, rec.company_id.id)
            if stage:
                rec.stage_id = stage.id

    @api.model_create_multi
    def create(self, vals_list):
        seq = self.env['ir.sequence']
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = seq.next_by_code('tori.student.application') or 'APP-NEW'
            if not vals.get('student_name'):
                vals['student_name'] = 'Unnamed Student'
            if not vals.get('email'):
                vals['email'] = vals.get('guardian_email') or vals.get('father_email')
            if not vals.get('phone'):
                vals['phone'] = vals.get('guardian_phone') or vals.get('father_phone') or vals.get('mother_mobile')
            self._apply_derived_fields(vals)
            self._sync_state_stage_values(vals)
        return super().create(vals_list)

    def write(self, vals):
        previous_states = {rec.id: rec.state for rec in self}
        vals = dict(vals)
        self._apply_derived_fields(vals)
        self._sync_state_stage_values(vals)
        res = super().write(vals)

        # When users move the statusbar stage directly to Enrolled,
        # make sure enrollment/partner records are created as in action_enroll.
        if not self.env.context.get('skip_auto_enroll') and ('state' in vals or 'stage_id' in vals):
            moved_to_enrolled = self.filtered(
                lambda rec: previous_states.get(rec.id) != 'enrolled' and rec.state == 'enrolled'
            )
            if moved_to_enrolled:
                moved_to_enrolled._ensure_enrollment_records(set_enrolled_state=False)

        return res

    @api.constrains('present_district_id', 'present_upazila_id', 'permanent_district_id', 'permanent_upazila_id')
    def _check_upazila_belongs_to_district(self):
        for rec in self:
            if rec.present_upazila_id and rec.present_district_id and rec.present_upazila_id.district_id != rec.present_district_id:
                raise ValidationError('Present thana/upazila must belong to the selected present district.')
            if rec.permanent_upazila_id and rec.permanent_district_id and rec.permanent_upazila_id.district_id != rec.permanent_district_id:
                raise ValidationError('Permanent thana/upazila must belong to the selected permanent district.')

    @api.constrains('country_id', 'state_id')
    def _check_state_country_consistency(self):
        for rec in self:
            if rec.state_id and rec.country_id and rec.state_id.country_id != rec.country_id:
                raise ValidationError('State/Division must belong to the selected country.')

    @api.constrains('date_of_birth', 'guardian_phone_normalized', 'class_id', 'session_id', 'state')
    def _check_duplicate_application(self):
        for rec in self:
            if rec.state == 'cancel':
                continue
            if not (rec.date_of_birth and rec.guardian_phone_normalized and rec.class_id and rec.session_id):
                continue
            duplicate_domain = [
                ('id', '!=', rec.id),
                ('state', '!=', 'cancel'),
                ('date_of_birth', '=', rec.date_of_birth),
                ('guardian_phone_normalized', '=', rec.guardian_phone_normalized),
                ('class_id', '=', rec.class_id.id),
                ('session_id', '=', rec.session_id.id),
            ]
            if self.search_count(duplicate_domain):
                raise ValidationError(
                    'Duplicate application detected for the same date of birth, guardian phone, class and session.'
                )

    def action_confirm(self):
        self.write({'state': 'confirm'})

    def action_cancel(self):
        self.write({'state': 'cancel'})

    def _ensure_enrollment_records(self, set_enrolled_state=False):
        enrollment_model = self.env['tori.enrollment']
        for rec in self:
            with self.env.cr.savepoint():
                try:
                    partner = rec.student_partner_id
                    if not partner:
                        partner = self.env['res.partner'].create({
                            'name': rec.student_name,
                            'email': rec.email or rec.guardian_email or rec.father_email,
                            'phone': rec.phone or rec.guardian_phone or rec.father_phone or rec.mother_mobile,
                            'street': rec.street,
                            'street2': rec.street2,
                            'city': rec.city,
                            'state_id': rec.state_id.id,
                            'zip': rec.zip,
                            'country_id': rec.country_id.id,
                            'is_student': True,
                            'company_id': rec.company_id.id,
                            'barcode': rec.name,
                        })
                        rec.student_partner_id = partner.id

                    parent_name = rec.guardian_name or rec.father_name or rec.mother_name
                    parent_email = rec.guardian_email or rec.father_email
                    parent_phone = rec.guardian_phone or rec.father_phone or rec.mother_mobile
                    parent_partner = self.env['res.partner']
                    if parent_name:
                        domain = [('is_parent', '=', True)]
                        if parent_email:
                            domain = [('email', '=', parent_email)]
                        elif parent_phone:
                            domain = [('phone', '=', parent_phone)]
                        parent_partner = self.env['res.partner'].search(domain, limit=1)
                        if not parent_partner:
                            parent_partner = self.env['res.partner'].create({
                                'name': parent_name,
                                'email': parent_email,
                                'phone': parent_phone,
                                'is_parent': True,
                                'company_id': rec.company_id.id,
                            })

                    year = self.env['tori.academic.year'].search([
                        ('session_id', '=', rec.session_id.id)
                    ], limit=1)
                    academic_year = rec.academic_year_id or year
                    if not academic_year and rec.session_id:
                        academic_year = self.env['tori.academic.year'].create({
                            'title': rec.session_id.name,
                            'session_id': rec.session_id.id,
                            'start_date': rec.session_id.start_date,
                            'end_date': rec.session_id.end_date,
                        })

                    fee_structure = self.env['tori.fee.structure'].search([
                        ('class_id', '=', rec.class_id.id),
                        ('session_id', '=', rec.session_id.id),
                    ], limit=1)

                    enrollment_vals = {
                        'student_id': partner.id,
                        'session_id': rec.session_id.id,
                        'academic_year_id': academic_year.id,
                        'class_id': rec.class_id.id,
                        'section_id': rec.section_id.id,
                        'subject_ids': [(6, 0, rec.class_id.subject_ids.ids)],
                        'fee_structure_id': fee_structure.id,
                        'parent_id': parent_partner.id,
                        'company_id': rec.company_id.id,
                    }

                    enrollment = enrollment_model.search([
                        ('student_id', '=', partner.id),
                        ('session_id', '=', rec.session_id.id),
                        ('company_id', '=', rec.company_id.id),
                    ], limit=1)

                    if enrollment:
                        enrollment.write({
                            'academic_year_id': enrollment_vals['academic_year_id'],
                            'class_id': enrollment_vals['class_id'],
                            'section_id': enrollment_vals['section_id'],
                            'subject_ids': enrollment_vals['subject_ids'],
                            'fee_structure_id': enrollment_vals['fee_structure_id'],
                            'parent_id': enrollment_vals['parent_id'],
                        })
                    else:
                        enrollment = enrollment_model.create(enrollment_vals)

                    if enrollment.fee_structure_id and not enrollment.fee_slip_ids:
                        enrollment.action_generate_fee_slips()

                    if set_enrolled_state and rec.state != 'enrolled':
                        rec.with_context(skip_auto_enroll=True).write({'state': 'enrolled'})
                    if rec.enquiry_id:
                        rec.enquiry_id.state = 'done'
                    rec.message_post(body='Enrollment created: %s' % enrollment.display_name)
                except Exception as e:
                    raise UserError(
                        'Enrollment failed for %s: %s' % (rec.student_name, e)
                    ) from e

    def action_enroll(self):
        self._ensure_enrollment_records(set_enrolled_state=True)

