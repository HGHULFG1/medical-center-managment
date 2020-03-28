from odoo import models, fields, api


class DoctorStatus(models.Model):
	_name = "doctor.status"
	_description = "Doctor Status"
	_order = "name, id"
	name = fields.Char("Name", required = True, Translate = True)
	
class FieldStudy(models.Model):
	_name = "field.study"
	_description = "Doctor Speciality"
	_order = "name, id"
	name = fields.Char("Name", required = True, Translate = True)

class DoctorSpecialityTags(models.Model):
	_name = "speciality.tag"
	_description = "Speciality Tags"
	_order = "name, id"
	name = fields.Char("Name", required = True, Translate = True)
class DoctorSpeciality(models.Model):
	_name = "doctor.speciality"
	_description = "Doctor Speciality"
	_order = "name, id"
	name = fields.Char("Speciality", required = True, Translate = True)
	# surgery = fields.Boolean("Surgery")
	# children = fields.Boolean("Children Speciality")
	tag_ids = fields.Many2many("speciality.tag")
	doctor_ids = fields.One2many("res.partner", "speciality_id", domain = "[('partner_type','=','dr')]",string = "Doctors")
class DoctorTimesheet(models.Model):
	_name = "doctor.timesheet"
	_description = "Doctor Timesheet"
	name = fields.Char(required=True, compute = "_compute_name")
	doctor_id = fields.Many2one('res.partner')
	dayofweek = fields.Selection([
		('0', 'Monday'),
		('1', 'Tuesday'),
		('2', 'Wednesday'),
		('3', 'Thursday'),
		('4', 'Friday'),
		('5', 'Saturday'),
		('6', 'Sunday')
		], 'Day of Week', required=True, index=True, default='0')
	date_from = fields.Date(string='Start Date')
	date_to = fields.Date(string='End Date')
	hour_from = fields.Float(string='From',
		help="Start and End time of working.\n"
			 "A specific value of 24:00 is interpreted as 23:59:59.999999.")
	hour_to = fields.Float(string='To', required=True, index=True,
		help="Start and End time of working.\n"
			 "A specific value of 24:00 is interpreted as 23:59:59.999999.")
	day_period = fields.Selection([('morning', 'Morning'), ('afternoon', 'Afternoon')], required=True, default='morning')
	week_type = fields.Selection([
		('1', 'Odd week'),
		('0', 'Even week')
		], 'Week Even/Odd', default=False)
	display_type = fields.Selection([
		('line_section', "Section")], default=False, help="Technical field for UX purpose.")
	sequence = fields.Integer(default=10,
		help="Gives the sequence of this line when displaying the resource calendar.")
	adress_id = fields.Many2one('res.partner', string = "Adress", required = True)

	def _compute_name(self):
		for record in self :
			record.name = record.adress_id.name + '(' + record.dayofweek + ', ' + record.day_period + ')'
class DeseaseLevel(models.Model):
	_name = "desease.level"
	_description = "Levels of desseases"
	name = fields.Char("Name", required = True, Translate = True)
	checking_period_days = fields.Integer('Check With Patient Every')
	critical = fields.Boolean('Critical')


class DeseasseLevelPartner(models.Model) :
	_name = "desease.level.doctor.partner"
	partner_id = fields.Many2one('res.partner', string = 'Patient', required = True, domain = "[('partner_type','=','dr')]")
	desease_id = fields.Many2one('desease', string = 'Desease', required = True)
	level_id = fields.Many2one('desease.level', string = "Level")
	doctor_id = fields.Many2one("res.partner", required = True, string = "Doctor", domain = "[('partner_type','=','dr')]")
	_sql_constraints = [
		('deases_level_partner_unique', 'unique (partner_id,desease_id)', 'Duplication in diseases')
	] 
	@api.onchange('desease_id')
	def _onchange_desease(self):
		lst = self.desease_id.level_ids.ids
		return {'domain': {'level_id': [('id', 'in', lst)]}}

class Desease(models.Model):
	_name = "desease"
	_description = "Desease"
	name = fields.Char("Name", required = True, Translate = True)
	level_ids = fields.Many2many('desease.level', 'desease_deasease_level_rel', string = 'Levels')
	doctor_speciality_id = fields.Many2one("doctor.speciality", string = "Doctor Speciality", help = "What speciality shoulf a doctor have to deal with this desease")


class ResPartner(models.Model):
	_inherit = "res.partner"
	same_name = fields.Boolean(default=False, compute = "_compute_same_name")
	partner_type = fields.Selection([("dr","Doctor"),("patient","Patient"),("hospital","Hospital"),("center","Medical Center"),("clinic","Clinic")], string = "Type")
	gender = fields.Selection([("male","Male"),("female","Female")])
	status = fields.Many2one("doctor.status", string = "Status")
	study_field_id = fields.Many2one("field.study", string = "Study Field")
	speciality_id = fields.Many2one("doctor.speciality", string = "Speciality")
	nationality = fields.Many2one("natioanlity", string = "Nationality")
	birth_date = fields.Date("Date of Birth")
	years_of_experience = fields.Integer("Experience")
	monthes_of_experience = fields.Integer()
	medical_center_ids = fields.Many2many("res.partner", "doctor_center_rel","doctor_id","center_id", string = "Medical Centers", domain = "[('partner_type','=','center')]")
	dr_id = fields.Many2one("res.partner")
	clinic_ids = fields.One2many("res.partner", "dr_id" ,string = "Clinics", domain = "[('partner_type','=','clinic')]")
	hospital_ids = fields.Many2many("res.partner","doctor_hospital_rel", "doctor_id","hospital_id",  string = "Hospitals", domain = "[('partner_type','=','hospital')]")

	#doctor fields
	emergency_phone = fields.Char("Emergency Phone")
	patient_count = fields.Integer("Patients", compute = "_compute_patient_count")
	doctor_appiontment_ids = fields.One2many('doctor.appointment','doctor_id', string = "Appointments")
	doctor_appointment_count = fields.Integer('Appointments', compute = "_compute_doctor_appointment")
	# Patient fields
	patient_appiontment_ids = fields.One2many('doctor.appointment','patient_id', string = "Appointments")
	patient_appointment_count = fields.Integer('Appointments', compute = "_compute_patient_appointment_count")
	disease_ids = fields.One2many('desease.level.doctor.partner','partner_id',string = "Deseases")
	doctor_count = fields.Integer('Doctors', compute = "_compute_doctor_count")
	medical_ids = fields.One2many("patient.medical.scheduel.scheduel", "patient_id", string = "Medicals")
	medical_count = fields.Integer("Medicals", compute = "_compute_medical_count")
	
	timesheet_ids = fields.One2many("doctor.timesheet", "doctor_id", string = "Timesheet")
	# functions 
	
	@api.depends('patient_appiontment_ids')
	def _compute_patient_appointment_count(self):
		for record in self :
			if record.partner_type != 'patient' :
				record.patient_appointment_count = 0
			else :
				record.patient_appointment_count = len(record.patient_appiontment_ids.ids)

	@api.depends('doctor_appiontment_ids')
	def _compute_doctor_appointment(self):
		for record in self :
			if record.partner_type != 'dr' :
				record.doctor_appointment_count = 0
			else :
				record.doctor_appointment_count = len(record.doctor_appiontment_ids.ids)
	@api.depends('medical_ids')
	def _compute_medical_count(self):
		for record in self :
			if record.partner_type != 'patient' :
				record.medical_count = 0
			else :
				record.medical_count = len(record.medical_ids.ids)
	@api.depends('name')
	def _compute_same_name(self):
		for partner in self:
			# use _origin to deal with onchange()
			partner_id = partner._origin.id
			domain = [('name', '=', partner.name)]
			if partner_id:
				domain += [('id', '!=', partner_id)]
			partner.same_name = bool(partner.name) and self.env['res.partner'].search(domain, limit=1)

	def _compute_patient_count(self) :
		for record in self :
			if record.partner_type == 'patient' :
				record.patient_count = 0
			else :
				record.patient_count = len(self.env["desease.level.doctor.partner"].search([('doctor_id','=',record.id)]).ids)
	@api.depends('disease_ids')			
	def _compute_doctor_count(self) :
		for record in self:
			if record.partner_type == 'dr':
				record.doctor_count = 0
			else : 
				record.doctor_count = len(record.disease_ids.ids)

	
	def write(self, vals):
		for rec in self:
			if '' in vals :
				if vals['confirmation'] == '0' :
					vals['force_customer_signature'] = False
			if 'code' in vals :
				if vals['code'] == any(['0','3']) :
					if vals['code'] == '0' :
						vals['stock_validation'] = '0'
						vals['allow_price_change'] = False
						vals['allow_free_item'] = False
						vals['promotion'] = False
						vals['allow_shelf_count'] = False
						vals['suggestion'] = False
			if 'allow_shelf_count' in vals :
				if not vals["allow_shelf_count"] :
					vals['suggestion'] = False
					vals['minimum_value'] = 0


		return super(ResPartner, self).write(vals)