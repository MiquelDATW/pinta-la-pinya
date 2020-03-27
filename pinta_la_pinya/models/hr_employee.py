# -*- coding: utf-8 -*-
# (c) 2020 Miquel March <m.marchpuig@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import calendar
from odoo import models, fields, api, exceptions, _
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    muixeranguera = fields.Boolean(string="Muixeranguera", default=True)
    data_inscripcio = fields.Date(string="Data inscripció")
    mesos_inscrit = fields.Char(string="Mesos inscrit", compute="_compute_mesos_inscrit")
    altres_noms = fields.Char(string="Altres noms", help="Altres noms pels que es coneix la persona")

    alsada_cap = fields.Integer(string="Alçada")
    alsada_muscle = fields.Integer(string="Alçada del muscle")
    alsada_bras = fields.Integer(string="Alçada de les mans")
    pes = fields.Float(string="Pes", digits=(4, 1))

    muixeranga_tronc_ids = fields.One2many("pinya.muixeranga.tronc", "membre_tronc_id", string="Muixeranga")
    muixeranga_pinya_ids = fields.One2many("pinya.muixeranga.pinya", "membre_pinya_id", string="Muixeranga")

    posicio_ids = fields.Many2many(string="Posicions", comodel_name="hr.skill", compute="_compute_posicions")

    @api.multi
    def _compute_posicions(self):
        muixeranguers = self.filtered(lambda x: x.muixeranguera)
        for muixeranguer in muixeranguers:
            posicions = muixeranguer.employee_skill_ids.mapped('skill_id')
            muixeranguer.posicio_ids = [(6, 0, posicions.ids)]

    @api.multi
    def _compute_mesos_inscrit(self):
        date_now = fields.Date.today()
        muixeranguers = self.filtered(lambda x: x.muixeranguera and bool(x.data_inscripcio))
        for muixeranguer in muixeranguers:
            to_date = fields.Date.from_string(date_now)
            from_dt = fields.Date.from_string(muixeranguer.data_inscripcio)
            delta = relativedelta(to_date, from_dt)
            mesos = delta.years * 12 + delta.months
            muixeranguer.mesos_inscrit = str(mesos)


class HrSkill(models.Model):
    _inherit = 'hr.skill'
    _order = 'tipus desc, name asc'

    tipus = fields.Selection([
        ('pinya', 'Pinya'),
        ('tronc', 'Tronc')
    ], string='Tipus', default="pinya", required=True)


class HrEmployeeSkill(models.Model):
    _inherit = 'hr.employee.skill'
    _order = 'name asc'

    name = fields.Char(string="Nom", index=True, required=True, translate=True)
    description = fields.Char(string="Descripció", related="skill_id.description")

    @api.model
    def create(self, vals):
        skill = vals.get('skill_id', False)
        if skill:
            vals['name'] = self.env['hr.skill'].browse(skill).name
        else:
            vals['name'] = 'Pinya'
        res = super(HrEmployeeSkill, self).create(vals)
        return res
