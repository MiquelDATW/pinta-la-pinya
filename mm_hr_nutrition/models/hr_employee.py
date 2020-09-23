# -*- coding: utf-8 -*-
# Copyright 2016 Ursa Information Systems <http://ursainfosystems.com>
# (c) 2020 Miquel March <m.marchpuig@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, exceptions, _


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    nutrition_allergen_ids = fields.Many2many(
        comodel_name='nutrition.food',
        relation='employee_allergen_rel',
        column1='employee_id',
        column2='allergen_id',
        domain=[('allergen', '=', True)],
        string='Allergens')

    nutrition_exclusion_ids = fields.Many2many(
        comodel_name='nutrition.food',
        relation='employee_exclusion_rel',
        column1='employee_id',
        column2='exclusion_id',
        string='Exclusions')

    nutrition_diet_id = fields.Many2one(
        comodel_name='nutrition.diet',
        string='Diet')

