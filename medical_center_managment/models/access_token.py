import hashlib
import os
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.http import request

expires_in = "medical_center_managment.access_token_expires_in"

def nonce(length = 40, prefix = "access_token"):
    """generate an access token string

    Args:
        length (int, optional): the length of the generated string. Defaults to 40.
        prefix (str, optional): prefix of the generated token string. Defaults to "access_token".

    Returns:
        [string]: a string representing an access token
    """
    rbytes = os.urandom(length)
    return "{}_{}".format(prefix, str(hashlib.sha1(rbytes).hexdigest()))

class APIAccessToken(models.Model):
    """"Access token string, to store the user tokens"""
    
    _name = "api.access_token"
    token = fields.Char("Access Token", required = True)
    user_id = fields.Many2one("res.users", string = "User", required = True)
    expires = fields.Datetime("Expires", required = True)
    scope = fields.Char("Scope")

    @classmethod
    def find_one_or_create_token(cls, user_id = None, create = False):
        """generate or find access tokens to users, if user is not sent 
        it will generate token for the user of the env.
        if create is false it will only search for existing valid tokens.

        Args:
            user_id ([int], optional): the user id you wish to create the token for. Defaults to None.
            create (bool, optional): behavior in case no valid tokens found, either create new one or return None. Defaults to False.

        Returns:
            [APIAccessToken]: the valid token created or searched for the specified user.
        """
        self = api.Environment(cls.pool.cursor(), SUPERUSER_ID, {})[cls._name]

        if not user_id:
            user_id = self.env.user.id

        access_token = (
            self.env["api.access_token"]
            .sudo()
            .search([("user_id", " = ", user_id)], order = "id DESC", limit = 1)
        )
        if access_token:
            access_token = access_token[0]
            if access_token.has_expired():
                access_token = None
        if not access_token and create:
            expires = datetime.now() + timedelta(
                seconds = 100000)
            
            vals = {
                "user_id": user_id, 
                "scope": False, 
                "expires": expires.strftime(DEFAULT_SERVER_DATETIME_FORMAT), 
                "token": nonce(), 
            }

            print(expires.strftime(DEFAULT_SERVER_DATETIME_FORMAT))
            access_token = request.env["api.access_token"].create(vals)
        if not access_token:
            return None
        return access_token.token

    def is_valid(self, scopes = None):
        """
        Checks if the access token is valid.
        :param scopes: An iterable containing the scopes to check or None
        """
        self.ensure_one()
        return not self.has_expired() and self._allow_scopes(scopes)
    
    def has_expired(self):
        """Check if the token has expired 

        Returns:
            [boolean]: expired = True
        """
        
        self.ensure_one()
        return datetime.now() > fields.Datetime.from_string(self.expires)

    def _allow_scopes(self, scopes):
        """
        If the token is used for specific scopes
        """
        self.ensure_one()
        if not scopes:
            return True
        provided_scopes = set(self.scope.split())
        resource_scopes = set(scopes)
        return resource_scopes.issubset(provided_scopes)

class Users(models.Model):
    """"Add one2many tokens field into users table"""
    
    _inherit = "res.users"
    token_ids = fields.One2many("api.access_token", "user_id", string = "Access Tokens")
