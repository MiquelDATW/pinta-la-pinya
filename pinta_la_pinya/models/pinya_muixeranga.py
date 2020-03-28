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
        lliures = membres - troncs - pinyes
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


class PinyaMuixerangaPinya(models.Model):
    _name = "pinya.muixeranga.pinya"
    _description = "Pinya de muixeranga"
    _order = "data, muixeranga_pinya_id, name, rengle, posicio_id asc"

    name = fields.Char(string="Cordó", index=True, required=True, translate=True)
    rengle = fields.Char(string="Rengle")
    active = fields.Boolean(string="Actiu", default=True)

    posicio_id = fields.Many2one(string="Posició", comodel_name="hr.skill")
    muixeranga_pinya_id = fields.Many2one(string="Figura", comodel_name="pinya.muixeranga")
    membre_pinya_id = fields.Many2one(string="Membre Pinya", comodel_name="hr.employee")

    actuacio_id = fields.Many2one(string="Actuació", comodel_name="pinya.actuacio", readonly=True)
    data = fields.Date(string="Data", readonly=True)

    disponible_ids = fields.Many2many(string="Disponibles", comodel_name="hr.employee", compute="_compute_disponible")
    recomanats_ids = fields.Many2many(string="Recomanats", comodel_name="hr.employee", compute="_compute_disponible")

    @api.onchange('membre_pinya_id')
    def onchange_membre_pinya(self):
        print("membre_pinya_id")

    @api.multi
    @api.depends('muixeranga_pinya_id.lliure_ids')
    def _compute_disponible(self):
        max_all = 6
        pinya = self.mapped('muixeranga_pinya_id')
        if len(pinya) > 1:
            return False
        muixers = pinya.lliure_ids
        for pinya in self:
            p1 = muixers.filtered(lambda x: pinya.posicio_id.id in x.posicio_ids.ids)
            p2 = p1.sorted(lambda x: x.employee_skill_ids.filtered(lambda x: x.skill_id.id == pinya.posicio_id.id).level,
                          reverse=True)
            p3 = p2[0:max_all] if len(p2) > max_all else p2
            pinya.recomanats_ids = [(6, 0, p3.ids)]
            pinya.disponible_ids = [(6, 0, p2.ids)]

    @api.model
    def create(self, vals):
        muixeranga = vals.get('muixeranga_pinya_id', False)
        if muixeranga:
            actuacio = self.env['pinya.muixeranga'].browse(muixeranga).actuacio_id
            vals['data'] = actuacio.data
            vals['actuacio_id'] = actuacio.id
        res = super(PinyaMuixerangaPinya, self).create(vals)
        return res


class PinyaMuixerangaTronc(models.Model):
    _name = "pinya.muixeranga.tronc"
    _description = "Tronc de muixeranga"
    _order = "data, muixeranga_tronc_id, name, posicio_id asc"

    name = fields.Char(string="Pis", index=True, required=True, translate=True)
    active = fields.Boolean(string="Actiu", default=True)

    posicio_id = fields.Many2one(string="Posició", comodel_name="hr.skill")
    muixeranga_tronc_id = fields.Many2one(string="Figura", comodel_name="pinya.muixeranga")
    membre_tronc_id = fields.Many2one(string="Membre Tronc", comodel_name="hr.employee")

    actuacio_id = fields.Many2one(string="Actuació", comodel_name="pinya.actuacio", readonly=True)
    data = fields.Date(string="Data", readonly=True)

    disponible_ids = fields.Many2many(string="Disponibles", comodel_name="hr.employee", compute="_compute_disponible")
    recomanats_ids = fields.Many2many(string="Recomanats", comodel_name="hr.employee", compute="_compute_disponible")

    @api.multi
    def _compute_disponible(self):
        max_all = 6
        tronc = self.mapped('muixeranga_tronc_id')
        if len(tronc) > 1:
            return False
        muixers = tronc.lliure_ids
        for tronc in self:
            t1 = muixers.filtered(lambda x: tronc.posicio_id.id in x.posicio_ids.ids)
            t2 = t1.sorted(lambda x: x.employee_skill_ids.filtered(lambda x: x.skill_id.id == tronc.posicio_id.id).level,
                          reverse=True)
            t3 = t2[0:max_all] if len(t2) > max_all else t2
            tronc.recomanats_ids = [(6, 0, t3.ids)]
            tronc.disponible_ids = [(6, 0, t2.ids)]

    @api.onchange('membre_tronc_id')
    def onchange_membre_tronc(self):
        print("membre_tronc_id")
        # max_all = 6
        # lliures = self.muixeranga_tronc_id._compute_lliures()
        # troncs = self.muixeranga_tronc_id.tronc_line_ids
        # for tronc in troncs:
        #     t1 = lliures.filtered(lambda x: tronc.posicio_id.id in x.posicio_ids.ids)
        #     t2 = t1.sorted(lambda x: x.employee_skill_ids.filtered(lambda x: x.skill_id.id == tronc.posicio_id.id).level,
        #                   reverse=True)
        #     t3 = t2[0:max_all] if len(t2) > max_all else t2
        #     tronc.recomanats_ids = [(6, 0, t3.ids)]
        #     tronc.disponible_ids = [(6, 0, t2.ids)]

    @api.model
    def create(self, vals):
        muixeranga = vals.get('muixeranga_tronc_id', False)
        if muixeranga:
            actuacio = self.env['pinya.muixeranga'].browse(muixeranga).actuacio_id
            vals['data'] = actuacio.data
            vals['actuacio_id'] = actuacio.id
        res = super(PinyaMuixerangaTronc, self).create(vals)
        return res