
import functools
import logging
import json

import werkzeug.wrappers
from odoo import http
from odoo.addons.restful.common import (
    extract_arguments,
    invalid_response,
    valid_response,
)
from odoo.http import request
import datetime
import yaml
_logger = logging.getLogger(__name__)



def validate_token(func):
    """."""

    @functools.wraps(func)
    def wrap(self, *args, **kwargs):

        access_token = request.httprequest.headers.get("Accesstoken")

        if not access_token:
            return werkzeug.wrappers.Response(
                    content_type="application/json; charset=utf-8",
                    headers=[("Cache-Control", "no-store"), ("Pragma", "no-cache")],
                    response=json.dumps(
                        {
                            # "uid": uid,
                            # "user_context": request.session.get_context() if uid else {},
                            # "company_id": request.env.user.company_id.id if uid else None,
                            "Error" : "There is no token in your requst !!!",
                            "Message" : "The request is reject, no token found !",
                            "Success" : False,
                            "Value" : False,
                        }
                    ),
        )
        access_token_data = (
            request.env["api.access_token"]
            .sudo()
            .search([("token", "=", access_token),("expires",">",datetime.datetime.now())])
        )

        if not access_token_data :
            return werkzeug.wrappers.Response(
                    content_type="application/json; charset=utf-8",
                    headers=[("Cache-Control", "no-store"), ("Pragma", "no-cache")],
                    response=json.dumps(
                        {
                            # "uid": uid,
                            # "user_context": request.session.get_context() if uid else {},
                            # "company_id": request.env.user.company_id.id if uid else None,
                            "Error" : "The token provided is invalid !!!",
                            "Message" : "The request is reject, Invalid token !",
                            "Success" : False,
                            "Value" : False,
                        }
                    ),
        )


        return func(self, *args, **kwargs)

    return wrap


class APIControllerDoctor(http.Controller):
    @http.route("/api/get/doctor/data", type="http", auth="none", methods=["GET"], csrf=False)
    @validate_token
    def get_doctor(self, **payload):
        write_date = request.httprequest.headers.get("write_date")
        partner_ids = request.env["res.partner"].sudo().search([('partner_type','in',['dr','clinic','hospital','center'])])
        partner_data = {}
        data = {}
        partner_data_list = []
        for partner in partner_ids :
            partner_data = {
            'name' : partner.name,
            # Address
            'street' : partner.street,
            'street2' : partner.street2,
            'city' : partner.city,
            'country_id' : partner.country_id.id,
            'study_field_id' : partner.study_field_id.id,
            'birth_date' : partner.birth_date.strftime('%Y-%m-%d %H:%M:%S.%f') if partner.birth_date else None ,
            'phone' : partner.phone,
            'mobile' : partner.mobile,
            'email' : partner.email,
            'gender' : partner.gender,
            'blood_type' : partner.blood_type,
            'speciality_id' : partner.speciality_id.id,
            'note' : partner.comment,
            'partner_type' : partner.partner_type,
            'image_url' : partner.image_url_count,
            }
            partner_data_list.append(partner_data)

        data["partner_list"] = partner_data_list

        docotr_speciality_data = {}
        docotr_speciality_data_list = []

        speciality_ids = request.env["doctor.speciality"].sudo().search([])
        for speciality in speciality_ids :
            docotr_speciality_data = {
            'id' : speciality.id,
            'name' : speciality.name,
            }
            docotr_speciality_data_list.append(docotr_speciality_data)

        data["doctor_speciality_list"] = docotr_speciality_data_list


        return werkzeug.wrappers.Response(
            content_type="application/json; charset=utf-8",
            headers=[("Cache-Control", "no-store"), ("Pragma", "no-cache")],
            response=json.dumps(
                {
                    # "uid": uid,
                    # "user_context": request.session.get_context() if uid else {},
                    # "company_id": request.env.user.company_id.id if uid else None,
                    "Error" : "",
                    "Message" : "",
                    "Success" : True,
                    "Value" : data,
                }
            ),
        )