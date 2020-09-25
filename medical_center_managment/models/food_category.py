"""Add two models.

Models Added:
FoodCategory
Food
"""
from odoo import models, fields, api

class FoodCategory(models.Model):
	"""."""

	_name = "food.category"
	_description = "Food Category"
	name = fields.Char("Name", translate = True)
	negative_disease_ids = fields.Many2many()
	positive_disease_ids = fields.Many2many()

class Food(models.Model) :
	"""."""
	
	name = fields.Char("Name", translate = True)
	category_id = fields.Many2one("food.category", string = "Category")
	negative_disease_ids = fields.Many2many()
	positive_disease_ids = fields.Many2many()
	