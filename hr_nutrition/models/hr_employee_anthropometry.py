# -*- coding: utf-8 -*-
# (c) 2020 Miquel March <m.marchpuig@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import models, fields, api, exceptions, _


class HrEmployeeAnthropometry(models.Model):
    _name = 'hr.employee.anthropometry'
    _description = 'Employee Anthropometry'
    _order = 'data desc'

    name = fields.Char("Name", required=True)

    employee_id = fields.Many2one('hr.employee', 'Employee', required=True)
    data = fields.Date(string="Date", required=True)

    height = fields.Integer("Height")
    height_diff = fields.Float(string="Height difference", digits=(4, 1), readonly=True)
    weight = fields.Float(string="Weight", digits=(4, 1))
    weight_diff = fields.Float(string="Weight difference", digits=(4, 1), readonly=True)
    bmi = fields.Float(string="Body mass index", digits=(4, 1),
                       compute='_compute_bmi', store=True)
    bmi_diff = fields.Float(string="BMI difference", digits=(4, 1), readonly=True)
    bmi_type = fields.Selection(
        [('18.5', 'Underweight'),
         ('25', 'Normal weight'),
         ('30', 'Overweight'),
         ('35', 'Obese'),
         ('40', 'Severily obese')],
        string="BMI type",
        compute='_compute_bmi_type', store=True)

    @api.multi
    @api.depends('weight', 'height')
    def _compute_bmi(self):
        anthropometry = self.filtered(lambda x: bool(x.height) and bool(x.weight))
        for ant in anthropometry:
            bmi = ant.weight/((ant.height/100)**2)
            ant.bmi = bmi

    @api.multi
    @api.depends('bmi')
    def _compute_bmi_type(self):
        anthropometry = self.filtered(lambda x: bool(x.bmi))
        for ant in anthropometry:
            bmi = ant.bmi
            bmi_type = "18.5"
            if 18.5 <= bmi < 25:
                bmi_type = "25"
            elif 25 <= bmi < 30:
                bmi_type = "30"
            elif 30 <= bmi < 35:
                bmi_type = "35"
            elif 35 <= bmi:
                bmi_type = "40"
            ant.bmi_type = bmi_type

    @api.onchange('employee_id', 'data')
    def _onchange_name(self):
        emp = self.employee_id
        data = self.data
        if emp and data:
            name = emp.name + ". " + str(data).replace("-", "/")
        else:
            name = False
        self.name = name

    def compute_diff(self):
        res = True
        anthropometry = self.employee_id.anthropometry_ids.sorted('data')
        for i in range(len(anthropometry)):
            ant = anthropometry[i]
            data = {}
            if i == 0:
                bmi_diff = height_diff = weight_diff = 0
            else:
                last = anthropometry[i-1]
                bmi_diff = ant.bmi - last.bmi
                height_diff = ant.height - last.height
                weight_diff = ant.weight - last.weight

            if ant.bmi_diff != bmi_diff:
                data.update({'bmi_diff': bmi_diff})
            if ant.height_diff != height_diff:
                data.update({'height_diff': height_diff})
            if ant.weight_diff != weight_diff:
                data.update({'weight_diff': weight_diff})

            if bool(data):
                res_n = ant.write(data)
                res = res and res_n
        return res

    @api.model
    def create(self, vals):
        emp = vals.get('employee_id', False)
        data = vals.get('data', False)
        if emp and data:
            employee = self.env['hr.employee'].browse(emp)
            name = employee.name + ". " + str(data).replace("-", "/")
        else:
            name = "EL GRAN HOUDINI"
        vals.update({'name': name})
        res = super(HrEmployeeAnthropometry, self).create(vals)
        res.compute_diff()

        return res

    @api.multi
    def write(self, vals):
        emp = vals.get('employee_id', False) or self.employee_id.id
        data = vals.get('data', False) or self.data
        if emp and data:
            employee = self.env['hr.employee'].browse(emp)
            name = employee.name + ". " + str(data).replace("-", "/")
            if name != self.name:
                vals.update({'name': name})
        else:
            name = "EL GRAN HOUDINI"
            vals.update({'name': name})
        res = super(HrEmployeeAnthropometry, self).write(vals)

        height = vals.get("height", False)
        weight = vals.get("weight", False)
        if height or weight:
            self.compute_diff()

        return res

