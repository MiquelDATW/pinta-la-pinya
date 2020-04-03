# -*- coding: utf-8 -*-
# (c) 2020 Miquel March <m.marchpuig@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

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

    posicio_ids = fields.Many2many(string="Posicions", comodel_name="hr.skill", compute="_compute_posicions", store=True)
    count_3stars = fields.Char(string="Habilitats expertes", compute="_compute_millors", store=True)
    count_2stars = fields.Char(string="Habilitats avançats", compute="_compute_millors", store=True)
    count_1stars = fields.Char(string="Habilitats mitjanes", compute="_compute_millors", store=True)
    count_total = fields.Integer(string="Figures total", compute="_compute_count_total", store=True)
    count_sismesos = fields.Integer(string="Figures 6 mesos", compute="_compute_count_sismesos", store=True)

    @api.multi
    @api.depends('employee_skill_ids', 'employee_skill_ids.skill_id')
    def _compute_posicions(self):
        muixeranguers = self.filtered(lambda x: x.muixeranguera)
        for muixeranguer in muixeranguers:
            posicions = muixeranguer.employee_skill_ids.mapped('skill_id')
            muixeranguer.posicio_ids = [(6, 0, posicions.ids)]

    @api.multi
    @api.depends('employee_skill_ids', 'employee_skill_ids.count_total')
    def _compute_count_total(self):
        muixeranguers = self.filtered(lambda x: x.muixeranguera)
        for muixeranguer in muixeranguers:
            total = muixeranguer.employee_skill_ids.mapped('count_total')
            muixeranguer.count_total = sum(total)

    @api.multi
    @api.depends('employee_skill_ids', 'employee_skill_ids.count_sismesos')
    def _compute_count_sismesos(self):
        muixeranguers = self.filtered(lambda x: x.muixeranguera)
        for muixeranguer in muixeranguers:
            total = muixeranguer.employee_skill_ids.mapped('count_sismesos')
            muixeranguer.count_sismesos = sum(total)

    @api.multi
    @api.depends('employee_skill_ids', 'employee_skill_ids.skill_id', 'employee_skill_ids.level')
    def _compute_millors(self):
        muixeranguers = self.filtered(lambda x: x.muixeranguera)
        for muixeranguer in muixeranguers:
            levels = muixeranguer.employee_skill_ids
            l3 = len(levels.filtered(lambda x: x.level == '3'))
            muixeranguer.count_3stars = (str(l3) + ' ⭐⭐⭐') if l3 > 0 else ''
            l2 = len(levels.filtered(lambda x: x.level == '2'))
            muixeranguer.count_2stars = (str(l2) + ' ⭐⭐') if l2 > 0 else ''
            l1 = len(levels.filtered(lambda x: x.level == '1'))
            muixeranguer.count_1stars = (str(l1) + ' ⭐') if l1 > 0 else ''

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

