# -*- coding: utf-8 -*-
# (c) 2020 Miquel March <m.marchpuig@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, exceptions, _
from odoo.exceptions import ValidationError


class HrTeam(models.Model):
    _inherit = 'hr.team'

    at_actual = fields.Boolean(string="Àrea Tècnica", help="Àrea Tècnica actual")
    jd_actual = fields.Boolean(string="Junta Directiva", help="Junta Directiva actual")

    @api.model
    def create(self, vals):
        if 'at_actual' in vals and vals.get('at_actual', False):
            altra_at = self.env['hr.team'].search([('at_actual', '=', True)])
            if bool(altra_at):
                raise ValidationError("Ja hi ha una Àrea Tècnica en actiu❗")
        if 'jd_actual' in vals and vals.get('jd_actual', False):
            altra_at = self.env['hr.team'].search([('jd_actual', '=', True)])
            if bool(altra_at):
                raise ValidationError("Ja hi ha una Junta Directiva en actiu❗")
        res = super(HrTeam, self).create(vals)
        return res

    @api.multi
    def write(self, vals):
        if 'at_actual' in vals and vals.get('at_actual', False):
            altra_at = self.env['hr.team'].search([('at_actual', '=', True)])
            if bool(altra_at):
                raise ValidationError("Ja hi ha una Àrea Tècnica en actiu❗")
        if 'jd_actual' in vals and vals.get('jd_actual', False):
            altra_at = self.env['hr.team'].search([('jd_actual', '=', True)])
            if bool(altra_at):
                raise ValidationError("Ja hi ha una Junta Directiva en actiu❗")
        res = super(HrTeam, self).write(vals)
        return res
