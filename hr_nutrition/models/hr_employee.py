# -*- coding: utf-8 -*-
# Copyright 2016 Ursa Information Systems <http://ursainfosystems.com>
# (c) 2020 Miquel March <m.marchpuig@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import models, fields, api, exceptions, _


def _get_action(view_tree_id, view_form_id, name, model, domain):
    action = {
        'type': 'ir.actions.act_window',
        'views': [(view_tree_id, 'tree'), (view_form_id, 'form')],
        'view_mode': 'form',
        'name': name,
        'target': 'current',
        'res_model': model,
        'context': {},
        'domain': domain,
    }
    return action


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    anthropometry_id = fields.Many2one(
        'hr.employee.anthropometry', 'Anthropometry',
        compute="_get_anthropometry", store=True)
    anthropometry_ids = fields.One2many(
        'hr.employee.anthropometry', 'employee_id', 'Anthropometry history')

    height = fields.Integer("Height", related="anthropometry_id.height", store=True)
    weight = fields.Float("Weight", related="anthropometry_id.weight", store=True)
    bmi = fields.Float(string="Body mass index (BMI)", related="anthropometry_id.bmi", store=True)
    bmi_type = fields.Selection(string="BMI type", related="anthropometry_id.bmi_type", store=True)

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
    @api.depends('anthropometry_ids')
    def _get_anthropometry(self):
        emps = self.filtered(lambda x: bool(x.anthropometry_ids))
        for emp in emps:
            anthropometry = emp.anthropometry_ids.sorted('data', reverse=True)
            emp.anthropometry_id = anthropometry[0].id

    def anthropometry_new(self):
        view_form_id = self.env.ref('hr_nutrition.view_anthropometry_form').id
        name = "New Weight & Height"
        model = "hr.employee.anthropometry"
        ctx = self.env.context.copy()
        ctx.update({
            'default_employee_id': self.id,
            'default_height': self.height,
            'default_data': fields.Date.today(),
            'default_name': self.name + ". " + str(fields.Date.today()).replace("-", "/"),
        })
        action = {
            'type': 'ir.actions.act_window',
            'views': [(view_form_id, 'form')],
            'view_mode': 'form',
            'name': name,
            'target': 'current',
            'res_model': model,
            'context': ctx,
        }
        return action

    def anthropometry_history(self):
        view_tree_id = self.env.ref('hr_nutrition.view_anthropometry_tree').id
        view_form_id = self.env.ref('hr_nutrition.view_anthropometry_form').id
        name = "Weight & Height history of {}".format(self.name)
        model = "hr.employee.anthropometry"
        domain = [('id', 'in', self.anthropometry_ids.ids)]
        action = _get_action(view_tree_id, view_form_id, name, model, domain)
        return action

