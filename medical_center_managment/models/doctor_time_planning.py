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
    doctor_id = fields.Many2one('res.partner', string = "Doctor", required = True, domain = "[('partner_type','=','dr')]")
    patient_id = fields.Many2one('res.partner', string = "Patient", required = True, domain = "[('partner_type','=','patient')]")
    address_id = fields.Many2one('res.partner', string = "Address", required = True, domain = "['|','|',('partner_type','=','clinic'),('partner_type','=','hospital'),('partner_type','=','center')]",tracking=True)
    prescription_ids = fields.One2many("doctor.prescription", 'appointment_id', string = "Prescriptions")
    prescription_count = fields.Integer("Prescription Count", compute = "_compute_prescription")
    @api.depends('prescription_ids')
    def _compute_prescription(self):
        for record in self :
            record.prescription_count = len(record.prescription_ids.ids)
    # Planned times
    start_date = fields.Datetime(string = "Start Date",tracking=True, required = True)
    end_date = fields.Datetime(string = "End Date",tracking=True)
    # Effective times
    effective_start_date = fields.Datetime(string = "Effectice Start Date",tracking=True)
    effective_end_date = fields.Datetime(string = "Effectice End Date",tracking=True)
    confirmation_date = fields.Datetime(string = "Confirmation Date", help = "The date the patient confirmed the presence. ")
    state = fields.Selection([("draft","To Approve"),("approved","Approved"),("confirm","Confirmed"),("progress","In Progress"),("done","Done"),("cancel","Canceled")], default = 'draft')
    description = fields.Text("Description")
    

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

    @api.onchange('state')
    @api.depends_context('meeting_error')
    def _onchange_state(self, error = False):
        pass


    def approve(self):
        valid = self.doctor_id._validate_meeting(self.start_date, self.end_date, self.address_id, self)
        if valid['success']:
            self.state = 'approved'

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
