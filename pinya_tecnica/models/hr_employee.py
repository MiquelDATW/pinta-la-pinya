# -*- coding: utf-8 -*-
# (c) 2020 Miquel March <m.marchpuig@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, exceptions, _
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
from datetime import datetime


def _get_action(view_tree_id, view_form_id, name, model, domain):
    action = {
        'type': 'ir.actions.act_window',
        'views': [(view_tree_id, 'tree'), (view_form_id, 'form')],
        'view_mode': 'form',
        'name': name,
        'target': 'current',
        'res_model': model,
        'context': {},
        'domain': domain,
    }
    return action


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    membre_at = fields.Boolean(string="Membre AT", compute='_compute_at_jd', store=True, help="Membre Àrea Tècnica")
    membre_jd = fields.Boolean(string="Membre JD", compute='_compute_at_jd', store=True, help="Membre Junta Directiva")
    muixeranguera = fields.Boolean(string="Muixeranguera", default=True)
    xicalla = fields.Boolean(string="Xicalla", default=False, readonly=True)
    data_inscripcio = fields.Date(string="Data inscripció")
    anys_inscrit = fields.Integer(string="Anys inscrit", readonly=True)
    nom_croquis = fields.Char(string="Nom del croquis", help="Nom que apareix en els croquis")
    nom_altres = fields.Char(string="Altres noms", help="Altres noms pels que es coneix la persona")
    posicions = fields.Char(string="Posicions", help="Posicions de la muixeranguera", compute='_compute_posicions', store=True)

    edat = fields.Integer(string='Edat', readonly=True)

    alsada_cap = fields.Integer(string="Alçada")
    alsada_muscle = fields.Integer(string="Alçada muscle")
    alsada_bras = fields.Integer(string="Alçada braços")
    pes = fields.Float(string="Pes", digits=(4, 1))
    imc = fields.Float(string="IMC", digits=(4, 1), compute='_compute_imc', store=True)

    muixeranga_tronc_ids = fields.One2many("pinya.muixeranga.tronc", "membre_tronc_id", string="Muixeranga")
    muixeranga_pinya_ids = fields.One2many("pinya.muixeranga.pinya", "membre_pinya_id", string="Muixeranga")
    membre_actuacio_ids = fields.One2many('hr.employee.actuacio', 'employee_id', string="Actuacions")

    posicions_3stars = fields.Char(string="Posicions expertes", compute="_compute_millors", store=True)
    posicions_2stars = fields.Char(string="Posicions avançats", compute="_compute_millors", store=True)
    posicions_1star = fields.Char(string="Posicions intermedies", compute="_compute_millors", store=True)
    count_pinya = fields.Integer(string="Pinyes total", compute="_compute_count_pinya", store=True)
    count_tronc = fields.Integer(string="Troncs total", compute="_compute_count_tronc", store=True)
    count_total = fields.Integer(string="Figures total", compute="_compute_count_total", store=True)
    count_sismesos = fields.Integer(string="Figures 6 mesos", compute="_compute_count_sismesos", store=True)

    count_teams = fields.Integer(string="Equips total", compute="_compute_count_teams", store=True)
    teams = fields.Char(string="Teams", compute='_compute_teams', store=True)

    @api.depends('team_ids')
    def _compute_teams(self):
        teams = self.filtered(lambda x: bool(x.team_ids))
        for team in teams:
            names = team.team_ids.sorted('name').mapped('name')
            team.teams = ", ".join(names)

    @api.multi
    @api.depends('team_ids', 'team_ids.at_actual', 'team_ids.jd_actual')
    def _compute_at_jd(self):
        muixeranguers = self.filtered(lambda x: bool(x.team_ids))
        for muixeranguer in muixeranguers:
            teams = muixeranguer.team_ids
            at = teams.filtered(lambda x: x.at_actual)
            jd = teams.filtered(lambda x: x.jd_actual)
            muixeranguer.membre_at = bool(at)
            muixeranguer.membre_jd = bool(jd)

    @api.multi
    @api.depends('muixeranga_pinya_ids')
    def _compute_count_pinya(self):
        muixeranguers = self.filtered(lambda x: bool(x.muixeranga_pinya_ids))
        for muixeranguer in muixeranguers:
            pinyes = muixeranguer.muixeranga_pinya_ids
            muixeranguer.count_pinya = len(pinyes.ids)

    @api.multi
    @api.depends('muixeranga_tronc_ids')
    def _compute_count_tronc(self):
        muixeranguers = self.filtered(lambda x: bool(x.muixeranga_tronc_ids))
        for muixeranguer in muixeranguers:
            troncs = muixeranguer.muixeranga_tronc_ids
            muixeranguer.count_tronc = len(troncs.ids)

    @api.multi
    @api.depends('team_ids')
    def _compute_count_teams(self):
        muixeranguers = self.filtered(lambda x: bool(x.team_ids))
        for muixeranguer in muixeranguers:
            teams = muixeranguer.team_ids
            muixeranguer.count_teams = len(teams.ids)

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
            muixeranguer.posicions_3stars = (str(l3) + ' ⭐⭐⭐') if l3 > 0 else ''
            l2 = len(levels.filtered(lambda x: x.level == '2'))
            muixeranguer.posicions_2stars = (str(l2) + ' ⭐⭐') if l2 > 0 else ''
            l1 = len(levels.filtered(lambda x: x.level == '1'))
            muixeranguer.posicions_1star = (str(l1) + ' ⭐') if l1 > 0 else ''

    @api.multi
    @api.depends('pes', 'alsada_cap')
    def _compute_imc(self):
        muixeranguers = self.filtered(lambda x: bool(x.pes) and bool(x.alsada_cap))
        for muixeranguer in muixeranguers:
            imc = muixeranguer.pes/((muixeranguer.alsada_cap/100)**2)
            muixeranguer.imc = imc

    @api.multi
    @api.depends('employee_skill_ids', 'employee_skill_ids.skill_id')
    def _compute_posicions(self):
        muixeranguers = self.filtered(lambda x: bool(x.employee_skill_ids))
        for muixeranguer in muixeranguers:
            skills = muixeranguer.employee_skill_ids.mapped('skill_id').sorted('name').mapped('name')
            muixeranguer.posicions = ", ".join(skills)

    @api.multi
    def _compute_anys_inscrit(self):
        date_now = fields.Date.from_string(fields.Date.today())
        muixeranguers = self.search([('muixeranguera', '=', True), ('data_inscripcio', '!=', False)])
        for muixeranguer in muixeranguers:
            from_dt = fields.Date.from_string(muixeranguer.data_inscripcio)
            anys = relativedelta(date_now, from_dt).years
            muixeranguer.anys_inscrit = anys

    @api.multi
    def _compute_edat(self):
        date_now = fields.Date.from_string(fields.Date.today())
        muixeranguers = self.search([('muixeranguera', '=', True), ('birthday', '!=', False)])
        for muixeranguer in muixeranguers:
            from_dt = fields.Date.from_string(muixeranguer.birthday)
            edat = relativedelta(date_now, from_dt).years
            muixeranguer.xicalla = edat < 16
            muixeranguer.edat = edat

    @api.multi
    @api.constrains('birthday', 'data_inscripcio')
    def _check_future_dates(self):
        today = datetime.today().date()
        employees = self.filtered(lambda x: bool(x.birthday) or bool(x.data_inscripcio))
        for employee in employees:
            birthday = fields.Date.from_string(employee.birthday)
            if bool(birthday) and birthday > today:
                raise ValidationError("No és possible una data de naixement en el futur❗")
            inscripcio = fields.Date.from_string(employee.data_inscripcio)
            if bool(inscripcio) and inscripcio > today:
                raise ValidationError("No és possible una data d'inscripció en el futur❗")
            colla_str = self.env.user.company_id.partner_id.fundacio_data
            colla_data = fields.Date.from_string(colla_str)
            if bool(inscripcio) and inscripcio < colla_data:
                raise ValidationError("No és possible una data d'inscripció anterior a la colla: {}❗".format(colla_str))

    def tronc_muixeranga(self):
        view_tree_id = self.env.ref('pinya_tecnica.view_muixeranga_tronc_tree_all').id
        view_form_id = self.env.ref('pinya_tecnica.view_muixeranga_tronc_form').id
        name = "Tronc de {}".format(self.name)
        model = "pinya.muixeranga.tronc"
        domain = [('id', 'in', self.muixeranga_tronc_ids.ids)]
        action = _get_action(view_tree_id, view_form_id, name, model, domain)
        return action

    def pinya_muixeranga(self):
        view_tree_id = self.env.ref('pinya_tecnica.view_muixeranga_pinya_tree_all').id
        view_form_id = self.env.ref('pinya_tecnica.view_muixeranga_pinya_form').id
        name = "Pinya de {}".format(self.name)
        model = "pinya.muixeranga.pinya"
        domain = [('id', 'in', self.muixeranga_pinya_ids.ids)]
        action = _get_action(view_tree_id, view_form_id, name, model, domain)
        return action

    def pinya_teams(self):
        view_tree_id = self.env.ref('hr_team.view_hr_team_tree').id
        view_form_id = self.env.ref('hr_team.view_hr_team_form').id
        name = "Equips de {}".format(self.name)
        model = "hr.team"
        domain = [('id', 'in', self.team_ids.ids)]
        action = _get_action(view_tree_id, view_form_id, name, model, domain)
        return action

    @api.model
    def create(self, vals):
        croquis = vals.get('nom_croquis', False)
        name = vals.get('name', False)
        if croquis:
            vals.update({'nom_croquis': croquis.upper()})
        elif name:
            vals.update({'nom_croquis': name.upper()})

        if 'data_inscripcio' in vals:
            data = vals.get('data_inscripcio', False)
            if data:
                date_now = fields.Date.from_string(fields.Date.today())
                from_dt = fields.Date.from_string(data)
                anys = relativedelta(date_now, from_dt).years
                vals.update({'anys_inscrit': anys})
            else:
                vals.update({'anys_inscrit': 0})
        if 'birthday' in vals:
            data = vals.get('birthday', False)
            if data:
                date_now = fields.Date.from_string(fields.Date.today())
                from_dt = fields.Date.from_string(data)
                anys = relativedelta(date_now, from_dt).years
                vals.update({'edat': anys, 'xicalla': anys < 16})
            else:
                vals.update({'edat': 0})
        res = super(HrEmployee, self).create(vals)
        return res

    @api.multi
    def write(self, vals):
        if 'nom_croquis' in vals:
            nom = vals.get('nom_croquis', False)
            name = vals.get('name', False) or self.name
            if nom:
                vals.update({'nom_croquis': nom.upper()})
            elif name:
                vals.update({'nom_croquis': name.upper()})

        if 'data_inscripcio' in vals:
            data = vals.get('data_inscripcio', False)
            if data:
                date_now = fields.Date.from_string(fields.Date.today())
                from_dt = fields.Date.from_string(data)
                anys = relativedelta(date_now, from_dt).years
                vals.update({'anys_inscrit': anys})
            else:
                vals.update({'anys_inscrit': 0})
        if 'birthday' in vals:
            data = vals.get('birthday', False)
            if data:
                date_now = fields.Date.from_string(fields.Date.today())
                from_dt = fields.Date.from_string(data)
                anys = relativedelta(date_now, from_dt).years
                vals.update({'edat': anys, 'xicalla': anys < 16})
            else:
                vals.update({'edat': 0})
        res = super(HrEmployee, self).write(vals)
        return res


class HrEmployeeActuacio(models.Model):
    _name = 'hr.employee.actuacio'
    _order = 'employee_id'

    active = fields.Boolean('Active', related='employee_id.active', default=True, store=True)
    name = fields.Char(string="Nom", index=True, required=True, translate=True)
    membre_at = fields.Boolean(string="Membre AT", related="employee_id.membre_at", store=True)

    #assistencia = fields.Boolean(string="Assistència")

    employee_id = fields.Many2one('hr.employee', string="Membre")
    actuacio_id = fields.Many2one('pinya.actuacio', string="Actuació")
    data = fields.Datetime(string='Data', related='actuacio_id.data_inici', store=True)
    actuacio_name = fields.Char(string='Nom', related='actuacio_id.name', store=True)
    tipus = fields.Selection(string='Tipus', related='actuacio_id.tipus', store=True)

    pinya_line_ids = fields.One2many('pinya.muixeranga.pinya', 'employee_actuacio_id', string="Pinya de muixeranga")
    tronc_line_ids = fields.One2many('pinya.muixeranga.tronc', 'employee_actuacio_id', string="Tronc de muixeranga")

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

    @api.multi
    def unlink(self):
        muixerangues = self.mapped('actuacio_id').muixeranga_ids
        troncs = muixerangues.mapped('tronc_line_ids').filtered(lambda x: x.employee_actuacio_id.id in self.ids)
        for tronc in troncs:
            tronc.membre_tronc_level_id = False
        pinyes = muixerangues.mapped('pinya_line_ids').filtered(lambda x: x.employee_actuacio_id.id in self.ids)
        for pinya in pinyes:
            pinya.membre_pinya_level_id = False
        res = super(HrEmployeeActuacio, self).unlink()
        return res

