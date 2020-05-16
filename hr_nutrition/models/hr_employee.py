# -*- coding: utf-8 -*-
# Copyright 2016 Ursa Information Systems <http://ursainfosystems.com>
# (c) 2020 Miquel March <m.marchpuig@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import models, fields, api, exceptions, _


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    height = fields.Integer("Height")
    weight = fields.Float("Weight", digits=(4, 1))
    bmi = fields.Float(string="Body mass index (BMI)", digits=(4, 1),
                       compute='_compute_bmi', store=True)
    bmi_type = fields.Selection(
        [('18.5', 'Underweight'),
         ('25', 'Normal weight'),
         ('30', 'Overweight'),
         ('35', 'Obese'),
         ('40', 'Severily obese')],
        string="BMI type",
        compute='_compute_bmi_type', store=True)

    activity_level = fields.Selection(
        [('sedentary', 'Sedentary'),
         ('active1', 'Moderately active'),
         ('active2', 'Very active'),
         ('active3', 'Extremely active')],
        string="Activity Level")

    weight_goal = fields.Selection(
        [('lose', 'Lose weight'),
         ('maintain', 'Maintain weight'),
         ('gain', 'Gain weight')],
        string="Goal")

    nutrition_allergen_ids = fields.Many2many(
        comodel_name='nutrition.food',
        relation='nutrition_allergen_food_rel',
        column1='allergen_id',
        column2='food_id',
        domain=[('allergen', '=', True)],
        string='Allergens')

    nutrition_exclusion_ids = fields.Many2many(
        comodel_name='nutrition.food',
        relation='nutrition_exclusion_food_rel',
        column1='exclusion_id',
        column2='food_id',
        string='Exclusions')

    nutrition_diet_id = fields.Many2one('nutrition.diet', 'Diet')

    @api.multi
    @api.depends('height', 'weight')
    def _compute_bmi(self):
        emps = self.filtered(lambda x: bool(x.height) and bool(x.weight))
        for emp in emps:
            bmi = emp.weight/((emp.height/100)**2)
            emp.bmi = bmi

    @api.multi
    @api.depends('bmi')
    def _compute_bmi_type(self):
        emps = self.filtered(lambda x: bool(x.bmi))
        for emp in emps:
            bmi = emp.bmi
            bmi_type = "18.5"
            if 18.5 <= bmi < 25:
                bmi_type = "25"
            elif 25 <= bmi < 30:
                bmi_type = "30"
            elif 30 <= bmi < 35:
                bmi_type = "35"
            elif 35 <= bmi:
                bmi_type = "40"
            emp.bmi_type = bmi_type


