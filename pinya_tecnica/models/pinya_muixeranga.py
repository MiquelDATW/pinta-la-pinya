# -*- coding: utf-8 -*-
# (c) 2020 Miquel March <m.marchpuig@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import statistics
import logging
import random
from odoo import models, fields, api, exceptions, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


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


class PinyaMuixeranga(models.Model):
    """
    Cree esta classe com a base de les figures muixerangueres
    """
    _name = "pinya.muixeranga"
    _description = "Muixeranga"
    _order = "id desc"
    _inherit = ['mail.thread']

    name = fields.Char(string="Nom", index=True, required=True, translate=True)
    active = fields.Boolean(string="Actiu", default=True)
    plantilla_id = fields.Many2one("pinya.plantilla", string="Plantilla", required=True, readonly=True)
    notes = fields.Text(string="Altra informació")

    tipus = fields.Selection(related="plantilla_id.tipus", string='Tipus', store=True, readonly=True)
    pisos = fields.Selection(related="plantilla_id.pisos", string='Pisos', store=True, readonly=True)
    neta = fields.Boolean(related="plantilla_id.neta", string='Sense pinya', store=True, readonly=True)
    cordons = fields.Integer(compute='_compute_cordons', string='Cordons', store=True, readonly=True)

    tronc_line_ids = fields.One2many('pinya.muixeranga.tronc', 'muixeranga_tronc_id', string="Tronc", copy=True)
    pinya_line_ids = fields.One2many('pinya.muixeranga.pinya', 'muixeranga_pinya_id', string="Pinya", copy=True)

    mestra_id = fields.Many2one('hr.employee', string="Mestra")
    passadora_id = fields.Many2one('hr.employee', string="Passadora")
    estiradora_id = fields.Many2one('hr.employee', string="Estiradora")
    resp_xicalla_ids = fields.Many2many('hr.employee', string="Responsable de xicalla")
    total_count = fields.Integer(compute='_compute_total_count', string='Total persones', store=True)
    pinya_count = fields.Integer(compute='_compute_total_count', string='Persones pinya', store=True)
    tronc_count = fields.Integer(compute='_compute_total_count', string='Persones tronc', store=True)
    pinya_count2 = fields.Integer(compute='_compute_total_count', string='Pinya', store=True)
    tronc_count2 = fields.Integer(compute='_compute_total_count', string='Tronc', store=True)

    actuacio_id = fields.Many2one(string="Actuació", comodel_name="pinya.actuacio", store=True)
    membre_count = fields.Integer(string='Total Membres', related='actuacio_id.membres_count', store=True)
    data = fields.Datetime(string='Data', related='actuacio_id.data_inici', store=True)
    actuacio_state = fields.Selection(string='Estat actuació', related='actuacio_id.state', store=True)
    temporada_id = fields.Many2one(string="Temporada", comodel_name="pinya.temporada", related='actuacio_id.temporada_id', store=True)
    actual = fields.Boolean(string="Actual", related="temporada_id.actual", store=True)

    lliure_ids = fields.Many2many('hr.employee', string="Lliures", compute="_compute_lliures")
    lliure_count = fields.Integer(compute='_compute_lliures', string='Total Lliures')

    alineacio = fields.Selection([
        ('0', 'Tothom nou'),
        ('25', 'Mantindre alguna posició'),
        ('50', 'Meitat'),
        ('75', 'Probar alguna posició'),
        ('100', 'Millor alineació')
    ], string='Alineació', required=True, default='75',
    help="Permet incloure persones noves amb menys experiència en les figures")

    state = fields.Selection([
        ('cancel', 'Cancel·lat'),
        ('draft', 'Esborrany'),
        ('ready', 'Preparat'),
        ('descarregat', 'Descarregat'),
        ('intent', 'Intent'),
        ('caigut', 'Caigut')
    ], string='Estat', required=True, default='draft')

    image = fields.Binary("Image", attachment=True, help="Limitat a 1024x1024px.")

    @api.multi
    def _compute_lliures(self):
        """
        Calcula els membres que estan lliures (no tenen assignada encara una posició)
        """
        membres = self.actuacio_id.membre_actuacio_ids.filtered(lambda x: x.assistencia).mapped('employee_id')
        troncs = self.tronc_line_ids.mapped('membre_tronc_id')
        pinyes = self.pinya_line_ids.mapped('membre_pinya_id')
        altres = self.mestra_id + self.passadora_id + self.estiradora_id
        xicalleres = self.resp_xicalla_ids
        lliures = membres - troncs - pinyes - altres - xicalleres
        self.lliure_ids = [(6, 0, lliures.ids)]
        self.lliure_count = len(lliures.ids)
        return lliures

    @api.multi
    @api.depends('pinya_line_ids')
    def _compute_cordons(self):
        """
        Calcula els cordons de la muixeranga
        """
        muixs = self.filtered(lambda x: not x.neta)
        for muix in muixs:
            c = max(muix.pinya_line_ids.mapped('cordo') or [0])
            muix.cordons = c

    @api.multi
    @api.depends('tronc_line_ids', 'pinya_line_ids')
    def _compute_total_count(self):
        """
        Calcula els totals de pinya i tronc
        """
        for muix in self:
            t = len(muix.tronc_line_ids)
            p = len(muix.pinya_line_ids)
            muix.tronc_count = t
            muix.pinya_count = p
            muix.total_count = t + p
            muix.tronc_count2 = t
            muix.pinya_count2 = p

    def action_descarregat(self):
        """
        Canvia l'estat de la figura
        """
        self.state = 'descarregat'

    def action_intent(self):
        """
        Canvia l'estat de la figura
        """
        self.state = 'intent'

    def action_caigut(self):
        """
        Canvia l'estat de la figura
        """
        self.state = 'caigut'

    def action_cancel(self):
        """
        Canvia l'estat de la figura
        """
        action_cancel = self.env.context.get('action_cancel', False)
        actuacio_state = self.actuacio_state
        if bool(action_cancel) and actuacio_state == 'done':
            troncs = self.tronc_line_ids
            for tronc in troncs:
                tronc.membre_tronc_level_id = False
            pinyes = self.pinya_line_ids
            for pinya in pinyes:
                pinya.membre_pinya_level_id = False
        self.state = 'cancel'

    def action_draft(self):
        """
        Canvia l'estat de la figura
        """
        self.state = 'draft'

    def reset_muixeranga(self):
        """
        Reinicialitzem la muixeranga
        """
        self.state = 'draft'
        self.actuacio_id.state = 'draft'
        troncs = self.tronc_line_ids
        for tronc in troncs:
            tronc.membre_tronc_level_id = False
        pinyes = self.pinya_line_ids
        for pinya in pinyes:
            pinya.membre_pinya_level_id = False

    def calcular_muixeranga(self):
        """
        Calculem la muixeranga
        """
        def _calcular_membre(tipus, muixe, ocupats):
            def _calcular_tronc(tronc, alsada_best):
                if alsada_best:
                    alsades = tronc.sorted(lambda x: abs(x.alsada_muscle - alsada_best))
                else:
                    i = random.randint(0, len(tronc) - 1)
                    alsades = tronc[i]
                res = alsades[0]
                return res

            def _calcular_pinya(pinya):
                pinya = pinya.sorted('alsada_bras', reverse=True)
                res = pinya[0]
                return res

            recomanats = muixe.recomanats_ids.filtered(lambda x: x.employee_id.id not in ocupats)
            aptes = recomanats.filtered(lambda x: x.level >= muixe.tecnica)
            if not bool(aptes):
                aptes = recomanats
            if not bool(aptes):
                muixeranga = muixe.muixeranga_pinya_id.name if tipus == "pinya" else \
                    (muixe.muixeranga_tronc_id.name if tipus == "tronc" else "")
                _logger.error("No es pot omplir la posició <{}> de la figura <{}>❗".format(
                    muixe.posicio_id.name, muixeranga))
                return False

            uniq_posicio = muixe.quisocjo.split('__')[0]
            if tipus == "tronc":
                people = tronc.search([('muixeranga_tronc_id', '!=', tronc.muixeranga_tronc_id.id),
                                       ('quisocjo', 'ilike', uniq_posicio)]).mapped('membre_tronc_id')
                all_time = tronc.search([('quisocjo', 'ilike', uniq_posicio)]).mapped('membre_tronc_id')
                alsada_best = round(statistics.mean(all_time.mapped('alsada_muscle'))) if bool(all_time) else False
            elif tipus == "pinya":
                people = pinya.search([('muixeranga_pinya_id', '!=', pinya.muixeranga_pinya_id.id),
                                       ('quisocjo', 'ilike', uniq_posicio)]).mapped('membre_pinya_id')
                all_time = pinya.search([('quisocjo', 'ilike', uniq_posicio)]).mapped('membre_pinya_id')
                alsada_best = max(all_time.mapped('alsada_bras')) if bool(all_time) else False
            else:
                alsada_best = people = False

            sabuts = aptes.filtered(lambda x: x.employee_id.id in people.ids) if bool(people) else aptes

            seguretat = random.randint(0, 100)
            if seguretat <= alineacio and bool(sabuts):
                if tipus == "tronc":
                    membre = _calcular_tronc(sabuts, alsada_best)
                elif tipus == "pinya":
                    membre = _calcular_pinya(sabuts)
                else:
                    membre = False
            else:
                equilibris = aptes.filtered(lambda x: x.employee_id.id not in muixe_readies.ids)
                if not bool(equilibris):
                    equilibris = recomanats.filtered(lambda x: x.employee_id.id not in muixe_readies.ids)
                    if not bool(equilibris):
                        equilibris = aptes
                if tipus == "tronc":
                    membre = _calcular_tronc(equilibris, alsada_best)
                elif tipus == "pinya":
                    membre = _calcular_pinya(equilibris)
                else:
                    membre = False
            return membre

        # Iniciem el càlcul de la muixeranga
        # ---------------------------------------------------------
        ocupats = []
        # alineació és el % de posicions que són "noves"
        alineacio = int(self.alineacio)
        # readies són la resta de figures de l'actuació que ja estan en estat preparat
        readies = self.actuacio_id.muixeranga_ids.filtered(lambda x: x.state == 'ready')
        # muixe_readies són les persones que ocupen posicions en les altres troncs de l'actuació
        muixe_readies = readies.mapped('tronc_line_ids.employee_actuacio_id.employee_id')
        # troncs són les posicions de tronc no ocupades ordenades per nivel de tècnica
        troncs = self.tronc_line_ids.filtered(lambda x: not x.membre_tronc_id).sorted('tecnica', reverse=True)
        i = 0
        for tronc in troncs:
            i += 1
            # subfunció que calcula quina persona ocuparà aquesta posició
            membre = _calcular_membre("tronc", tronc, ocupats)
            if membre and membre.employee_id:
                # Assignem la persona calculada a la posició
                tronc.membre_tronc_level_id = membre.id
                # Afegim la persona a la llista de persones que ocupen una posició en la figura
                ocupats.append(membre.employee_id.id)
                # Fem anotació en el log
                _logger.info("Calculant tronc {} de {}...".format(str(i), len(troncs)))

        # muixe_readies són les persones que ocupen posicions en les altres pinyes de l'actuació
        muixe_readies = readies.mapped('pinya_line_ids.employee_actuacio_id.employee_id')
        # pinyes són les posicions de pinya no ocupades ordenades per nivel de tècnica
        pinyes = self.pinya_line_ids.filtered(lambda x: not x.membre_pinya_id).sorted('tecnica', reverse=True)
        tecniques = ['3', '2', '1', '0']
        i = 0
        for tecnica in tecniques:
            # el procediment en les pinyes serà un poc diferent als troncs
            # xq les pinyes són molt més nombroses en persones que els troncs
            # començarem a omplir les posicions segons la tècnica que necessiten i
            # ordenades per la seua prioritat
            # ❗ tècnica és el nivell de coneixement per ocupar la posició
            # ❗ prioritat és la urgència en ocupar eixa posició respecta una altra
            pinyes_ = pinyes.filtered(lambda x: x.tecnica == tecnica).sorted(lambda x: x.posicio_id.prioritat, reverse=True)
            for pinya in pinyes_:
                i += 1
                # subfunció que calcula quina persona ocuparà aquesta posició
                membre = _calcular_membre("pinya", pinya, ocupats)
                if membre and membre.employee_id:
                    # Assignem la persona calculada a la posició
                    pinya.membre_pinya_level_id = membre.id
                    # Afegim la persona a la llista de persones que ocupen una posició en la figura
                    ocupats.append(membre.employee_id.id)
                    # Fem anotació en el log
                    _logger.info("Calculant pinya {} de {}...".format(str(i), len(pinyes)))

        # Una vegada calculada la muixeranga, li canviem l'estat a "Preparada"
        self.state = 'ready'

    def tronc_muixeranga(self):
        """
        Funció per mostrar els troncs
        """
        view_tree_id = self.env.ref('pinya_tecnica.view_muixeranga_tronc_tree_selected').id
        view_form_id = self.env.ref('pinya_tecnica.view_muixeranga_tronc_form').id
        name = "Tronc de {}".format(self.name)
        model = "pinya.muixeranga.tronc"
        domain = [('id', 'in', self.tronc_line_ids.ids)]
        action = _get_action(view_tree_id, view_form_id, name, model, domain)
        return action

    def pinya_muixeranga(self):
        """
        Funció per mostrar les pinyes
        """
        view_tree_id = self.env.ref('pinya_tecnica.view_muixeranga_pinya_tree_selected').id
        view_form_id = self.env.ref('pinya_tecnica.view_muixeranga_pinya_form').id
        name = "Pinya de {}".format(self.name)
        model = "pinya.muixeranga.pinya"
        domain = [('id', 'in', self.pinya_line_ids.ids)]
        action = _get_action(view_tree_id, view_form_id, name, model, domain)
        return action

    @api.multi
    def unlink(self):
        """
        Si s'elimina la muixeranga, ens assegurem que les pìnyes i els troncs, tb s'eliminen
        Compobrar si funciona més senzill amb: ondelete="cascade"
        """
        for muixe in self:
            muixe.pinya_line_ids.unlink()
            muixe.tronc_line_ids.unlink()
        res = super(PinyaMuixeranga, self).unlink()
        return res


class PinyaMuixerangaPinya(models.Model):
    """
    Cree esta classe com a base de les figures muixerangueres
    """
    _name = "pinya.muixeranga.pinya"
    _description = "Pinya de muixeranga"
    _order = "data desc, muixeranga_pinya_id, cordo, rengle, posicio_id asc"

    name = fields.Char(string="Nom", index=True, required=True, translate=True)
    quisocjo = fields.Char(string="Qui sòc jo")
    cordo = fields.Selection([
        ('0', '0'),
        ('1', '1'), ('2', '2'), ('3', '3'),
        ('4', '4'),  ('5', '5'),  ('6', '6'),
    ], string="Cordó", required=True)

    rengle = fields.Integer(string="Rengle", required=True)
    active = fields.Boolean(string="Actiu", default=True)
    data = fields.Datetime(string="Data", related="muixeranga_pinya_id.actuacio_id.data_inici", readonly=True, store=True)

    tecnica = fields.Selection([
        ('0', 'Inicial'),
        ('1', 'Intermedia'),
        ('2', 'Avançada'),
        ('3', 'Experta'),
    ], string='Tècnica', default="1", required=True)

    posicio_id = fields.Many2one(string="Posició", comodel_name="hr.skill", required=True)
    muixeranga_pinya_id = fields.Many2one(string="Figura", comodel_name="pinya.muixeranga")
    membre_pinya_id = fields.Many2one(string="Membre Pinya", comodel_name="hr.employee",
                                      related="membre_pinya_level_id.employee_id", store=True)
    membre_pinya_level_id = fields.Many2one(string="Membre Pinya Level", comodel_name="hr.employee.level")
    employee_actuacio_id = fields.Many2one(string="Membre actuacio", comodel_name="hr.employee.actuacio", compute="_compute_employee_actuacio", store=True)
    actuacio_id = fields.Many2one(string="Actuació", related="muixeranga_pinya_id.actuacio_id", readonly=True, store=True)
    muixeranga_state = fields.Selection(string='Estat muixeranga', related='muixeranga_pinya_id.state', store=True)
    plantilla_id = fields.Many2one(string="Plantilla", related="muixeranga_pinya_id.plantilla_id", readonly=True, store=True)

    recomanats_ids = fields.Many2many(string="Recomanats", comodel_name="hr.employee.level", compute="_compute_recomanats")

    _sql_constraints = [
        ('muixeranga_membre_pinya_uniq', 'unique(muixeranga_pinya_id, membre_pinya_id)',
         "Aquest membre ja forma part de la figura❗"),
    ]

    @api.multi
    @api.depends('membre_pinya_id', 'actuacio_id')
    def _compute_employee_actuacio(self):
        """
        Calcula cada muixeranguer que està en l'actuació
        """
        emp_act_obj = self.env['hr.employee.actuacio']
        pinyes = self.filtered(lambda x: x.membre_pinya_id and x.actuacio_id)
        for pinya in pinyes:
            membre = pinya.membre_pinya_id.id
            actuacio = pinya.actuacio_id.id
            membre_actuacio = emp_act_obj.search([('employee_id', '=', membre), ('actuacio_id', '=', actuacio)])
            pinya.employee_actuacio_id = membre_actuacio.id

    @api.multi
    def _compute_recomanats(self):
        """
        Calcula els muixeranguers recomanats per a una posició
        """
        if not bool(self.ids):
            return False
        muixeranga = self.mapped('muixeranga_pinya_id')
        if len(muixeranga) > 1:
            return False
        muixers = muixeranga.lliure_ids
        pinyes = muixeranga.pinya_line_ids
        for pinya in pinyes:
            levels = pinya.posicio_id.employee_level_ids
            mu1 = muixers.filtered(lambda x: pinya.posicio_id.id in x.employee_skill_ids.mapped('skill_id').ids)
            recomanats = levels.filtered(lambda x: x.employee_id.id in mu1.ids).sorted('level', reverse=True)
            pinya.recomanats_ids = [(6, 0, recomanats.ids)]

    @api.onchange('posicio_id', 'cordo')
    def _onchange_make_name(self):
        """
        Ens assegurem que el nom de la pinya no queda buit
        """
        if not bool(self.posicio_id) and not self.cordo:
            name = ''
        elif not bool(self.posicio_id) and self.cordo:
            name = ' / ' + str(self.cordo)
        elif bool(self.posicio_id) and not self.cordo:
            name = self.posicio_id.name + ' / '
        else:
            name = self.posicio_id.name + ' / ' + str(self.cordo)
        self.name = name

    @api.model
    def create(self, vals):
        res = super(PinyaMuixerangaPinya, self).create(vals)
        return res

    @api.multi
    def write(self, vals):
        res = super(PinyaMuixerangaPinya, self).write(vals)
        return res


class PinyaMuixerangaTronc(models.Model):
    _name = "pinya.muixeranga.tronc"
    _description = "Tronc de muixeranga"
    _order = "data desc, muixeranga_tronc_id, pis, rengle, posicio_id asc"

    name = fields.Char(string="Nom", index=True, required=True, translate=True)
    quisocjo = fields.Char(string="Qui sòc jo")
    active = fields.Boolean(string="Actiu", default=True)
    data = fields.Datetime(string="Data", related="muixeranga_tronc_id.actuacio_id.data_inici", readonly=True, store=True)

    tecnica = fields.Selection([
        ('0', 'Inicial'),
        ('1', 'Intermedia'),
        ('2', 'Avançada'),
        ('3', 'Experta'),
    ], string='Tècnica', default="1", required=True)

    pis = fields.Selection([
        ('1', '1'), ('2', '2'), ('3', '3'),
        ('4', '4'),  ('5', '5'),  ('6', '6'),
    ], string="Pis", required=True)
    rengle = fields.Integer(string="Rengle", required=True)
    posicio_id = fields.Many2one(string="Posició", comodel_name="hr.skill", required=True)
    muixeranga_tronc_id = fields.Many2one(string="Figura", comodel_name="pinya.muixeranga")
    membre_tronc_id = fields.Many2one(string="Membre Tronc", comodel_name="hr.employee",
                                      related="membre_tronc_level_id.employee_id", store=True)
    membre_tronc_level_id = fields.Many2one(string="Membre Tronc Level", comodel_name="hr.employee.level")
    employee_actuacio_id = fields.Many2one(string="Membre actuacio", comodel_name="hr.employee.actuacio", compute="_compute_employee_actuacio", store=True)
    actuacio_id = fields.Many2one(string="Actuació", related="muixeranga_tronc_id.actuacio_id", readonly=True, store=True)
    muixeranga_state = fields.Selection(string='Estat muixeranga', related='muixeranga_tronc_id.state', store=True)
    plantilla_id = fields.Many2one(string="Plantilla", related="muixeranga_tronc_id.plantilla_id", readonly=True, store=True)

    recomanats_ids = fields.Many2many(string="Recomanats", comodel_name="hr.employee.level", compute="_compute_recomanats")

    _sql_constraints = [
        ('muixeranga_membre_tronc_uniq', 'unique(muixeranga_tronc_id, membre_tronc_id)',
         "Aquest membre ja forma part de la figura❗"),
    ]

    @api.multi
    @api.depends('membre_tronc_id', 'actuacio_id')
    def _compute_employee_actuacio(self):
        emp_act_obj = self.env['hr.employee.actuacio']
        troncs = self.filtered(lambda x: x.membre_tronc_id and x.actuacio_id)
        for tronc in troncs:
            membre = tronc.membre_tronc_id.id
            actuacio = tronc.actuacio_id.id
            membre_actuacio = emp_act_obj.search([('employee_id', '=', membre), ('actuacio_id', '=', actuacio)])
            tronc.employee_actuacio_id = membre_actuacio.id

    @api.multi
    def _compute_recomanats(self):
        if not bool(self.ids):
            return False
        muixeranga = self.mapped('muixeranga_tronc_id')
        if len(muixeranga) > 1:
            return False
        muixers = muixeranga.lliure_ids
        troncs = muixeranga.tronc_line_ids
        for tronc in troncs:
            levels = tronc.posicio_id.employee_level_ids
            mu1 = muixers.filtered(lambda x: tronc.posicio_id.id in x.employee_skill_ids.mapped('skill_id').ids)
            recomanats = levels.filtered(lambda x: x.employee_id.id in mu1.ids).sorted('level', reverse=True)
            tronc.recomanats_ids = [(6, 0, recomanats.ids)]

    @api.onchange('posicio_id', 'pis')
    def _onchange_make_name(self):
        if not bool(self.posicio_id) and not self.pis:
            name = ''
        elif not bool(self.posicio_id) and self.pis:
            name = ' / ' + str(self.pis)
        elif bool(self.posicio_id) and not self.pis:
            name = self.posicio_id.name + ' / '
        else:
            name = self.posicio_id.name + ' / ' + str(self.pis)
        self.name = name

    @api.model
    def create(self, vals):
        res = super(PinyaMuixerangaTronc, self).create(vals)
        return res

    @api.multi
    def write(self, vals):
        res = super(PinyaMuixerangaTronc, self).write(vals)
        return res

