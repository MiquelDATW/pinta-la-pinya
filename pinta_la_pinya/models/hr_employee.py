# -*- coding: utf-8 -*-
# (c) 2020 Miquel March <m.marchpuig@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, exceptions, _
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    membre_at = fields.Boolean(string="Membre AT", default=False)
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
    membre_actuacio_ids = fields.One2many('hr.employee.actuacio', 'employee_id', string="Actuacions")

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

    @api.model
    def create(self, vals):
        res = super(HrEmployee, self).create(vals)
        return res

    @api.multi
    def write(self, vals):
        res = super(HrEmployee, self).write(vals)
        return res


class HrEmployeeActuacio(models.Model):
    _name = 'hr.employee.actuacio'
    _order = 'employee_id'

    active = fields.Boolean('Active', related='employee_id.active', default=True, store=True)
    name = fields.Char(string="Nom", index=True, required=True, translate=True)
    membre_at = fields.Boolean(string="Membre AT", related="employee_id.membre_at", store=True)

    employee_id = fields.Many2one('hr.employee', string="Membre")
    actuacio_id = fields.Many2one('pinya.actuacio', string="Actuació")

    pinya_line_ids = fields.One2many('pinya.muixeranga.pinya', 'employee_actuacio_id', string="Pinya de muixeranga")
    tronc_line_ids = fields.One2many('pinya.muixeranga.tronc', 'employee_actuacio_id', string="Tronc de muixeranga")

    count_3stars = fields.Char(string="Habilitats expertes", related="employee_id.count_3stars", store=True)
    count_2stars = fields.Char(string="Habilitats avançats", related="employee_id.count_2stars", store=True)
    count_1stars = fields.Char(string="Habilitats mitjanes", related="employee_id.count_1stars", store=True)

    count_actuacio_total = fields.Char(string="Figures total", compute="_compute_actuacio", store=True)
    count_actuacio_pinya = fields.Char(string="Figures pinya", compute="_compute_actuacio", store=True)
    count_actuacio_tronc = fields.Char(string="Figures tronc", compute="_compute_actuacio", store=True)

    _sql_constraints = [
        ('employee_actuacio_uniq', 'unique(employee_id, actuacio_id)',
         "Aquest membre ja forma part de l'actuació/assaig❗"),
    ]

    @api.multi
    @api.depends('pinya_line_ids.employee_actuacio_id', 'tronc_line_ids.employee_actuacio_id')
    def _compute_actuacio(self):
        muix_act = self.filtered(lambda x: x)
        for m in muix_act:
            pinyes = m.pinya_line_ids
            troncs = m.tronc_line_ids

            suma1 = [0, 0, 0, 0]
            p1 = pinyes.filtered(lambda x: x.membre_pinya_id.id == m.employee_id.id)
            if not bool(p1):
                p4 = ""
            else:
                p2 = list(set(p1.mapped('posicio_id').sorted('prioritat').mapped('prioritat')))
                p3 = []
                for i in p2:
                    i2 = str(i).replace('0', '0️⃣').replace('1', '1️⃣').replace('2', '2️⃣').replace('3', '3️⃣')
                    aux = str(len(p1.filtered(lambda x: x.posicio_id.prioritat == i).ids))
                    suma1[int(i)] = aux
                    p3.append(aux + ' ' + i2)
                p3.reverse()
                p4 = ", ".join(p3)
            m.count_actuacio_pinya = p4

            suma2 = [0, 0, 0, 0]
            t1 = troncs.filtered(lambda x: x.membre_tronc_id.id == m.employee_id.id)
            if not bool(t1):
                t4 = ""
            else:
                t2 = list(set(t1.mapped('posicio_id').sorted('prioritat').mapped('prioritat')))
                t3 = []
                for i in t2:
                    i2 = str(i).replace('0', '0️⃣').replace('1', '1️⃣').replace('2', '2️⃣').replace('3', '3️⃣')
                    aux = str(len(t1.filtered(lambda x: x.posicio_id.prioritat == i).ids))
                    suma2[int(i)] = aux
                    t3.append(aux + ' ' + i2)
                t3.reverse()
                t4 = ", ".join(t3)
            m.count_actuacio_tronc = t4

            suma_n = []
            for i in range(4):
                ss = int(suma1[i]) + int(suma2[i])
                if ss != 0:
                    i2 = str(i).replace('0', '0️⃣').replace('1', '1️⃣').replace('2', '2️⃣').replace('3', '3️⃣')
                    suma_n.append(str(ss) + ' ' + i2)
            suma_n.reverse()
            suma_c = ", ".join(suma_n)
            m.count_actuacio_total = suma_c

    @api.model
    def create(self, vals):
        if not vals.get('name', False):
            muix = vals.get('employee_id')
            name = self.env['hr.employee'].browse(muix).name
            vals['name'] = name
        res = super(HrEmployeeActuacio, self).create(vals)
        return res

    @api.multi
    def write(self, vals):
        res = super(HrEmployeeActuacio, self).write(vals)
        return res

