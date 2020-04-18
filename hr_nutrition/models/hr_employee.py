# -*- coding: utf-8 -*-
# Copyright 2016 Ursa Information Systems <http://ursainfosystems.com>
# (c) 2020 Miquel March <m.marchpuig@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import models, fields, api, exceptions, _


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    height = fields.Integer("Height")
    height_uom = fields.Many2one(
        "product.uom", "Height UoM", readonly=True,
        domain=lambda self: [('category_id', '=', self.env.ref('product.uom_categ_length').id)],
        default=lambda self: self.env.ref('product.product_uom_cm').id
    )
    weight = fields.Float("Weight")
    weight_uom = fields.Many2one(
        "product.uom", "Weight UoM", readonly=True,
        domain=lambda self: [('category_id', '=', self.env.ref('product.product_uom_categ_kgm').id)],
        default=lambda self: self.env.ref('product.product_uom_kgm').id
    )
    bmi = fields.Float(string="Body mass index (BMI)", digits=(4, 1),
                       compute='_compute_bmi', store=True)
    bmi_uom = fields.Many2one(
        "product.uom", "BMI UoM", readonly=True,
        domain=lambda self: [('category_id', '=', self.env.ref('hr_nutrition.product_category_bmi').id)],
        default=lambda self: self.env.ref('hr_nutrition.product_uom_bmi').id
    )

    caloric_intake = fields.Float("Calories")
    caloric_intake_uom = fields.Many2one(
        "product.uom", "Calories UoM",
        domain=lambda self: [('category_id', '=', self.env.ref('hr_nutrition.product_category_energy').id)]
    )
    carbohydrate_intake = fields.Float("Carbohydrate")
    carbohydrate_intake_uom = fields.Many2one(
        "product.uom", "Carbohydrate UoM",
        domain=lambda self: [('category_id', '=', self.env.ref('product.product_uom_categ_kgm').id)]
    )
    fat_intake = fields.Float("Fat")
    fat_intake_uom = fields.Many2one(
        "product.uom", "Fat UoM",
        domain=lambda self: [('category_id', '=', self.env.ref('product.product_uom_categ_kgm').id)]
    )
    protein_intake = fields.Float("Protein")
    protein_intake_uom = fields.Many2one(
        "product.uom", "Protein UoM",
        domain=lambda self: [('category_id', '=', self.env.ref('product.product_uom_categ_kgm').id)]
    )

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
        string='Allergens')

    nutrition_exclusion_ids = fields.Many2many(
        comodel_name='nutrition.food',
        string='Exclusions')

    nutrition_diet_id = fields.Many2one('nutrition.diet', 'Diet')

    @api.multi
    @api.depends('height', 'weight')
    def _compute_bmi(self):
        emps = self.filtered(lambda x: bool(x.height) and bool(x.weight))
        for emp in emps:
            bmi = emp.weight/((emp.height/100)**2)
            emp.bmi = bmi

