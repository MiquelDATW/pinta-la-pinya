# -*- coding: utf-8 -*-
# Copyright 2016 Ursa Information Systems <http://ursainfosystems.com>
# (c) 2020 Miquel March <m.marchpuig@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import models, fields, api, exceptions, _


class NutritionDiet(models.Model):
    _name = 'nutrition.diet'
    _description = "Diet"

    name = fields.Char("Name", required=True)
    description = fields.Char("Description")


class NutritionFood(models.Model):
    _name = 'nutrition.food'
    _description = "Food"

    name = fields.Char("Name", required=True)
    category_id = fields.Many2one('nutrition.food.category', 'Category', required=True)


class NutritionFoodCategory(models.Model):
    _name = 'nutrition.food.category'
    _description = "Food Category"

    name = fields.Char("Name", required=True)

