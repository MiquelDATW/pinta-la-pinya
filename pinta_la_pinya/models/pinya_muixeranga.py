# -*- coding: utf-8 -*-
# (c) 2020 Miquel March <m.marchpuig@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, exceptions, _
from odoo.exceptions import ValidationError


class PinyaMuixeranga(models.Model):
    _name = "pinya.muixeranga"
    _description = "Muixeranga"
    _order = "id desc"
    _inherit = ['mail.thread']

    name = fields.Char(string="Nom", index=True, required=True, translate=True)
    active = fields.Boolean(string="Actiu", default=True)
    plantilla_id = fields.Many2one("pinya.plantilla", string="Plantilla", required=True, readonly="1")
    notes = fields.Text(string="Altra informació")

    tipus = fields.Selection(related="plantilla_id.tipus", string='Tipus', required=True, readonly="1")
    pisos = fields.Selection(related="plantilla_id.pisos", string='Pisos', required=True, readonly="1")
    cordons = fields.Integer(compute='_compute_cordons', string='Cordons', store=True, readonly="1")

    tronc_line_ids = fields.One2many('pinya.muixeranga.tronc', 'muixeranga_tronc_id', string="Tronc", copy=True)
    pinya_line_ids = fields.One2many('pinya.muixeranga.pinya', 'muixeranga_pinya_id', string="Pinya", copy=True)

    mestra_id = fields.Many2one('hr.employee', string="Mestra")
    passadora_id = fields.Many2one('hr.employee', string="Passadora")
    estiradora_id = fields.Many2one('hr.employee', string="Estiradora")
    resp_xicalla_ids = fields.Many2many('hr.employee', string="Responsable de xicalla")
    membres_count = fields.Integer(compute='_compute_membres_count', string='Total persones', store=True)
    pinya_count = fields.Integer(compute='_compute_membres_count', string='Persones pinya', store=True)
    tronc_count = fields.Integer(compute='_compute_membres_count', string='Persones tronc', store=True)

    actuacio_id = fields.Many2one(string="Actuació", comodel_name="pinya.actuacio")
    membre_ids = fields.Many2many('hr.employee', string="Membres", related="actuacio_id.membre_ids")
    lliure_ids = fields.Many2many('hr.employee', string="Lliures", compute="_compute_lliures")

    estat = fields.Selection([
        ('draft', 'Esborrany'),
        ('desca', 'Descarregat'),
        ('intent', 'Intent'),
        ('fail', 'Caigut')
    ], string='Estat', required=True, default='draft')

    image = fields.Binary("Image", attachment=True, help="Limitat a 1024x1024px.")

    @api.multi
    def _compute_lliures(self):
        membres = self.membre_ids.filtered(lambda x: x.muixeranguera)
        troncs = self.tronc_line_ids.mapped('membre_tronc_id')
        pinyes = self.pinya_line_ids.mapped('membre_pinya_id')
        altres = self.mestra_id + self.passadora_id + self.estiradora_id
        xicalleres = self.resp_xicalla_ids
        lliures = membres - troncs - pinyes - altres - xicalleres
        self.lliure_ids = [(6, 0, lliures.ids)]
        return lliures

    @api.multi
    @api.depends('pinya_line_ids')
    def _compute_cordons(self):
        for muix in self:
            c = max(muix.pinya_line_ids.mapped('name'))
            muix.cordons = c

    @api.multi
    @api.depends('tronc_line_ids', 'pinya_line_ids')
    def _compute_membres_count(self):
        for muix in self:
            t = len(muix.tronc_line_ids)
            p = len(muix.pinya_line_ids)
            muix.tronc_count = t
            muix.pinya_count = p
            muix.membres_count = t + p

    def calcular_muixeranga(self):
        print(fields.Datetime.now())

    def tronc_muixeranga(self):
        view_tree_id = self.env.ref('pinta_la_pinya.view_muixeranga_tronc_tree_selected').id
        view_form_id = self.env.ref('pinta_la_pinya.view_muixeranga_tronc_form').id
        name = self.name
        domain = [('id', 'in', self.tronc_line_ids.ids)]
        action = {
            'type': 'ir.actions.act_window',
            'views': [(view_tree_id, 'tree'), (view_form_id, 'form')],
            'view_mode': 'form',
            'name': "Tronc de {}".format(name),
            'target': 'current',
            'res_model': 'pinya.muixeranga.tronc',
            'context': {},
            'domain': domain,
        }
        return action

    def pinya_muixeranga(self):
        view_tree_id = self.env.ref('pinta_la_pinya.view_muixeranga_pinya_tree_selected').id
        view_form_id = self.env.ref('pinta_la_pinya.view_muixeranga_pinya_form').id
        name = self.name
        domain = [('id', 'in', self.pinya_line_ids.ids)]
        action = {
            'type': 'ir.actions.act_window',
            'views': [(view_tree_id, 'tree'), (view_form_id, 'form')],
            'view_mode': 'form',
            'name': "Pinya de {}".format(name),
            'target': 'current',
            'res_model': 'pinya.muixeranga.pinya',
            'context': {},
            'domain': domain,
        }
        return action


class PinyaMuixerangaPinya(models.Model):
    _name = "pinya.muixeranga.pinya"
    _description = "Pinya de muixeranga"
    _order = "data, muixeranga_pinya_id, name, rengle, posicio_id asc"

    name = fields.Char(string="Cordó", index=True, required=True, translate=True)
    rengle = fields.Char(string="Rengle")
    active = fields.Boolean(string="Actiu", default=True)
    data = fields.Date(string="Data", related="muixeranga_pinya_id.actuacio_id.data", readonly=True, store=True)

    posicio_id = fields.Many2one(string="Posició", comodel_name="hr.skill")
    muixeranga_pinya_id = fields.Many2one(string="Figura", comodel_name="pinya.muixeranga")
    membre_pinya_id = fields.Many2one(string="Membre Pinya", comodel_name="hr.employee",
                                      related="membre_pinya_level_id.employee_id", store=True)
    membre_pinya_level_id = fields.Many2one(string="Membre Pinya Level", comodel_name="hr.employee.level")
    actuacio_id = fields.Many2one(string="Actuació", related="muixeranga_pinya_id.actuacio_id", readonly=True, store=True)

    recomanats_ids = fields.Many2many(string="Recomanats ⭐", comodel_name="hr.employee.level", compute="_compute_recomanats")

    @api.multi
    def _compute_recomanats(self):
        if not bool(self.ids):
            return False
        muixeranga = self.mapped('muixeranga_pinya_id')
        if len(muixeranga) > 1:
            return False
        muixers = muixeranga.lliure_ids
        pinyes = muixeranga.pinya_line_ids
        for pinya in pinyes:
            levels = pinya.posicio_id.employee_level_ids
            mu1 = muixers.filtered(lambda x: pinya.posicio_id.id in x.posicio_ids.ids)
            recomanats = levels.filtered(lambda x: x.employee_id.id in mu1.ids).sorted('level', reverse=True)
            pinya.recomanats_ids = [(6, 0, recomanats.ids)]

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
    _order = "data, muixeranga_tronc_id, name, posicio_id asc"

    name = fields.Char(string="Pis", index=True, required=True, translate=True)
    active = fields.Boolean(string="Actiu", default=True)
    data = fields.Date(string="Data", related="muixeranga_tronc_id.actuacio_id.data", readonly=True, store=True)

    posicio_id = fields.Many2one(string="Posició", comodel_name="hr.skill")
    muixeranga_tronc_id = fields.Many2one(string="Figura", comodel_name="pinya.muixeranga")
    membre_tronc_id = fields.Many2one(string="Membre Tronc", comodel_name="hr.employee",
                                      related="membre_tronc_level_id.employee_id", store=True)
    membre_tronc_level_id = fields.Many2one(string="Membre Tronc Level", comodel_name="hr.employee.level")
    actuacio_id = fields.Many2one(string="Actuació", related="muixeranga_tronc_id.actuacio_id", readonly=True, store=True)

    recomanats_ids = fields.Many2many(string="Recomanats ⭐", comodel_name="hr.employee.level", compute="_compute_recomanats")

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
            mu1 = muixers.filtered(lambda x: tronc.posicio_id.id in x.posicio_ids.ids)
            recomanats = levels.filtered(lambda x: x.employee_id.id in mu1.ids).sorted('level', reverse=True)
            tronc.recomanats_ids = [(6, 0, recomanats.ids)]

    @api.model
    def create(self, vals):
        res = super(PinyaMuixerangaTronc, self).create(vals)
        return res

    @api.multi
    def write(self, vals):
        res = super(PinyaMuixerangaTronc, self).write(vals)
        return res

