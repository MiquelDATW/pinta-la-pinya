# -*- coding: utf-8 -*-
# (c) 2020 Miquel March <m.marchpuig@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, exceptions, _
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
from datetime import datetime


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    age = fields.Integer(string='Age', compute="_compute_age", store=True)

    @api.multi
    @api.depends('birthday')
    def _compute_age(self):
        date_now = fields.Date.from_string(fields.Date.today())
        employees = self.search([('birthday', '!=', False)])
        for employee in employees:
            from_dt = fields.Date.from_string(employee.birthday)
            age = relativedelta(date_now, from_dt).years
            employee.age = age

    @api.model
    def create(self, vals):
        res = super(HrEmployee, self).create(vals)
        return res

    @api.multi
    def write(self, vals):
        res = super(HrEmployee, self).write(vals)
        return res

