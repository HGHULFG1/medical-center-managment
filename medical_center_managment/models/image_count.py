"""In order to make image caching possible for third party clients, there is a need \
to store a variable telling the api client that the image of the partner has been changed.

Modified Models:
    ResPartner
        Added fields:
            image_changes: count the change of the image the partner.
            image_url_count: computed field to get the url of the partner image.
"""
from odoo import api, fields, models
from datetime import datetime


class ResPartner(models.Model):
    """Add image count (to track the modification of image changes for a partner)."""

    _inherit = 'res.partner'
    image_changes = fields.Integer(
        "Image changing count", default=False, compute="_get_image_changes", store=True)
    image_url_count = fields.Char(
        "Image URL Changes", compute="_get_url_count", store=True)

    @api.depends("image_1920")
    def _get_image_changes(self):
        for record in self:
            record.image_changes = record.image_changes + 1

    @api.depends("image_1920")
    def _get_url_count(self):
        for record in self:
            record.image_url_count = "/api/get/image/contact" + \
                str(record.image_changes + 1) + "/" + str(record.id)
