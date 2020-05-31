# -*- coding: utf-8 -*-
# (c) 2020 Miquel March <m.marchpuig@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, exceptions, _
from odoo.exceptions import ValidationError


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    @api.depends('user_id')
    def _compute_display_data(self):
        for employee in self:
            employee.employee_display_personal_data = False
            if self.user_has_groups('hr.group_hr_user'):
                employee.employee_display_data = True
            elif employee.user_id == self.env.user:
                employee.employee_display_data = True
            elif self.env.user.id in employee.family_ids.mapped('family_id.user_id').ids:
                employee.employee_display_data = True

    employee_display_data = fields.Boolean(
        compute='_compute_display_data'
    )
