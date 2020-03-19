# -*- coding: utf-8 -*-
# (c) 2020 Miquel March <m.marchpuig@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, exceptions, _
from odoo.exceptions import ValidationError


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    data_inscripcio = fields.Date(string="Data inscripció")
    altres_noms = fields.Char(string="Altres noms", help="Altres noms pels que es coneix la persona")

    muixeranguera = fields.Boolean(string="Muixeranguera", default=True)
    pinya_ids = fields.Many2many("pinya.pinya.line", string="Pinya")
    tronc_ids = fields.Many2many("pinya.tronc.line", string="Tronc")


class HrEmployeeSkill(models.Model):
    _inherit = 'hr.employee.skill'

    name = fields.Char(string="Nom", index=True, required=True, translate=True)

    @api.model
    def create(self, vals):
        skill = vals.get('skill_id', False)
        if skill:
            vals['name'] = self.env['hr.skill'].browse(skill).name
        else:
            vals['name'] = 'Pinya'
        res = super(HrEmployeeSkill, self).create(vals)
        return res
