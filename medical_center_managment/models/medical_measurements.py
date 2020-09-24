from odoo import api, fields, models, _
import json
from matplotlib.patches import Rectangle
import datetime
import matplotlib 
matplotlib.use('Agg')
import matplotlib.pyplot as plt, mpld3
from matplotlib.dates import (YEARLY, DateFormatter,
                              rrulewrapper, RRuleLocator, drange)
import matplotlib.dates as mdates
from matplotlib import cm
class MedicalExamination(models.Model):
    _name = "medical.examination"
    _description = "Medical Examination"
    name = fields.Char("Name", required = True, translate = True)
    measurement_ids = fields.Many2many('medical.measurements','examination_measurements_rel','exam_id','measurement_id', string = "Measurements")



class MedicalMeasureUoM(models.Model):
    _name = "medical.measurements.uom"
    _description = "Medical Measurements UoM"
    name = fields.Char('Name', required = True)


class MedicalMeasure(models.Model):
    _name = "medical.measurements"
    _inherit = ['mail.thread.cc', 'mail.activity.mixin']
    _description = "Medical Measurements"
    active = fields.Boolean(default = True)
    name = fields.Char('Name', required = True, translate = True)
    min_norm_value = fields.Float('Min. Normal')
    max_norm_value = fields.Float('Max. Normal')
    min_danger_value = fields.Float('Min. Danger')
    max_danger_value = fields.Float('Max. Danger')
    age_dependent = fields.Boolean('Age Dependent')
    notify_patient = fields.Boolean('Notify Patient')
    age_range_ids = fields.One2many('medical.measure.age','medical_measurement_id',string='Age Ranges')
    uom_id = fields.Many2one('medical.measurements.uom', string = "Unit of Measure")

class MedicalMeasureAge(models.Model):
    _name = "medical.measure.age"
    _description = "Medical Measurements Ranges"
    min_age = fields.Integer("From Age")
    max_age = fields.Integer("To Age")

    min_norm_value = fields.Float('Min')
    max_norm_value = fields.Float('Max')
    min_danger_value = fields.Float('Danger Min')
    max_danger_value = fields.Float('Danger Max')
    medical_measurement_id = fields.Many2one("medical.measurements", string = "Medical Measurement")

class MedicalMeasurePatient(models.Model):
    _name = "medical.patient.measure"
    patient_id = fields.Many2one('res.partner', string = 'Patient', domain = "[('partner_type','=','patient')]")
    measurement_id = fields.Many2one('medical.measurements', string = 'Measurement')
    scheduel_id = fields.Many2one('patient.medicals.scheduel', string = "Scheduel")
    value_ids = fields.One2many("patient.measure.value",'measure_id', string = "Values")
    graph_data = fields.Text(compute = "_compute_graph_data")
    mpld3_chart = fields.Text(string='Mpld3 Chart',compute='_compute_mpld3_chart')
    def action_new_value(self):

        return {
            'name': _('Add New Value'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'patient.measure.value',
            'target' : 'new',
            'context' : {
            'default_measure_id': self.id,
            'default_measure_moment': datetime.datetime.now(),

            }
        }

    def action_view_measurement(self):
        self.ensure_one()
        action = self.env.ref('medical_center_managment.patient_measurement_action_window').read()[0]

        action['context'] = {'default_active_id': self.id}
        action['views'] =  [(False, 'form')]
        action['res_id'] =  self.id
        return action


    def name_get(self):
        result = []
        for measure in self:
            name = measure.measurement_id.name + _(' For ') + measure.patient_id.name
            result.append((measure.id, name))
        return result
    def _compute_mpld3_chart(self):
        for rec in self:
            dates = []
            values = []

            dates_warning = []
            values_warning = []

            dates_danger = []
            values_danger = []

            dates_norm = []
            values_norm = []

            for value in rec.value_ids :
                    if value.is_warning : 
                        dates_warning.append(value.measure_moment)
                        values_warning.append(value.value)
                        dates.append(value.measure_moment)
                        values.append(value.value)
                    if value.is_danger : 
                        dates_danger.append(value.measure_moment)
                        values_danger.append(value.value)
                        dates.append(value.measure_moment)
                        values.append(value.value)                    
                    if not value.is_warning and not  value.is_danger : 
                        dates.append(value.measure_moment)
                        values.append(value.value)
                        dates_norm.append(value.measure_moment)
                        values_norm.append(value.value)                                               

            figure = plt.figure(figsize = (10,3))
            plt.plot_date(dates_norm,values_norm, color = 'green')
            plt.plot_date(dates_danger,values_danger, color = 'red')
            plt.plot_date(dates_warning,values_warning, color = 'yellow')
            plt.plot(dates,values, 'b--')
            # plt.plot(dates,[rec.measurement_id.min_norm_value]*len(dates),'y--',label = 'Min. Normal Value')
            # plt.plot(dates,[rec.measurement_id.max_norm_value]*len(dates),'y--',label = 'Max. Normal Value')
            # plt.plot(dates,[rec.measurement_id.max_danger_value]*len(dates),'r--',label = 'Max. Danger Value')
            # plt.plot(dates,[rec.measurement_id.min_danger_value]*len(dates),'r--',label = 'Min. Danger Value')
            # plt.plot([1, 2, 3, 4], [1, 4, 9, 16],'r',label = 'Line1')
            # plt.plot([1, 2, 3, 4], [1, 7, 11, 9],'b--',label = 'Line1')
            plt.ylabel(rec.measurement_id.name)
            plt.legend()

            rec.mpld3_chart = mpld3.fig_to_html(figure)
    @api.depends('value_ids')
    def _compute_graph_data(self) :
        for patient_measure in self:

            '''[{"values": [{"label": "23-29 Mar", "value": 0}}], "area": true, "title": "", "key": "Sales: Untaxed Total", "color": "#875A7B"}]
            '''
            '''
            [{'values': [{'label': '04-17 15:48', 'value': 123.0}], 'area': true, 'title': '', 'key': 'Sales: Untaxed Total', 'color': '#875A7B'}]

            '''
            data_list = []
            data_list_json = {}
            data = []
            data_json = {}
            for value in patient_measure.value_ids:
                data_json = {
                "label" :value.measure_moment.strftime('%m-%d %H:%M'),
                "value" : value.value,
                }
                data.append(data_json)
            special_data = {
            "value" : 124,
            "label" : "Hassan"
            }
            jsonp = {"values" : data, "type":"row", "area":True, "title" : "123","key": "1", "color": "#00A09D", "is_sample_data": False }
            data_list.append(jsonp)

            patient_measure.graph_data = json.dumps(data_list)
            print(data_list)

            '''[{"values": [{"label": "13-19 Apr", "value": 36558.5}], "area": true, "title": "", "key": "Sales: Untaxed Total", "color": "#875A7B"}]
            '''

            '''
            [{"values": [{"x": "17 Mar", "y": 8998.2, "name": "17 March 2020"}, {"x": "16 Apr", "y": 8998.2, "name": "16 April 2020"}], "title": "", "key": "Bank: Balance", "area": true, "color": "#875A7B", "is_sample_data": false}]
[{"values": [{"x": "17 Mar", "y": 8, "name": "17 March 2020"}, {"x": "22 Mar", "y": 8, "name": "22 March 2020"}, {"x": "27 Mar", "y": -5, "name": "27 March 2020"}, {"x": "1 Apr", "y": 14, "name": "1 April 2020"}, {"x": "6 Apr", "y": 5, "name": "6 April 2020"}, {"x": "11 Apr", "y": 1, "name": "11 April 2020"}], "title": "", "key": "Cash: Balance", "area": true, "color": "#875A7B", "is_sample_data": true}]
            '''
class MedicalMeasurePatientValue(models.Model):
    _name = "patient.measure.value"
    _order = 'measure_moment desc'
    measure_id = fields.Many2one("medical.patient.measure", strnig = "Medical Measurements")
    measure_moment = fields.Datetime(string = "Moment")
    value = fields.Float("Value")
    is_danger = fields.Boolean(compute = "_compute_state")
    is_warning = fields.Boolean(compute = "_compute_state")
    @api.depends('value')
    def _compute_state(self):
        for rec in self :
            measurement = rec.measure_id.measurement_id
            if not measurement.age_dependent :
                rec.is_danger = (rec.value < measurement.min_danger_value or rec.value > measurement.max_danger_value)
                rec.is_warning = (rec.value < measurement.min_norm_value or rec.value > measurement.max_norm_value) and not rec.is_danger