from odoo import models, fields, api
class Partner(models.Model):
	_inherit = "res.company"
	center_type = fields.Selection([("clinic","Clinic"),("center","Medical Center"),("hospital","Hospital")], string = "Type")
	doctor_id = fields.Many2one("res.partner", string = "Doctor")