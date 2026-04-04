import base64
import logging
import mimetypes
import time
from collections import defaultdict
from threading import Lock

from odoo import fields, http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal

_logger = logging.getLogger(__name__)

ALLOWED_PHOTO_MIME_TYPES = {'image/jpeg', 'image/png', 'image/gif', 'image/webp'}

# ---------------------------------------------------------------------------
# B3: In-process rate limiter for public admission form
# For multi-worker production, replace with PostgreSQL or Redis counters.
# ---------------------------------------------------------------------------
_rate_limit_store = defaultdict(list)
_rate_limit_lock = Lock()
RATE_LIMIT_MAX = 5          # max submissions
RATE_LIMIT_WINDOW = 3600    # per hour (seconds)


def _is_rate_limited(ip: str) -> bool:
    now = time.time()
    with _rate_limit_lock:
        timestamps = _rate_limit_store[ip]
        _rate_limit_store[ip] = [t for t in timestamps if now - t < RATE_LIMIT_WINDOW]
        if len(_rate_limit_store[ip]) >= RATE_LIMIT_MAX:
            return True
        _rate_limit_store[ip].append(now)
        return False


class ToriSchoolPortal(CustomerPortal):
    def _get_allowed_enrollments(self):
        user = request.env.user
        partner = user.partner_id
        Enrollment = request.env['tori.enrollment'].sudo()

        student_enrollments = Enrollment.search([('student_id', '=', partner.id)])
        parent_enrollments = Enrollment.search([
            ('parent_id', '=', partner.id),
            ('portal_access_granted', '=', True),
        ])
        return (student_enrollments | parent_enrollments)

    @http.route('/my/dashboard', type='http', auth='user', website=True)
    def my_dashboard(self, **kwargs):
        enrollments = self._get_allowed_enrollments()
        
        # Calculate stats for the first enrollment (if multiple exist, usually we'd aggregate or let user pick, but for now take the first)
        enrollment = enrollments and enrollments[0] or request.env['tori.enrollment']
        student_name = enrollment.student_id.name if enrollment else request.env.user.name
        class_name = enrollment.class_id.name if enrollment else 'Not Assigned'
        session_name = enrollment.session_id.name if enrollment else '-'
        
        attendance_records = request.env['tori.student.attendance'].sudo().search([('enrollment_id', 'in', enrollments.ids)])
        attendance_pct = round((len(attendance_records.filtered(lambda r: r.status == 'present')) / len(attendance_records)) * 100) if attendance_records else 0
        
        current_gpa = "N/A"
        if enrollment:
            marks = request.env['tori.marksheet'].sudo().search([('enrollment_id', '=', enrollment.id)], limit=1, order='create_date desc')
            if marks: current_gpa = str(marks.gpa)
            
        pending_assignments = request.env['tori.assignment'].sudo().search_count([
            ('class_id', 'in', enrollments.mapped('class_id').ids)
        ])
        
        overdue_fees_count = request.env['tori.fee.slip'].sudo().search_count([
            ('enrollment_id', 'in', enrollments.ids),
            ('state', '=', 'overdue')
        ])

        import datetime
        today_date = datetime.date.today()
        weekday = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'][today_date.weekday()]
        
        slots = request.env['tori.timetable.slot'].sudo().search([
            ('class_id', 'in', enrollments.mapped('class_id').ids),
            ('day', '=', weekday),
        ])
        
        today_slots = []
        for slot in slots:
            sh, sm = divmod(slot.start_time * 60, 60)
            eh, em = divmod(slot.end_time * 60, 60)
            time_str = f"{int(sh):02d}:{int(sm):02d} - {int(eh):02d}:{int(em):02d}"
            today_slots.append({
                'time': time_str,
                'subject': slot.subject_id.name,
                'teacher': slot.teacher_id.name,
                'room': slot.room_id.name or 'TBA'
            })
            
        announcements_records = request.env['tori.announcement'].sudo().search([
            ('date', '=', today_date)
        ], limit=5, order='create_date desc')
        
        announcements = [{'title': a.title, 'body': a.body} for a in announcements_records]

        values = {
            'page_name': 'dashboard',
            'enrollments': enrollments,
            'student_name': student_name,
            'class_name': class_name,
            'session_name': session_name,
            'attendance_pct': attendance_pct,
            'current_gpa': current_gpa,
            'pending_assignments': pending_assignments,
            'overdue_fees': overdue_fees_count,
            'today_slots': today_slots,
            'announcements': announcements,
            
            # Keep old ones just in case
            'attendance_count': len(attendance_records),
            'assignment_count': pending_assignments,
            'fee_slip_count': request.env['tori.fee.slip'].sudo().search_count([
                ('enrollment_id', 'in', enrollments.ids)
            ]),
        }
        return request.render('tori_school_management.portal_dashboard', values)

    @http.route('/my/timetable', type='http', auth='user', website=True)
    def my_timetable(self, **kwargs):
        enrollments = self._get_allowed_enrollments()
        slots = request.env['tori.timetable.slot'].sudo().search([
            ('class_id', 'in', enrollments.mapped('class_id').ids)
        ])
        return request.render('tori_school_management.portal_timetable', {'slots': slots, 'page_name': 'timetable'})

    @http.route('/my/attendance', type='http', auth='user', website=True)
    def my_attendance(self, **kwargs):
        enrollments = self._get_allowed_enrollments()
        records = request.env['tori.student.attendance'].sudo().search([
            ('enrollment_id', 'in', enrollments.ids)
        ], order='date desc')
        return request.render('tori_school_management.portal_attendance', {'records': records, 'page_name': 'attendance'})

    @http.route('/my/assignments', type='http', auth='user', website=True)
    def my_assignments(self, **kwargs):
        enrollments = self._get_allowed_enrollments()
        assignments = request.env['tori.assignment'].sudo().search([
            ('class_id', 'in', enrollments.mapped('class_id').ids)
        ])
        submissions = request.env['tori.submission'].sudo().search([
            ('enrollment_id', 'in', enrollments.ids)
        ])
        return request.render(
            'tori_school_management.portal_assignments',
            {'assignments': assignments, 'submissions': submissions, 'page_name': 'assignments'},
        )

    @http.route('/my/assignments/submit/<int:assignment_id>/<int:enrollment_id>', type='http', auth='user', methods=['POST'], website=True, csrf=True)
    def submit_assignment(self, assignment_id, enrollment_id, **post):
        enrollments = self._get_allowed_enrollments()
        if enrollment_id not in enrollments.ids:
            return request.redirect('/my/assignments')
        request.env['tori.submission'].sudo().create({
            'assignment_id': assignment_id,
            'enrollment_id': enrollment_id,
            'submission_date': fields.Datetime.now(),
            'state': 'submitted',
        })
        return request.redirect('/my/assignments')

    @http.route('/my/grades', type='http', auth='user', website=True)
    def my_grades(self, **kwargs):
        enrollments = self._get_allowed_enrollments()
        marksheets = request.env['tori.marksheet'].sudo().search([
            ('enrollment_id', 'in', enrollments.ids)
        ])
        return request.render('tori_school_management.portal_grades', {'marksheets': marksheets, 'page_name': 'grades'})

    @http.route('/my/transcript', type='http', auth='user', website=True)
    def my_transcript(self, **kwargs):
        enrollments = self._get_allowed_enrollments()
        return request.render('tori_school_management.portal_transcript', {'enrollments': enrollments, 'page_name': 'transcript'})

    @http.route('/my/library', type='http', auth='user', website=True)
    def my_library(self, **kwargs):
        enrollments = self._get_allowed_enrollments()
        records = request.env['tori.book.issue'].sudo().search([
            ('student_id', 'in', enrollments.mapped('student_id').ids)
        ])
        return request.render('tori_school_management.portal_library', {'records': records, 'page_name': 'library'})

    @http.route('/my/transport', type='http', auth='user', website=True)
    def my_transport(self, **kwargs):
        enrollments = self._get_allowed_enrollments()
        records = request.env['tori.student.transport'].sudo().search([
            ('enrollment_id', 'in', enrollments.ids)
        ])
        return request.render('tori_school_management.portal_transport', {'records': records, 'page_name': 'transport'})

    @http.route('/my/announcements', type='http', auth='user', website=True)
    def my_announcements(self, **kwargs):
        announcements = request.env['tori.announcement'].sudo().search([], order='date desc')
        return request.render('tori_school_management.portal_announcements', {'announcements': announcements, 'page_name': 'announcements'})

    @http.route('/my/children', type='http', auth='user', website=True)
    def my_children(self, **kwargs):
        partner = request.env.user.partner_id
        children = request.env['tori.enrollment'].sudo().search([
            ('parent_id', '=', partner.id),
            ('portal_access_granted', '=', True),
        ])
        return request.render('tori_school_management.portal_children', {'children': children, 'page_name': 'children'})

    @http.route('/my/fees', type='http', auth='user', website=True)
    def my_fees(self, **kwargs):
        enrollments = self._get_allowed_enrollments()
        slips = request.env['tori.fee.slip'].sudo().search([
            ('enrollment_id', 'in', enrollments.ids)
        ], order='due_date desc')
        return request.render('tori_school_management.portal_fees', {'slips': slips, 'page_name': 'fees'})

    @http.route('/my/child/<int:enrollment_id>/dashboard', type='http', auth='user', website=True)
    def my_child_dashboard(self, enrollment_id, **kwargs):
        enrollments = self._get_allowed_enrollments()
        if enrollment_id not in enrollments.ids:
            return request.redirect('/my/children')
        enrollment = request.env['tori.enrollment'].sudo().browse(enrollment_id)
        return request.render('tori_school_management.portal_child_dashboard', {'enrollment': enrollment, 'page_name': 'children'})


class ToriSchoolPublic(http.Controller):
    def _to_int(self, value):
        return int(value) if value and str(value).isdigit() else False

    def _to_float(self, value):
        try:
            return float(value) if value not in (None, '') else 0.0
        except Exception:
            return 0.0

    def _to_date(self, value):
        if not value:
            return False
        try:
            return fields.Date.to_date(value)
        except Exception:
            return False

    def _is_honeypot_triggered(self, post):
        return bool((post.get('website') or '').strip())

    def _validate_upload_type(self, upload_file):
        content_type = (upload_file.mimetype or '').split(';', 1)[0].strip().lower()
        if not content_type:
            content_type = (mimetypes.guess_type(upload_file.filename or '')[0] or '').lower()
        return content_type in ALLOWED_PHOTO_MIME_TYPES

    @http.route('/admission/submit', type='http', auth='public', methods=['POST'], website=True, csrf=True)
    def admission_submit(self, **post):
        # Layer 1: Rate limiting by IP
        client_ip = request.httprequest.environ.get(
            'HTTP_X_FORWARDED_FOR', request.httprequest.remote_addr
        )
        if client_ip:
            client_ip = client_ip.split(',')[0].strip()
        if _is_rate_limited(client_ip):
            _logger.warning("Rate limit hit for IP: %s on /admission/submit", client_ip)
            return request.redirect('/admission?error=rate_limited')

        # Layer 2: Honeypot checks (original + new hidden field)
        if self._is_honeypot_triggered(post):
            return request.redirect('/admission?submitted=1')
        if post.get('website_url'):
            return request.redirect('/admission?submitted=1')

        first_name = (post.get('first_name') or '').strip()
        last_name = (post.get('last_name') or '').strip()
        student_name = ('%s %s' % (first_name, last_name)).strip() or first_name
        class_id = self._to_int(post.get('class_id'))
        session_id = self._to_int(post.get('session_id'))
        date_of_birth = self._to_date(post.get('date_of_birth'))
        guardian_phone = (post.get('guardian_phone') or '').strip()

        if not first_name or not class_id or not session_id or not date_of_birth or not guardian_phone:
            return request.redirect('/admission?error=missing_required')

        application_vals = {
            'student_name': student_name,
            'first_name': first_name,
            'last_name': last_name,
            'student_full_name_bn': (post.get('student_full_name_bn') or '').strip(),
            'student_category': (post.get('student_category') or 'learn').strip(),
            'date_of_birth': date_of_birth,
            'birth_certificate_no': (post.get('birth_certificate_no') or '').strip(),
            'nationality': (post.get('nationality') or '').strip() or 'Bangladeshi',
            'blood_group': (post.get('blood_group') or '').strip() or False,
            'gender': (post.get('gender') or '').strip() or False,
            'religion': (post.get('religion') or '').strip() or False,
            'transport_mode': (post.get('transport_mode') or 'guardian_own').strip(),
            'session_id': session_id,
            'class_id': class_id,
            'section_id': self._to_int(post.get('section_id')),
            'academic_year_id': self._to_int(post.get('academic_year_id')),
            'class_roll': (post.get('class_roll') or '').strip(),
            'academic_version': (post.get('academic_version') or 'general').strip(),
            'group_stream': (post.get('group_stream') or 'general').strip(),
            'shift': (post.get('shift') or '').strip() or False,
            'admission_date': self._to_date(post.get('admission_date')) or fields.Date.today(),
            'previous_school_info': (post.get('previous_school_info') or '').strip(),
            'father_name': (post.get('father_name') or '').strip(),
            'father_name_bn': (post.get('father_name_bn') or '').strip(),
            'father_company': (post.get('father_company') or '').strip(),
            'father_income': self._to_float(post.get('father_income')),
            'father_education': (post.get('father_education') or '').strip(),
            'father_occupation': (post.get('father_occupation') or '').strip(),
            'father_designation': (post.get('father_designation') or '').strip(),
            'father_phone': (post.get('father_phone') or '').strip(),
            'father_email': (post.get('father_email') or '').strip(),
            'father_nid': (post.get('father_nid') or '').strip(),
            'mother_name': (post.get('mother_name') or '').strip(),
            'mother_name_bn': (post.get('mother_name_bn') or '').strip(),
            'mother_mobile': (post.get('mother_mobile') or '').strip(),
            'mother_education': (post.get('mother_education') or '').strip(),
            'mother_occupation': (post.get('mother_occupation') or '').strip(),
            'mother_designation': (post.get('mother_designation') or '').strip(),
            'mother_company': (post.get('mother_company') or '').strip(),
            'guardian_name': (post.get('guardian_name') or '').strip(),
            'guardian_email': (post.get('guardian_email') or '').strip(),
            'guardian_phone': guardian_phone,
            'guardian_relationship': (post.get('guardian_relationship') or '').strip(),
            'guardian_address': (post.get('guardian_address') or '').strip(),
            'street': (post.get('street') or '').strip(),
            'street2': (post.get('street2') or '').strip(),
            'city': (post.get('city') or '').strip(),
            'state_id': self._to_int(post.get('state_id')),
            'zip': (post.get('zip') or '').strip(),
            'country_id': self._to_int(post.get('country_id')),
        }
        application_vals['email'] = application_vals['guardian_email'] or application_vals['father_email']
        application_vals['phone'] = application_vals['guardian_phone'] or application_vals['father_phone'] or application_vals['mother_mobile']

        application_model = request.env['tori.student.application'].sudo()
        application_vals['guardian_phone_normalized'] = (
            application_model._normalize_phone(application_vals.get('guardian_phone')) or False
        )

        if application_vals.get('date_of_birth') and application_vals.get('guardian_phone_normalized'):
            duplicate_domain = [
                ('state', '!=', 'cancel'),
                ('date_of_birth', '=', application_vals['date_of_birth']),
                ('guardian_phone_normalized', '=', application_vals['guardian_phone_normalized']),
                ('class_id', '=', application_vals['class_id']),
                ('session_id', '=', application_vals['session_id']),
            ]
            duplicate = application_model.search(duplicate_domain, limit=1, order='id desc')
            if duplicate:
                return request.redirect('/admission?error=duplicate_application&reference=%s' % duplicate.name)

        upload_vals = {}
        student_photo_file = request.httprequest.files.get('student_photo')
        if student_photo_file and student_photo_file.filename:
            if not self._validate_upload_type(student_photo_file):
                return request.redirect('/admission?error=invalid_file_type')
            student_photo_bytes = student_photo_file.read()
            if len(student_photo_bytes) > 2 * 1024 * 1024:
                return request.redirect('/admission?error=photo_too_large')
            upload_vals['student_photo'] = base64.b64encode(student_photo_bytes)
            upload_vals['student_photo_filename'] = student_photo_file.filename

        application = application_model.create(application_vals)
        if upload_vals:
            application.sudo().write(upload_vals)
        return request.redirect('/admission?submitted=1&reference=%s' % application.name)

    @http.route('/edu/application/status', type='http', auth='public', website=True)
    def application_status(self, **kwargs):
        app_ref = (kwargs.get('reference') or '').strip()
        guardian_phone = (kwargs.get('guardian_phone') or '').strip()
        application = request.env['tori.student.application']
        if app_ref and guardian_phone:
            normalized_phone = request.env['tori.student.application']._normalize_phone(guardian_phone)
            application = request.env['tori.student.application'].sudo().search([
                ('name', '=', app_ref),
                ('guardian_phone_normalized', '=', normalized_phone),
            ], limit=1)
        return request.render('tori_school_management.application_status_page', {
            'reference': app_ref,
            'guardian_phone': guardian_phone,
            'application': application,
        })

    @http.route('/edu/attendance/scan', type='jsonrpc', auth='user')
    def attendance_scan(self, barcode=None, method='barcode', **kwargs):
        if not (
            request.env.user.has_group('tori_school_management.group_education_admin')
            or request.env.user.has_group('tori_school_management.group_education_teacher')
        ):
            return {'success': False, 'message': 'You do not have permission to mark attendance'}

        partner = request.env['res.partner'].sudo().search([('barcode', '=', barcode), ('is_student', '=', True)], limit=1)
        if not partner:
            return {'success': False, 'message': 'Student not found'}
        enrollment = request.env['tori.enrollment'].sudo().search([
            ('student_id', '=', partner.id),
            ('state', '=', 'active'),
        ], limit=1)
        if not enrollment:
            return {'success': False, 'message': 'Enrollment not found'}

        today = fields.Date.today()
        weekday = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'][today.weekday()]
        now = fields.Datetime.now()
        current_time = now.hour + (now.minute / 60.0)
        slot = request.env['tori.timetable.slot'].sudo().search([
            ('class_id', '=', enrollment.class_id.id),
            ('day', '=', weekday),
            ('start_time', '<=', current_time),
            ('end_time', '>=', current_time),
        ], limit=1)

        existing = request.env['tori.student.attendance'].sudo().search([
            ('enrollment_id', '=', enrollment.id),
            ('date', '=', today),
            ('timetable_slot_id', '=', slot.id if slot else False),
        ], limit=1)
        if existing:
            return {'success': True, 'message': 'Attendance already marked'}

        request.env['tori.student.attendance'].sudo().create({
            'enrollment_id': enrollment.id,
            'date': today,
            'timetable_slot_id': slot.id,
            'status': 'present',
            'method': 'qr' if method == 'qr' else 'barcode',
            'marked_by': request.env.user.id,
        })
        return {'success': True, 'message': 'Attendance marked'}

