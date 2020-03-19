from odoo import models, fields, api


class DoctorStatus(models.Model):
	_name = "doctor.status"
	_description = "Doctor Speciality"
	_order = "name, id"
	name = fields.Char("Name", required = True, Translate = True)
	
class FieldStudy(models.Model):
	_name = "field.study"
	_description = "Doctor Speciality"
	_order = "name, id"
	name = fields.Char("Name", required = True, Translate = True)

class DoctorSpecialityTags(models.Model):
	_name = "speciality.tag"
	_description = "Doctor Speciality"
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
	
class Partner(models.Model):
	_inherit = "res.partner"
	partner_type = fields.Selection([("dr","Doctor"),("patient","Patient")], string = "Type")
	gender = fields.Selection([("male","Male"),("female","Female")])
	status = fields.Many2one("doctor.status", string = "Status")
	study_field_id = fields.Many2one("field.study", string = "Status")
	speciality_id = fields.Many2one("doctor.speciality", string = "Speciality")
	nationality = fields.Many2one("natioanlity", string = "Nationality")
	birth_date = fields.Date("Date of Birth")
	emergency_phone = fields.Char("Emergency Phone")
	years_of_experience = fields.Integer("Experience")
	monthes_of_experience = fields.Integer()
	medical_center_ids = fields.Many2many("res.company", "doctor_center_rel", string = "Medical Centers")
	clinic_ids = fields.One2many("res.company", "doctor_id" ,string = "Clinics")
	hospital_ids = fields.Many2many("res.company", "doctor_hospital_rel", string = "Clinics")


