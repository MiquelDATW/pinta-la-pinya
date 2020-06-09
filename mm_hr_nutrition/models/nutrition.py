# -*- coding: utf-8 -*-
# Copyright 2016 Ursa Information Systems <http://ursainfosystems.com>
# (c) 2020 Miquel March <m.marchpuig@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import models, fields, api, exceptions, _


class NutritionDiet(models.Model):
    _name = "nutrition.diet"
    _description = "Diet"
    _order = "name"

    name = fields.Char("Name", required=True)
    description = fields.Char("Description")
    employee_ids = fields.One2many('hr.employee', 'nutrition_diet_id', string="Employees")


class NutritionFood(models.Model):
    _name = 'nutrition.food'
    _description = "Food"
    _order = "name"

    name = fields.Char("Name", required=True)
    allergen = fields.Boolean("Allergen")
    category_id = fields.Many2one('nutrition.food.category', 'Category', required=True)

    employee_allergen_ids = fields.Many2many(
        comodel_name='hr.employee',
        relation='employee_allergen_rel',
        column1='allergen_id',
        column2='employee_id',
        string='Employees Allergens')

    employee_exclusion_ids = fields.Many2many(
        comodel_name='hr.employee',
        relation='employee_exclusion_rel',
        column1='exclusion_id',
        column2='employee_id',
        string='Employees Exclusions')


class NutritionFoodCategory(models.Model):
    _name = 'nutrition.food.category'
    _description = "Food Category"
    _order = "name"

    name = fields.Char("Name", required=True)
    description = fields.Char("Description")
    food_ids = fields.One2many('nutrition.food', 'category_id', string="Foods")

