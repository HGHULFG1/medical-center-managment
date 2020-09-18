from odoo import models, fields, api, _
import pytz
import datetime
from math import modf
import logging
from odoo.addons.medical_center_managment.models.exceptions.custom_exceptions import InvalidMeeting
from pytz import timezone
_logger = logging.getLogger(__name__)

class DoctorStatus(models.Model):
	_name = "doctor.status"
	_description = "Doctor Status"
	_order = "name, id"
	name = fields.Char("Name", required = True, Translate = True)
	
class FieldStudy(models.Model):
	_name = "field.study"
	_description = "Field Study"
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
	name = fields.Char( compute = "_compute_name")
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
	hour_to = fields.Float(string='To', index=True,
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
	adress_id = fields.Many2one('res.partner', string = "Adress", required = True, domain = "[('partner_type','in',['hospital','center','clinic'])]")

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
	_inherit = ['mail.thread.cc', 'mail.activity.mixin']
	name = fields.Char("Name", required = True, Translate = True)
	level_ids = fields.Many2many('desease.level', 'desease_deasease_level_rel', string = 'Levels')
	doctor_speciality_id = fields.Many2one("doctor.speciality", string = "Doctor Speciality", help = "What speciality shoulf a doctor have to deal with this desease")
	color = fields.Integer('Color Index')
	contagious = fields.Boolean("Contagious?")
	description = fields.Text("Description")

class MedicalAssurance(models.Model):
	_name = "medical.assurance"
	_description = "Medical Assurance"
	name = fields.Char("Name", required = True, translate = True)
	active = fields.Boolean(default = True)

class ResPartner(models.Model):
	_inherit = "res.partner"
	same_name = fields.Boolean(default=False, compute = "_compute_same_name")
	partner_type = fields.Selection([("dr","Doctor"),("patient","Patient"),("hospital","Hospital"),("center","Medical Center"),("clinic","Clinic"),('insurance',"Insurance")], string = "Type")
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
	blood_type = fields.Selection([("a+","A+"),("a-","A-"),("b+","B+"),("b-","B-"),("o+","O+"),("o-","O-"),("ab+","AB+"),("ab-","AB-")], string = "Blood Type")
	date_last_donation = fields.Date("Last Donation Date")

	#doctor fields
	emergency_phone = fields.Char("Emergency Phone")
	patient_count = fields.Integer("Patients", compute = "_compute_patient_count")
	doctor_appiontment_ids = fields.One2many('doctor.appointment','doctor_id', string = "Appointments")
	doctor_appointment_count = fields.Integer('Appointments', compute = "_compute_doctor_appointment")
	meeting_product_id = fields.Many2one('product.product', string="Product For Meetings", help="This product will be used to generate invoices for meetings")
	
	# Patient fields
	contagious_disease = fields.Boolean("Contagious Diseases", compute="_compute_contagious")
	patient_appiontment_ids = fields.One2many('doctor.appointment','patient_id', string = "Appointments")
	patient_appointment_count = fields.Integer('Appointments', compute = "_compute_patient_appointment_count")
	disease_ids = fields.One2many('desease.level.doctor.partner','partner_id',string = "Deseases")
	doctor_count = fields.Integer('Doctors', compute = "_compute_doctor_count")
	medical_ids = fields.One2many("patient.medical.scheduel.scheduel", "patient_id", string = "Medicals")
	medical_count = fields.Integer("Medicals", compute = "_compute_medical_count")
	timesheet_ids = fields.One2many("doctor.timesheet", "doctor_id", string = "Timesheet")
	smoker = fields.Boolean("Smoker")
	drinker = fields.Boolean("Drinker")
	measurement_ids = fields.One2many('medical.patient.measure','patient_id', string = 'Measurements')
	measurement_count = fields.Integer(compute = "_compute_measurement_count")
	height = fields.Float("Hieght (cm)")
	weight = fields.Float("Weight (kg)")
	#Please add these models, Todo 
	# job = fields.Many2one('partner.job', string = "Job")
	ibw = fields.Float("Ideal Body Weight", compute = "_compute_ibw", help = "Perfect body weight, depending on the calculation method you've specified in the settings")
	abw = fields.Float("Adjusted Body Weight", compute = "_compute_abw", help = "Perfect body weight, depending on the calculation method you've specified in the settings")
	# ABW = IBW + 0.4(actual weight - IBW)
	medical_assurance_id = fields.Many2one("res.partner",string = "Health Insurance", domain = "[('partner_type','=','insurance')]")
	# disability_ids = fields.Many2many('disability', 'disability_partner_rel','contact_id','disability_id',string = "Disabilities")
	# functions 
	# Please implement me, but before create system parameter refer to tasks, Todo
	@api.depends('disease_ids')
	def _compute_contagious(self) :
		for patient in self :
			contagious = False
			for disease in patient.disease_ids :
				if disease.contagious :
					contagious = True
			patient.contagious_disease = contagious

	@api.depends('gender','height')
	def _compute_ibw(self):
		gender_switcher = {'male':50,'female':45.5}
		for partner in self :
			if partner.gender and partner.partner_type == 'patient' :
				partner.ibw = (partner.height/30.48 - 5)*2.3*12 + gender_switcher.get(partner.gender)
			else :
				partner.ibw = 0.0

	@api.depends('ibw')
	def _compute_abw(self):
		for partner in self :

			if partner.weight > 1.3 * partner.ibw and  partner.gender and partner.partner_type == 'patient':
				partner.abw = partner.ibw + 0.4 * (partner.weight - partner.ibw)

			else :
				partner.abw = 0.0

	@api.depends('measurement_ids')
	def _compute_measurement_count(self) :
		for patient in self :
			patient.measurement_count = len(patient.measurement_ids.ids)

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
	def _validate_meeting(self, datetime_start, datetime_end, adress, meeting):
		'''raise InvalidMeeting if there is concurrency and the meeting is not availabe '''
		concurrent_meetings = self._compute_concurrency(datetime_start, datetime_end, adress)		
		if concurrent_meetings:
			availibilities = self._get_doctor_available_times(datetime_start.date(),datetime.time(hour=0, minute=0),datetime.time(hour=23, minute=59),[adress])
			raise InvalidMeeting(doctor=self,type="another_meeting", meeting=concurrent_meetings[0],valid_times=availibilities)
			return {'success': False}
			# except InvalidMeeting as e:
			# 	_logger.warning("dsd")
				# return {'warning': {'title': _('Invalid Meeting'), 'message': e.message}, 'success':False}
		else:
			return {'success': True}
	
	@api.model
	def _get_available_times(self, doctor_id, date, time_start, time_end, adress):
		return self.env["res.partner"].sudo().browse(doctor_id)._compute_concurrency(date, time_start, time_end, [adress])
	def _get_doctor_available_times(self, date, time_start, time_end, addresses):
		'''this function returns a list of periods splitted by doctor availibility'''
		availability = []
		for adress in addresses:
			timesheet = self._compute_current_timesheet(date, time_start, time_end, adress)
			if not timesheet:
				availability.append(
					{
						"address": adress.name,
						"availibility": {"name":f"The doctor {self.name} is not available in {adress.name}", "state":"not_available"},
						"date": date,
						"start_time": str(time_start),
						"end_time" : str(time_end)

					}
				)
				continue
			else:
				from_datetime = datetime.datetime.combine(date,time_start)
				to_datetime = datetime.datetime.combine(date,time_end)
				meetings = self._compute_concurrency(from_datetime.replace(hour=0, minute=0), to_datetime.replace(hour=23, minute=59), adress)
				start_time = datetime.time(hour=int(timesheet.hour_from), minute= int(modf(timesheet.hour_from)[0]*60))
				end_time = datetime.time(hour=int(timesheet.hour_to), minute= int(modf(timesheet.hour_to)[0]*60))
				current_time = start_time
				if not meetings:
					availability.append(
						{
						"address": adress.name,
						"availibility": {"name":f"The doctor {self.name} is available in {adress.name} from {start_time} till {end_time}","state":"available"},
						"date": date,
						"start_time": str(time_start),
						"end_time" : str(time_end)
						}
					)
					continue
				availability_details = []
				for index, meeting in enumerate(meetings):
					tz = timezone(self.env.user.tz)
					start_date_meeting = pytz.utc.localize(meeting.start_date).astimezone(tz)
					end_date_meeting = pytz.utc.localize(meeting.end_date).astimezone(tz)
					if start_date_meeting.time() > current_time:
						availability.append(
							{
							"address": adress.name,
							"availibility": {"name":f"The doctor {self.name} is available in {adress.name} from {current_time} till {start_date_meeting.time()}","state":"available"},
							"date": date,
							"start_time": str(current_time),
							"end_time" : str(start_date_meeting.time())
							}
						)
						availability.append(
							{
							"address": adress.name,
							"availibility": {"name":f"The doctor {self.name} is not available in {adress.name} from {current_time} till {end_date_meeting.time()}","state":"not_available"},
							"date": date,
							"start_time": str(start_date_meeting.time()),
							"end_time" : str(end_date_meeting.time())
							}
						)
						current_time = end_date_meeting.time()

					if start_date_meeting.time() == current_time:
						availability.append(
							{
							"address": adress.name,
							"availibility": {"name":f"The doctor {self.name} is not available in {adress.name} from {current_time} till {end_date_meeting.time()}","state":"not_available"},
							"date": date,
							"start_time": str(start_date_meeting.time()),
							"end_time" : str(end_date_meeting.time())
							}
						)
						current_time = end_date_meeting.time()


				if current_time < end_time:
						availability.append(
							{
							"address": adress.name,
							"availibility": {"name":f"The doctor {self.name} is available in {current_time} from {end_time} till {end_date_meeting.time()}","state":"available"},
							"date": date,
							"start_time": str(current_time),
							"end_time" : str(end_time)
							}
						)
				return availability
	def _compute_concurrency(self, from_datetime, to_datetime, addresse):
		'''this function returns a list of concurrent meetings, that will happen at concurrent times'''
		# appoints_ids = self
		appointment_ids = self.with_context(tz=self.env.user.tz, lang=self.env.user.lang).doctor_appiontment_ids
		concurrent_meetings = list(filter(lambda meeting:
		meeting.state not in ['draft', 'done','cancel']
		and
		meeting.start_date >= from_datetime
		and
		meeting.start_date <= to_datetime
		and
		meeting.address_id.id == addresse.id,
		appointment_ids
		))
		return sorted(concurrent_meetings, key=lambda x: x.start_date, reverse=False)

	def _compute_current_timesheet(self, date, time_form, time_to, address):
		'''this function compute the timesheet that should be used in order to validate a meeting
		the retrun value is an object of type 'doctor.timesheet' or False
		'''
		timesheet_ids = self.with_context(tz=self.env.user.tz, lang=self.env.user.lang).timesheet_ids
		weekday = date.weekday()
		current_timesheet = False
		current_date_from = datetime.datetime.min


		# start_datetime = datetime.datetime.combine(start_date, start_time)
		valid_timesheets = list(
		filter(lambda time: time.dayofweek == str(weekday)
		and
		not time.date_from or (time.date_from and time.date_from >= date)
		and
		not time.date_to or (time.date_to and time.date_to <= date)
		and
		datetime.time(hour=int(time.hour_from), minute=int(modf(time.hour_from)[0] * 60)) >= time_form
		and
		datetime.time(hour=int(time.hour_to), minute=int(modf(time.hour_to)[0] * 60)) <= time_to
		and
		time.adress_id == address.id,
		timesheet_ids
		))
		if not valid_timesheets:
			return False
		# No we will check if there is an exception for the date
		for valid_time in valid_timesheets:
			if valid_time.date_from:
				if valid_time.date_from > current_date_from:
					current_date_from = valid_time.date_from
					current_timesheet = valid_time
		
		return current_timesheet or valid_timesheets[0]
# patient related functions
	def get_age(self):
		'''return the age of the partner in case date of birth specified
		else return 0
		'''
		born = self.birth_date
		if not born:
			return 0
		today = fields.Date.today()
		return today.year - born.year - ((today.month, today.day) < (born.month, born.day))
		
	def _check_age_medicals(self, medicament):
		'''ckeck if the medicament is suitable for the age of the patient
		'''
		age = self.get_age()
		if age:
			if age > medicament.maximum_age and medicament.maximum_age:
				return {"valid":False, "message":_(f"The patient is {age} years old, and {medicament.name} could not be taken for ages above {medicament.maximum_age}")}
			if age < medicament.minimum_age:
				return {"valid":False, "message":_(f"The patient is {age} years old, and {medicament.name} could not be taken for ages under {medicament.minimum_age}")}
						
		return {"valid": True}
		
	def _check_side_effects_medicaments(self, medicament):
		'''
		check if the medicament has side effect for that patient
		'''
		side_effects_ids = medicament.side_effect_ids
		if not side_effects_ids:
			return {"valid": True}
		data = []
		patient_diseases = self.disease_ids
		side_effects_could_affects_patient = list(filter(
			lambda side_effect:
			not side_effect.disease_id or side_effect.disease_id.id in side_effects_ids.ids
			, side_effects_ids
		))
		if side_effects_could_affects_patient:
			return {"valid":False, "data": [{"causing":side_effect.causing_disease_id.name, "caused_by":side_effect.disease_id.name or None} for side_effect in side_effects_could_affects_patient if side_effect.causing_disease_id.name]}
				