# -*- coding: utf-8 -*-
# from odoo import http


# class MedicalCenterManagment(http.Controller):
#     @http.route('/medical_center_managment/medical_center_managment/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/medical_center_managment/medical_center_managment/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('medical_center_managment.listing', {
#             'root': '/medical_center_managment/medical_center_managment',
#             'objects': http.request.env['medical_center_managment.medical_center_managment'].search([]),
#         })

#     @http.route('/medical_center_managment/medical_center_managment/objects/<model("medical_center_managment.medical_center_managment"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('medical_center_managment.object', {
#             'object': obj
#         })
