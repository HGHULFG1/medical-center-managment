from odoo import api, fields, models, _
import json
import matplotlib.pyplot as plt, mpld3
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
    min_norm_value = fields.Char('Min. Normal')
    max_norm_value = fields.Char('Max. Normal')
    min_danger_value = fields.Char('Min. Danger')
    max_danger_value = fields.Char('Max. Danger')
    age_dependent = fields.Boolean('Age Dependent')
    notify_patient = fields.Boolean('Notify Patient')
    age_range_ids = fields.One2many('medical.measure.age','medical_measurement_id',string='Age Ranges')
    uom_id = fields.Many2one('medical.measurements.uom', string = "Unit of Measure")

class MedicalMeasureAge(models.Model):
    _name = "medical.measure.age"
    _description = "Medical Measurements Ranges"
    min_age = fields.Integer("From Age")
    max_age = fields.Integer("To Age")

    min_norm_value = fields.Char('Min')
    max_norm_value = fields.Char('Max')
    min_danger_value = fields.Char('Danger Min')
    max_danger_value = fields.Char('Danger Max')
    medical_measurement_id = fields.Many2one("medical.measurements", string = "Medical Measurement")

class MedicalMeasurePatient(models.Model):
    _name = "medical.patient.measure"
    patient_id = fields.Many2one('res.partner', string = 'Patient', domain = "[('partner_type','=','patient')]")
    measurement_id = fields.Many2one('medical.measurements', string = 'Measurement')
    scheduel_id = fields.Many2one('patient.medicals.scheduel', string = "Scheduel")
    value_ids = fields.One2many("patient.measure.value",'measure_id', string = "Values")
    graph_data = fields.Text(compute = "_compute_graph_data")
    mpld3_chart = fields.Text(string='Mpld3 Chart',compute='_compute_mpld3_chart')
    def _compute_mpld3_chart(self):
        for rec in self:
            # Design your mpld3 figure:
            plt.scatter([1, 10], [5, 9])
            figure = plt.figure()
            plt.plot([1, 2, 3, 4], [1, 4, 9, 16],'r',label = 'Line1')
            plt.plot([1, 2, 3, 4], [1, 7, 11, 9],'b--',label = 'Line1')
            t = plt.xlabel('my data', fontsize=14, color='red')
            plt.ylabel('some numbers')
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
    measure_id = fields.Many2one("medical.patient.measure", strnig = "Medical Measurements")
    measure_moment = fields.Datetime(string = "Moment")
    value = fields.Float("Value")
