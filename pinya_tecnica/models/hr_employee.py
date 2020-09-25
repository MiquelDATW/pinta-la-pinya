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
    """
    Faig herència d'esta classe per gastar-la com a persona muixeranguera.
    """
    _inherit = 'hr.employee'

    membre_at = fields.Boolean(string="Membre AT", compute='_compute_at_jd', store=True, help="Membre Àrea Tècnica")
    membre_jd = fields.Boolean(string="Membre JD", compute='_compute_at_jd', store=True, help="Membre Junta Directiva")
    muixeranguera = fields.Boolean(string="Muixeranguera", default=True)
    xicalla = fields.Boolean(string="Xicalla", compute="_compute_xicalla", store=True)
    data_inscripcio = fields.Date(string="Data inscripció")
    anys_inscrit = fields.Integer(string="Anys inscrit", readonly=True)
    nom_croquis = fields.Char(string="Nom del croquis", help="Nom que apareix en els croquis")
    nom_altres = fields.Char(string="Altres noms", help="Altres noms pels que es coneix la persona")
    posicions = fields.Char(string="Posicions", help="Posicions de la muixeranguera", compute='_compute_posicions', store=True)

    alsada_muscle = fields.Integer("Alçada muscle", related="anthropometry_id.alsada_muscle", store=True)
    alsada_bras = fields.Integer("Alçada braços", related="anthropometry_id.alsada_bras", store=True)

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

    @api.multi
    @api.depends('team_ids', 'team_ids.at_actual', 'team_ids.jd_actual')
    def _compute_at_jd(self):
        """
        Calcula si el muixeranguer forma part de l'AT o JD actual
        """
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
        """
        Calcula el número de pinyes que forma part el muixeranguer
        """
        muixeranguers = self.filtered(lambda x: bool(x.muixeranga_pinya_ids))
        for muixeranguer in muixeranguers:
            pinyes = muixeranguer.muixeranga_pinya_ids
            muixeranguer.count_pinya = len(pinyes.ids)

    @api.multi
    @api.depends('muixeranga_tronc_ids')
    def _compute_count_tronc(self):
        """
        Calcula el número de troncs que forma part el muixeranguer
        """
        muixeranguers = self.filtered(lambda x: bool(x.muixeranga_tronc_ids))
        for muixeranguer in muixeranguers:
            troncs = muixeranguer.muixeranga_tronc_ids
            muixeranguer.count_tronc = len(troncs.ids)

    @api.multi
    @api.depends('employee_skill_ids', 'employee_skill_ids.count_total')
    def _compute_count_total(self):
        """
        Calcula el número de figures que ha format part el muixeranguer
        """
        muixeranguers = self.filtered(lambda x: x.muixeranguera)
        for muixeranguer in muixeranguers:
            total = muixeranguer.employee_skill_ids.mapped('count_total')
            muixeranguer.count_total = sum(total)

    @api.multi
    @api.depends('employee_skill_ids', 'employee_skill_ids.count_sismesos')
    def _compute_count_sismesos(self):
        """
        Calcula el número de figures que ha format part els darres 6 mesos el muixeranguer
        """
        muixeranguers = self.filtered(lambda x: x.muixeranguera)
        for muixeranguer in muixeranguers:
            total = muixeranguer.employee_skill_ids.mapped('count_sismesos')
            muixeranguer.count_sismesos = sum(total)

    @api.multi
    @api.depends('employee_skill_ids', 'employee_skill_ids.skill_id', 'employee_skill_ids.level')
    def _compute_millors(self):
        """
        Calcula en format caràcter la tècnica de les posicions del muixeranguer
        """
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
    @api.depends('employee_skill_ids', 'employee_skill_ids.skill_id')
    def _compute_posicions(self):
        """
        Calcula en format caràcter les posicions del muixeranguer
        """
        muixeranguers = self.filtered(lambda x: bool(x.employee_skill_ids))
        for muixeranguer in muixeranguers:
            skills = muixeranguer.employee_skill_ids.mapped('skill_id').sorted('name').mapped('name')
            muixeranguer.posicions = ", ".join(skills)

    @api.multi
    def _compute_anys_inscrit(self):
        """
        Calcula els anys de pertànyer a la colla
        Serà cridada cada dia per el cron: ir_cron_code_compute_anys_inscrit
        """
        date_now = fields.Date.from_string(fields.Date.today())
        muixeranguers = self.search([('muixeranguera', '=', True), ('data_inscripcio', '!=', False)])
        for muixeranguer in muixeranguers:
            from_dt = fields.Date.from_string(muixeranguer.data_inscripcio)
            anys = relativedelta(date_now, from_dt).years
            muixeranguer.anys_inscrit = anys

    @api.multi
    @api.depends("age")
    def _compute_xicalla(self):
        """
        Calcula si el muixeranguer és menor de 16 anys i, per tant, xicalla
        """
        muixeranguers = self.search([('muixeranguera', '=', True), ('age', '<', 16)])
        for muixeranguer in muixeranguers:
            edat = muixeranguer.age
            muixeranguer.xicalla = edat < 16 if bool(edat) else False

    @api.multi
    @api.constrains('birthday', 'data_inscripcio')
    def _check_future_dates(self):
        """
        Ens assegurem que les dates de naixement i d'inscripció siguen coherents
        """
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
            if bool(inscripcio) and bool(colla_data) and inscripcio < colla_data:
                raise ValidationError("No és possible una data d'inscripció anterior a la colla: {}❗".format(colla_str))

    def tronc_muixeranga(self):
        """
        Funció per mostrar els troncs del muixeranguer
        """
        view_tree_id = self.env.ref('pinya_tecnica.view_muixeranga_tronc_tree_all').id
        view_form_id = self.env.ref('pinya_tecnica.view_muixeranga_tronc_form').id
        name = "Tronc de {}".format(self.name)
        model = "pinya.muixeranga.tronc"
        domain = [('id', 'in', self.muixeranga_tronc_ids.ids)]
        action = _get_action(view_tree_id, view_form_id, name, model, domain)
        return action

    def pinya_muixeranga(self):
        """
        Funció per mostrar les pinyes del muixeranguer
        """
        view_tree_id = self.env.ref('pinya_tecnica.view_muixeranga_pinya_tree_all').id
        view_form_id = self.env.ref('pinya_tecnica.view_muixeranga_pinya_form').id
        name = "Pinya de {}".format(self.name)
        model = "pinya.muixeranga.pinya"
        domain = [('id', 'in', self.muixeranga_pinya_ids.ids)]
        action = _get_action(view_tree_id, view_form_id, name, model, domain)
        return action

    def anthropometry_new(self):
        """
        Funció per mostrar els pesos i les alçades del muixeranguer
        """
        action = super(HrEmployee, self).anthropometry_new()
        ctx = action.get('context')
        ctx.update({
            'default_alsada_muscle': self.alsada_muscle,
            'default_alsada_bras': self.alsada_bras,
        })
        action.update({'context': ctx})
        return action

    @api.model
    def create(self, vals):
        """
        Calcula els anys de d'inscripió a la colla en el moment de crear-se el registre
        """
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
        res = super(HrEmployee, self).create(vals)
        return res

    @api.multi
    def write(self, vals):
        """
        Calcula els anys d'inscripió a la colla en el moment de modificar-se el registre
        """
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
        res = super(HrEmployee, self).write(vals)
        return res

    @api.multi
    def toggle_active(self):
        """
        Si arxivem l'empleat, arxivem també el partner
        """
        res = super(HrEmployee, self).toggle_active()
        employee = self.env.context.get('toggle_active_employee', False)
        if self.address_home_id and employee:
            self.address_home_id.toggle_active()
        return res


class HrEmployeeActuacio(models.Model):
    """
    Cree esta classe per relacionar la informació de cada muixeranguer en cada actuació.
    """
    _name = 'hr.employee.actuacio'
    _order = 'employee_id'

    active = fields.Boolean('Active', related='employee_id.active', default=True, store=True)
    name = fields.Char(string="Nom", index=True, required=True, translate=True)
    membre_at = fields.Boolean(string="Membre AT", related="employee_id.membre_at", store=True)

    assistencia = fields.Boolean(string="Assistència")

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
        """
        Excessivament complicada funció per descriure les figures en les que participa el muixeranguer
        amb distinció de la prioritat de la posició
        """
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

    @api.onchange("employee_id")
    def _onchange_employee_id(self):
        """
        Omplir (temporalment) el camp del nom
        """
        if self.employee_id:
            self.name = self.employee_id.name
        else:
            self.name = False

    @api.model
    def create(self, vals):
        """
        Si no té nom, li asignem el del muixeranguer
        Si ja existeix, però sense assistència, en compte de crear-lo, li fiquen assistència = True
        """
        if not vals.get('name', False):
            muix = vals.get('employee_id')
            name = self.env['hr.employee'].browse(muix).name
            vals['name'] = name
        res = self.search([('employee_id', '=', vals.get('employee_id')), ('actuacio_id', '=', vals.get('actuacio_id'))])
        if bool(res) and not bool(res.assistencia):
            res.write({'assistencia': True})
        else:
            res = super(HrEmployeeActuacio, self).create(vals)
        return res

    @api.multi
    def write(self, vals):
        res = super(HrEmployeeActuacio, self).write(vals)
        return res

    @api.multi
    def unlink(self):
        """
        Si s'elimina el muixeranguer de l'actuació, ens assegurem que les posicions que puguera estar, tb s'eliminen
        Compobrar si funciona més senzill amb: ondelete="cascade"
        """
        muixerangues = self.mapped('actuacio_id').muixeranga_ids
        troncs = muixerangues.mapped('tronc_line_ids').filtered(lambda x: x.employee_actuacio_id.id in self.ids)
        for tronc in troncs:
            tronc.membre_tronc_level_id = False
        pinyes = muixerangues.mapped('pinya_line_ids').filtered(lambda x: x.employee_actuacio_id.id in self.ids)
        for pinya in pinyes:
            pinya.membre_pinya_level_id = False
        res = super(HrEmployeeActuacio, self).unlink()
        return res

