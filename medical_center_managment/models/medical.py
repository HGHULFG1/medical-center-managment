from odoo import models, fields, api

class MedicalsTiters(models.Model):
	_name = "patient.medical.titer"
	_description = "Medicals Titers"
	name = fields.Char("Label")
	value = fields.Float("Value")
	color = fields.Integer('Color Index')


class Medicals(models.Model):
	_name = "patient.medicals"
	_description = "Medicals"
	_inherit = ['mail.thread.cc', 'mail.activity.mixin']
	name = fields.Char("Commercial Name", required = True)
	scientific_name = fields.Char("Scientific Name")
	side_effect_ids = fields.One2many("patient.medicals.side.effect", 'medical_id', string = "Side Effects")
	disease_ids = fields.Many2many('desease', 'desease_medical_rel','desease_id','medical_id', string = "Diseases")
	minimum_age = fields.Integer("Don't Take If Under")
	maximum_age = fields.Integer("Don't Take If Above")
	barcode = fields.Char('Barcode')
	code = fields.Char("Code")
	titer_ids = fields.Many2many("patient.medical.titer", string = "Titers")
	description = fields.Text("Description")
	
	
class MedicalSideEffect(models.Model):
	_name = "patient.medicals.side.effect"
	_description = "Medical Side Effect"
	medical_id = fields.Many2one('patient.medicals', string = "Medical")
	causing_disease_id = fields.Many2one('desease', string = "It causes")
	disease_id = fields.Many2one('desease', string = "In Case A Patient Has")
	description = fields.Char('Description', required = True)

class MedicalSchedule(models.Model):
	_name = "patient.medicals.scheduel"
	_description = "Medical Scheduel"
	name = fields.Char('Name')
	start_date = fields.Date("Start Date", required = True)
	start_end = fields.Date("Start End")
	schedule_line_ids = fields.One2many('patient.medicals.scheduel.line', 'scheduel_id', string = "Scheduels")

class MedicalScheduleLine(models.Model):
	_name = "patient.medicals.scheduel.line"
	_description = "Medical Schedule Line"	
	name = fields.Char("Name")
	description = fields.Char("Description")
	scheduel_id = fields.Many2one("patient.medicals.scheduel")
	scheduel_type = fields.Selection([("time","Time"),("activity","Activity")])
	scheduel_activity = fields.Selection([("before_breakfast","Before Breakfast"),("after_breakfast","After Breakfast")
		,("before_lunch","Before Lunch"),("after_lunch","After Lunch"),("before_dinner","Before Dinner")
		,("after_dinner","After Dinner")])
	quantity = fields.Float("Quantity")

class MedicalSchedulePatient(models.Model):

	_name = "patient.medical.scheduel.scheduel"
	patient_id = fields.Many2one("res.partner", string = "Patient", required = True, domain = "[('partner_type','=','patient')]")
	medical_id = fields.Many2one("patient.medicals", string = "Medical", required = True)
	scheduel_id = fields.Many2one("patient.medicals.scheduel", string = "Scheduel", required = True)
	schedule_appointment = fields.Many2one("doctor.appointment", string = "Schedueld In")
	appointment_id = fields.Many2one("doctor.appointment", string = "Schedueld Date", domain = "[('patient_id','=',patient_id),('doctor_id','=',doctor_id)]")
	doctor_id = fields.Many2one("res.partner", string = "Doctor", domain = "[('partner_type','=','dr')]")
	prescription_id = fields.Many2one("doctor.prescription", string = "Presciption")
	titer_id = fields.Many2one("patient.medical.titer", string = "Titer")

	@api.onchange("patient_id", "medical_id")
	def _validate_medicament_for_patient(self):
		valid = True
		if self.patient_id.id and self.medical_id.id:
			result = self.patient_id._check_age_medicals(self.medical_id)
			valid = result.get("valid")
		if not valid:
			self.env['bus.bus'].sendone(
					(self._cr.dbname, 'res.partner', self.env.user.partner_id.id),
					{'type': 'medicaments_age_invalid', 'message': result.get("message")})



	@api.onchange("medical_id")
	def _onchange_titer_domain(self):
		return {'domain': {'titer_id': [('id', 'in', self.medical_id.titer_ids.ids)]}}