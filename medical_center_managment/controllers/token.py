import json
import logging
from datetime import datetime
from datetime import timedelta
from odoo import http
from odoo.http import request
import werkzeug.wrappers

_logger = logging.getLogger(__name__)

expires_in = "medical_center_managment.access_token_expires_in"


class AccessToken(http.Controller):
    """."""

    def __init__(self):
        self._token = request.env["api.access_token"]
        self._expires_in = request.env.ref(expires_in).sudo().value
        self.value = False

    @http.route(
        "/api/auth/token", methods=["GET"], type="http", auth="none", csrf=False
    )

    def token(self, **post):
 
        _token = request.env["api.access_token"]
        params = ["login", "password"]
        params = {key: post.get(key) for key in params if post.get(key)}
        username, password = (
           
            post.get("login"),
            post.get("password"),
        )

        print(username)
        print(password)
        _credentials_includes_in_body = all([username, password])
        if not _credentials_includes_in_body:
            # The request post body is empty the credetials maybe passed via the headers.
            headers = request.httprequest.headers
            
            username = headers.get("login")
            password = headers.get("password")
            _credentials_includes_in_headers = all([True])
            if not _credentials_includes_in_headers:
                # Empty 'db' or 'username' or 'password:
                return werkzeug.wrappers.Response(
                    content_type="application/json; charset=utf-8",
                    headers=[("Cache-Control", "no-store"), ("Pragma", "no-cache")],
                    response=json.dumps(
                        {
                            # "uid": uid,
                            # "user_context": request.session.get_context() if uid else {},
                            # "company_id": request.env.user.company_id.id if uid else None,
                            "Error" : "Something went wrong please check credentials",
                            "Message" : "Please send the credentials in the header or the body",
                            "Success" : False,
                            "Value" : None,
                        }
            ),
        )
        # Login in odoo database:
        try:
            request.session.authenticate(request.env.cr.dbname, username, password)
        except Exception as e:
            # Invalid database:
            info = "The database name is not valid {}".format((e))
            error = "invalid_database"
            _logger.error(info)
            
            return werkzeug.wrappers.Response(
            content_type="application/json; charset=utf-8",
            headers=[("Cache-Control", "no-store"), ("Pragma", "no-cache")],
            response=json.dumps(
                {
                    # "uid": uid,
                    # "user_context": request.session.get_context() if uid else {},
                    # "company_id": request.env.user.company_id.id if uid else None,
                    "Error" : info,
                    "Message" : "You can not get the token   uyu",
                    "Success" : False,
                    "Value" : None,
                }
            ),
        )

        uid = request.session.uid
        # odoo login failed:
        if not uid:
            info = "authentication failed"
            error = "authentication failed"
            _logger.error(info)
            
            return werkzeug.wrappers.Response(
            content_type="application/json; charset=utf-8",
            headers=[("Cache-Control", "no-store"), ("Pragma", "no-cache")],
            response=json.dumps(
                {
                    # "uid": uid,
                    # "user_context": request.session.get_context() if uid else {},
                    # "company_id": request.env.user.company_id.id if uid else None,
                    "Error" : "Something went wrong",
                    "Message" : "You can not get the token",
                    "Success" : False,
                    "Value" : None,
                }
            ),
        )

        access_token = _token.find_one_or_create_token(user_id=uid, create=True)
        # Successful response:
        user = request.env["res.users"].search([('id','=',uid)])

        expiry_date_time_zone_user = (datetime.now() + timedelta(minutes=50000))
        
    
        value = {
                    'UserName':user.login,
                    'Description' : user.name,
                    'PrintDescription' : user.name,
                    'Token' : access_token,
                    'TokenExpiryDate' : str(expiry_date_time_zone_user),
                    'TypeID' : 2,
                    'PhoneNumber' : user.name,
                    'GroupCode' : user.name,
                    'EmailAddress' : user.name,
                    'RelatedClientID' : user.partner_id.id,
                    'IsProcessed' : 0,
                    'StampDate' : str(datetime.now()),
                    'IsActive' : 1,
                    'Avatar' : user.partner_id.image_url_count,
                }



        return werkzeug.wrappers.Response(
            content_type="application/json; charset=utf-8",
            headers=[("Cache-Control", "no-store"), ("Pragma", "no-cache")],
            response=json.dumps(
                {
                    # "uid": uid,
                    # "user_context": request.session.get_context() if uid else {},
                    # "company_id": request.env.user.company_id.id if uid else None,
                    "Error" : "There is no error !!!",
                    "Message" : "Congradulations You Got The TOKEN !",
                    "Success" : True,
                    "Value" : value,
                }
            ),
        )

    @http.route(
        "/api/auth/token", methods=["DELETE"], type="http", auth="none", csrf=False
    )
    def delete(self, **post):
        """."""

        _token = request.env["api.access_token"]
        access_token = request.httprequest.headers.get("access_token")
        access_token = _token.search([("token", "=", access_token)])
        
        if not access_token:
            info = "No access token was provided in request!"
            error = "no_access_token"
            _logger.error(info)
            return invalid_response(400, error, info)
        for token in access_token:
            token.unlink()
        # Successful response:
        return valid_response(
            200, {"desc": "token successfully deleted", "delete": True}
        )
