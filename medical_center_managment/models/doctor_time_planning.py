# -*- coding: utf-8 -*-
"""Add class appointment."""

from odoo import api, fields, models, _


class DoctorAppointment(models.Model):
    """Add model for appointments."""

    _name = "doctor.appointment"
    _inherit = ['mail.thread.cc', 'mail.activity.mixin']
    _date_name = "start_date"
    _description = "Doctor Appointment"
    doctor_id = fields.Many2one(
        'res.partner', string="Doctor", required=True, domain="[('partner_type','=','dr')]")
    patient_id = fields.Many2one('res.partner', string="Patient",
                                 required=True, domain="[('partner_type','=','patient')]")
    address_id = fields.Many2one('res.partner', string="Address", required=True,
                                 domain="['|','|',('partner_type','=','clinic'),('partner_type','=','hospital'),('partner_type','=','center')]", tracking=True)
    prescription_ids = fields.One2many(
        "doctor.prescription", 'appointment_id', string="Prescriptions", copy=False)
    prescription_count = fields.Integer(
        "Prescription Count", compute="_compute_prescription_count")

    @api.depends('prescription_ids')
    def _compute_prescription_count(self):
        """Compute the prescription count related to the meeting."""
        for record in self:
            record.prescription_count = len(record.prescription_ids.ids)
    # Planned times
    start_date = fields.Datetime(
        string="Start Date", tracking=True, required=True)
    end_date = fields.Datetime(string="End Date", tracking=True, copy=False)
    # Effective times
    effective_start_date = fields.Datetime(
        string="Effectice Start Date", tracking=True, copy=False)
    effective_end_date = fields.Datetime(
        string="Effectice End Date", tracking=True, copy=False)
    confirmation_date = fields.Datetime(
        string="Confirmation Date", help="The date the patient confirmed the presence. ", copy=False)
    state = fields.Selection([("draft", "To Approve"),
                              ("approved", "Approved"), ("confirm", "Confirmed"),
                              ("progress", "In Progress"), ("done", "Done"),
                              ("cancel", "Canceled")],
                             default='draft')
    description = fields.Text("Description")
    # Invoicing fields
    invoice_id = fields.Many2one('account.move', string='Invoice', copy=False)
    # TODO implement this function

    def constrains_doctor_timesheet(self):
        """Prevent creation of an appointment where the doctor is\
        not available in the specified address."""
        timesheets = self.doctor_id.timesheet_ids
        # valid_timesheets = list(filter(lambda time: time.address_id = self.address_id and ))

    def name_get(self):
        """Get the name of meetings."""
        result = []
        for appointment in self:
            doctor_title = appointment.doctor_id.title.name or ''
            patient_title = appointment.patient_id.title.name or ''
            date = ''
            if appointment.start_date:
                date = appointment.start_date.strftime('%m/%d/%Y-%H:%M')
            name = doctor_title + ' ' + appointment.doctor_id.name + ' ' + \
                _('With') + ' ' + patient_title + \
                appointment.patient_id.name + ' (' + date + ')'
            result.append((appointment.id, name))
        return result

    def approve(self):
        """Check the validation of the meeting, if valid then make the meeting as to done (state=approved)."""
        valid = self.doctor_id._validate_meeting(
            self.start_date, self.end_date, self.address_id, self)
        if valid['success']:
            self.state = 'approved'

    # Process actions
    def confirm(self):
        """Set state to confirm."""
        self.state = 'confirm'

    def cancel(self):
        """Cancel the meeting, set state to cancel."""
        self.state = 'cancel'

    def start(self):
        """Start the meeting, set state to start."""
        self.state = 'progress'

    def done(self):
        """Set meeting state as done."""
        self.state = 'done'

    def action_prescription(self):
        """Open a window to allow creation of prescription in the meeting."""
        return {
            'name': _('Add Prescription To Appointment'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'doctor.prescription',
            'target': 'new',
            'context': {'default_patient_id': self.patient_id.id, 'default_doctor_id': self.doctor_id.id, 'default_appointment_id': self.id}
        }

    # create invoice
    def create_invoice(self):
        """Use the product defined at the doctor level to create an invoice, where \
        the customer is the patient."""
        product_id = self.doctor_id.meeting_product_id
        if product_id:
            self.invoice_id = self.env["account.move"].create(
                {
                    "type": "out_invoice",
                    "partner_id": self.patient_id.id,
                    "invoice_line_ids": [(0, 0, {
                        "product_id": product_id.id,
                        "quantity": 1,
                        "price_unit": product_id.list_price
                    }

                    )]
                }
            ).id

    def action_appointment_sent(self):
        """Open a window to compose an email, with the edi invoice template\
            message loaded by default."""
        self.ensure_one()
        template = self.env.ref(
            'medical_center_managment.email_template_edi_medical_appointment', raise_if_not_found=False)
        lang = self.patient_id.lang
        if template and template.lang:
            lang = template._render_template(
                template.lang, 'doctor.appointment', self.ids)
        compose_form = self.env.ref(
            'medical_center_managment.medical_email_send_wizard_form', raise_if_not_found=False)
        ctx = dict(
            default_model='doctor.appointment',
            default_res_id=self.id,
            default_use_template=bool(template),
            default_template_id=template and template.id or False,
            default_composition_mode='comment',
            mark_invoice_as_sent=True,
            model_description=self.with_context(lang=lang)._name,
            force_email=True
        )
        return {
            'name': _('Send Appointment'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'medical.email.send',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'new',
            'context': ctx,
        }
