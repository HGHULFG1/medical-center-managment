# -*- coding: utf-8 -*-
from collections import defaultdict
import math
from datetime import datetime, time, timedelta
from dateutil.relativedelta import relativedelta
from dateutil.rrule import rrule, DAILY, WEEKLY
from functools import partial
from itertools import chain
from pytz import timezone, utc
from odoo import api, fields, models, _
from odoo.addons.base.models.res_partner import _tz_get
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression
from odoo.tools.float_utils import float_round
from odoo.tools import date_utils, float_utils

class DoctorAppointment(models.Model):
    _name = "doctor.appointment"
    _inherit = ['mail.thread.cc', 'mail.activity.mixin']
    _date_name = "start_date"
    _description = "Doctor Appointment"
    # Todo add name instead of name_get
    doctor_id = fields.Many2one('res.partner', string = "Doctor", required = True, domain = "[('partner_type','=','dr')]")
    patient_id = fields.Many2one('res.partner', string = "Patient", required = True, domain = "[('partner_type','=','patient')]")
    address_id = fields.Many2one('res.partner', string = "Address", required = True, domain = "['|','|',('partner_type','=','clinic'),('partner_type','=','hospital'),('partner_type','=','center')]",tracking=True)
    prescription_ids = fields.One2many("doctor.prescription", 'appointment_id', string = "Prescriptions",copy=False)
    prescription_count = fields.Integer("Prescription Count", compute = "_compute_prescription_count")
    
    @api.depends('prescription_ids')
    def _compute_prescription_count(self):
        for record in self :
            record.prescription_count = len(record.prescription_ids.ids)
    # Planned times
    start_date = fields.Datetime(string = "Start Date",tracking=True, required = True)
    end_date = fields.Datetime(string = "End Date",tracking=True,copy=False)
    # Effective times
    effective_start_date = fields.Datetime(string = "Effectice Start Date",tracking=True,copy=False)
    effective_end_date = fields.Datetime(string = "Effectice End Date",tracking=True,copy=False)
    confirmation_date = fields.Datetime(string = "Confirmation Date", help = "The date the patient confirmed the presence. ",copy=False)
    state = fields.Selection([("draft","To Approve"),("approved","Approved"),("confirm","Confirmed"),("progress","In Progress"),("done","Done"),("cancel","Canceled")], default = 'draft')
    description = fields.Text("Description")
    #Invoicing fields
    invoice_id = fields.Many2one('account.move', string='Invoice', copy=False)
    
    #TODO implement this function
    def constrains_doctor_timesheet(self):
        """
        This function will prevent creation of an appointment where the doctor is 
        not available in the specified address.
        """
        timesheets = self.doctor_id.timesheet_ids
        # valid_timesheets = list(filter(lambda time: time.address_id = self.address_id and ))

    def name_get(self):
        result = []
        for appointment in self:
            doctor_title =  appointment.doctor_id.title.name or '' 
            patient_title = appointment.patient_id.title.name or ''
            date = ''
            if appointment.start_date :
                date = appointment.start_date.strftime('%m/%d/%Y-%H:%M')
            name =  doctor_title + ' '  + appointment.doctor_id.name + ' ' + _('With') + ' ' + patient_title + appointment.patient_id.name + ' (' + date + ')'
            result.append((appointment.id, name))
        return result

    def approve(self):
        valid = self.doctor_id._validate_meeting(self.start_date, self.end_date, self.address_id, self)
        if valid['success']:
            self.state = 'approved'

    #Process actions
    def confirm(self):
        self.state = 'confirm'
    def cancel(self):
        self.state = 'cancel'
    def start(self):
        self.state = 'progress'
    def done(self):
        self.state = 'done'

    def action_prescription(self):

        return {
            'name': _('Add Prescription To Appointment'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'doctor.prescription',
            'target' : 'new',
            'context' : {'default_patient_id': self.patient_id.id,'default_doctor_id': self.doctor_id.id, 'default_appointment_id': self.id }
        }
    
    #create invoice
    def create_invoice(self):
        '''use the product defined at the doctor level to create an invoice, where 
        the customer is the patient
        '''
        product_id = self.doctor_id.meeting_product_id
        if product_id:
            self.invoice_id = self.env["account.move"].create(
                {   
                    "type": "out_invoice",
                    "partner_id": self.patient_id.id,
                    "invoice_line_ids": [(0,0,{
                        "product_id": product_id.id,
                        "quantity": 1,
                        "price_unit": product_id.list_price
                    }

                    )]
                }
            ).id
    


    def action_appointment_sent(self):
        """ Open a window to compose an email, with the edi invoice template
            message loaded by default
        """
        self.ensure_one()
        template = self.env.ref('medical_center_managment.email_template_edi_medical_appointment', raise_if_not_found=False)
        lang = self.patient_id.lang
        if template and template.lang:
            lang = template._render_template(template.lang, 'doctor.appointment', self.id)
        compose_form = self.env.ref('medical_center_managment.medical_email_send_wizard_form', raise_if_not_found=False)
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


    def _send_email(self):
        if self.patient_id.email:
            self.composer_id.send_mail()
    def send_and_print_action(self):
        self.ensure_one()
        # Send the mails in the correct language by splitting the ids per lang.
        # This should ideally be fixed in mail_compose_message, so when a fix is made there this whole commit should be reverted.
        # basically self.body (which could be manually edited) extracts self.template_id,
        # which is then not translated for each customer.
        if self.composition_mode == 'mass_mail' and self.template_id:
            active_ids = self.env.context.get('active_ids', self.res_id)
            active_records = self.env[self.model].browse(active_ids)
            langs = active_records.mapped('partner_id.lang')
            default_lang = self.env.user_id.lang
            for lang in (set(langs) or [default_lang]):
                active_ids_lang = active_records.filtered(lambda r: r.partner_id.lang == lang).ids
                self_lang = self.with_context(active_ids=active_ids_lang, lang=lang)
                self_lang.onchange_template_id()
                self_lang._send_email()
        else:
            self._send_email()
        # if self.is_print:
        #     return self._print_document()
        # return {'type': 'ir.actions.act_window_close'}