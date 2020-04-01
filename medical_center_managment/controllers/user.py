import json
import logging
from datetime import datetime
from datetime import timedelta,timezone
from odoo import http
from odoo.http import request

import yaml

_logger = logging.getLogger(__name__)


class UserSignUp(http.Controller):
    """."""

    @http.route(
        "/api/signup", methods=["GET"], type="http", auth="none", csrf=False
    )
    def signup(self, **post):
        base_comapny = request.env.ref("base.main_company").sudo().id
        group_portal = request.env.ref("base.group_portal").sudo().id

        user_data = request.httprequest.data
        user_data_in_json = yaml.load(user_data)
        partner_id = request.env["res.partner"].sudo().with_context(force_company = base_comapny,mail_create_nosubscribe=True).create({
            "name" : user_data_in_json["name"],
            }).id

        user_id = request.env["res.users"].with_context(mail_create_nosubscribe=True,force_company = base_comapny).sudo().create({
            "company_ids" : [(6,0,[base_comapny])],
            "company_id" : base_comapny,
            "notification_type" : user_data_in_json["notification_type"],
            "odoobot_state" : user_data_in_json["odoobot_state"],
            "partner_id" : partner_id,
            "login" : user_data_in_json["login"],
            "groups_id" :[(6,0,[group_portal])]
            })
