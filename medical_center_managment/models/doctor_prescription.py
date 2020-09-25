"""Add model prescription."""

from odoo import models, fields, api

class Prescriptions(models.Model):
	"""."""

	_name = "doctor.prescription"
	_description = "Doctor Prescriptions"
	_inherit = ['mail.thread.cc', 'mail.activity.mixin']

	appointment_id = fields.Many2one("doctor.appointment", string = "Appointment")
	patient_id = fields.Many2one("res.partner", domain = "[('partner_type','=','patient')]" , required = True, string = "Patient")
	doctor_id = fields.Many2one("res.partner", domain = "[('partner_type','=','dr')]", required = True, string = "Doctor")
	medical_schedueled_ids = fields.One2many("patient.medical.scheduel.scheduel","prescription_id", string ="Medicals")
	name = fields.Char('Name', required = True, placeholder = 'Prescription for sugar')

	def _default_patient_medicals(self):
		for rec in self :
			rec.patient_medical_ids = [(6,0,rec.patient_id.medical_ids.ids)]
	patient_medical_ids = fields.Many2many("patient.medical.scheduel.scheduel", string = "Patient Medicals", default = _default_patient_medicals)
	description = fields.Html("Description")


	def write(self,vals):
		"""Add the medications of the prescription to the patient."""
		for prescription in self :
			if 'medical_schedueled_ids' in vals:
				for medical in vals['medical_schedueled_ids']:
					medical[2]['doctor_id'] = prescription.doctor_id.id
					medical[2]['patient_id'] = prescription.patient_id.id
		return super(Prescriptions, self).write(vals)	
	@api.model
	def create(self, vals):
		"""Add the medications of the prescription to the patient."""
		if 'medical_schedueled_ids' in vals :
			for medical in vals['medical_schedueled_ids']:
				medical[2]['doctor_id'] = vals['doctor_id']
				medical[2]['patient_id'] = vals['patient_id']
		return super(Prescriptions, self).create(vals)

	
