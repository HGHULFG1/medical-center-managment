from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class SurgeryType(models.Model):
    _name = 'surgery.type'
    _description = 'Surgery Type'
    name = fields.Char(string='Name', translate=True, required=True)

class Surgery(models.Model):
    _name = 'surgery'
    _description = 'Surgery'
    surgery_type_id = fields.Many2one('surgery.type', string='Surgery', required=True)
    patient_id = fields.Many2one('res.partner', string="Patient", required=True)
    doctor_id = fields.Many2one('res.partner', string='Doctor', required=True)
    comment = fields.Text(string='Note')
    scheduled_date = fields.Datetime('Scheduled Date', required=True)
    name = fields.Char('Name', translate=True, compute="_compute_name")
    state = fields.Selection([('plan', 'Planned'), ('done', 'Done')],string='State')
    
    @api.depends('surgery_type_id','patient_id','doctor_id','scheduled_date')
    def _compute_name(self):
        for rec in self:
            rec.name = _(f"Surgery:{rec.surgery_type_id.name}, Doctor: {rec.doctor_id.name}, Patient: {rec.patient_id.name}")
    
    # prevent making a surgery done, if it is scheduled for future
    @api.constrains('state','scheduled_date')
    def _check_state_done_future(self):
        if self.scheduled_date>fields.datetime.today() and self.state=='done':
            raise ValidationError(_("Could not make a future surgery as done."))
    
    
    
    
    

    
