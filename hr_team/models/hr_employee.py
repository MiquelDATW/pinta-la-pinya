# -*- coding: utf-8 -*-
# (c) 2020 Miquel March <m.marchpuig@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, exceptions, _


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    team_ids = fields.Many2many('hr.team', string='Teams')

