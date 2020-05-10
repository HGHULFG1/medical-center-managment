# -*- coding: utf-8 -*-
{
    'name': "Medical Center Managment",

    'summary': """
        This module allows doctors and/or medical center admins to manage their 
        tasks super easily.  """,

    'description': """

Description :
-------------

This module represents a unified suite of software designed for independent laboratories, medical, physical therapy and mental health.
The use of the software will automate many process for patients and doctors as well (surveys, measurments,... )
and give the patient and the doctor a very helpful dashboard to ease their tasks, also they will have beatiful and performant reports,
such as BI reports, medical reports, visit analysis reports.. and so on.

Freatures : 
-----------
1-Multi language:

Software will be translated into many languages

2-Remote reservation:

auto scheduling and timesheet, with custom notifications (inform patient if any delay occurs for example) 

3-Chating and video call (not confirmed yet)

4-Measurements: 

For example a doctor can schedule a sugar rate measurement for a sugar patient, to be measured six times a day (before and after each meal) , 
doctor can add thresholds and provide warning messages for them, for example : when sugar rate pass 160 "take insoline 50 unit/ml",
when sugar rate pass 220 "take insoline 60 unit/ml", when sugar pass 300 "go to hospital immediately"
so the app. will notify the patient to make the measurements and notify him for warnings if there is any.

5-Schedule medicals : 

For example a doctor add "Siofor 500mg" to a patient, and give it a schedule 3 times per day for duration of 3 monthes, 
so a notification will be shown on the patient mobile phone each time he needs to take "Siofor 500mg"
After these three months the doctor needs to do a revision so the software ask the patient to reserve an appointment.

Now suppose another doctor gives the patient a medical that will have a side effect with the "Siofor 500mg", 
or the patient needs to have a surgery and he must stop taking "Siofor 500mg", or for any other reason the patient should stop taking "Siofor 500mg",
the doctor will have a notification and will have the following options : 
    -update the period of "Siofore 500mg" taking
    -replace the "Siofore 500mg" with another medical, and another schedule
    -custom action


6-Map to navigate throw the clinic/medical center


7-Doctor profile: 

Patients could rate doctors(not confirmed yet), and put comments on them

8-Patient profile:

A doctor can track the info of his/her clients, with a user freindly interface,
for example in the patient profile the doctor can see the measurements, the visits, personel information,
 add tags to group patients with, add notes, and warnings to show when start a new visit, add warning on finishing a visit

9-Survey before an appointment:

For example a doctor needs to have the following informations before giving 
appointments for new patients, (or update infos for registered patients)

Name : For new patients (mandatory)
Prename : For new patients (mandatory)
Phone : For new patients 
Weight : For new and registered patients (mandatory)

So when a patient request an appointment he/she should fill the above informations

10- Appointment managment: 

A doctor can schedule activities in his/her appointment(take measurements ... )
and trak them easly during the appointment

11-Timesheet on visits:

A doctor can start the appointment with only one button click and finish it with one click also,
then the system will add the duration in the visit form.
(from 16:00 --> 16:30   duration 30 min
    """,

    'author': "Hassan Ghannoum",
    'website': "https://www.linkedin.com/in/hassan-ghannoum-4593a4127/",


    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Medical',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','mail','base_geolocalize'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/data.xml',
        'views/tree/partner.xml',
        'views/tree/medicals.xml',
        'views/map/partner.xml',
        'views/map/appointment.xml',
        'views/tree/patient_medical_scheduel.xml',
        'views/kanban/medicals.xml',
        'views/kanban/disease.xml',
        'views/kanban/measurement_patient.xml',
        'actions/window_actions/doctor_patient.xml',
        
        'actions/window_actions/patient_doctor.xml',
        'actions/window_actions/patient_medical.xml',
        'actions/window_actions/appointments.xml',
        'actions/window_actions/patient_measure.xml',
        'views/form/res_partner.xml', 
        'actions/window_actions/assurance.xml',
        'actions/window_actions/center.xml',
        'actions/window_actions/patient.xml',
        'actions/window_actions/hospital.xml',
        'actions/window_actions/prescription.xml',
        'actions/window_actions/disease.xml',

        'actions/window_actions/doctor_appointment.xml',
        'actions/window_actions/prescription_appointment.xml',
        'actions/window_actions/measurement.xml',
        'views/form/medicals.xml',
        'views/form/disease.xml',
        'views/form/patient_scheduel_medical.xml',
        'views/form/doctor_appointment.xml',
        'views/form/prescription.xml',
        'views/form/measurement.xml',
        'views/form/measurment_patient.xml',
        'views/tree/doctor_appointment.xml',
        'views/tree/disease.xml',
        'views/tree/doctor_timesheet.xml',
        'views/tree/prescription.xml',
        'views/tree/measurement.xml',
        'actions/window_actions/doctor.xml',
        'actions/window_actions/medicals.xml',
        'views/kanban/appointment.xml',
        'menuitems/menuis.xml',
        'views/templates.xml',
        'views/asset.xml',

        'data/speciality.xml',
        'data/doctor.xml',
        'data/medicine_titer.xml',
        'data/medicine.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'qweb': ["static/src/xml/template_time_picker.xml"],
}
