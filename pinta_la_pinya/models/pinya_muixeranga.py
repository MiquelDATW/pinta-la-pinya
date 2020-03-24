# -*- coding: utf-8 -*-
# (c) 2020 Miquel March <m.marchpuig@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, exceptions, _
from odoo.exceptions import ValidationError


class PinyaMuixeranga(models.Model):
    _name = "pinya.muixeranga"
    _description = "Muixeranga"
    _order = "name asc"
    _inherit = ['mail.thread']

    name = fields.Char(string="Nom", index=True, required=True, translate=True)
    active = fields.Boolean(string="Actiu", default=True)
    plantilla_id = fields.Many2one("pinya.plantilla", string="Plantilla", required=True, readonly="1")
    notes = fields.Text(string="Altra informació")

    tipus = fields.Selection(related="plantilla_id.tipus", string='Tipus', required=True, readonly="1")
    pisos = fields.Selection(related="plantilla_id.pisos", string='Pisos', required=True, readonly="1")
    cordons = fields.Integer(compute='_compute_cordons', string='Cordons', store=True, readonly="1")

    tronc_line_ids = fields.One2many('pinya.muixeranga.line', 'muixeranga_tronc_id', string="Tronc", copy=True)
    pinya_line_ids = fields.One2many('pinya.muixeranga.line', 'muixeranga_pinya_id', string="Pinya", copy=True)

    mestra_id = fields.Many2one('hr.employee', string="Mestra")
    passadora_id = fields.Many2one('hr.employee', string="Passadora")
    estiradora_id = fields.Many2one('hr.employee', string="Estiradora")
    resp_xicalla_ids = fields.Many2many('hr.employee', string="Responsable de xicalla")
    membres_count = fields.Integer(compute='_compute_membres_count', string='Total persones', store=True)
    pinya_count = fields.Integer(compute='_compute_membres_count', string='Persones pinya', store=True)
    tronc_count = fields.Integer(compute='_compute_membres_count', string='Persones tronc', store=True)

    actuacio_id = fields.Many2one(string="Actuació", comodel_name="pinya.actuacio")
    membre_ids = fields.Many2many('hr.employee', string="Membres", related="actuacio_id.membre_ids")

    estat = fields.Selection([
        ('draft', 'Esborrany'),
        ('desca', 'Descarregat'),
        ('intent', 'Intent'),
        ('fail', 'Caigut')
    ], string='Estat', required=True, default='draft')

    image = fields.Binary("Image", attachment=True, help="Limitat a 1024x1024px.")

    @api.multi
    @api.depends('pinya_line_ids')
    def _compute_cordons(self):
        for muix in self:
            c = max(muix.pinya_line_ids.mapped('cordo'))
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


class PinyaMuixerangaLine(models.Model):
    _name = "pinya.muixeranga.line"
    _description = "Línea de muixeranga"
    _order = "name, rengle, posicio_id asc"

    name = fields.Char(string="Pis/Cordó", index=True, required=True, translate=True)
    pis = fields.Integer(string="Pis")
    cordo = fields.Integer(string="Cordó")
    rengle = fields.Integer(string="Rengle")
    active = fields.Boolean(string="Actiu", default=True)

    posicio_id = fields.Many2one(string="Posició", comodel_name="hr.skill")
    muixeranga_tronc_id = fields.Many2one(string="Figura", comodel_name="pinya.muixeranga")
    muixeranga_pinya_id = fields.Many2one(string="Figura", comodel_name="pinya.muixeranga")
    membre_tronc_id = fields.Many2one(string="Membre Tronc", comodel_name="hr.employee")
    membre_pinya_id = fields.Many2one(string="Membre Pinya", comodel_name="hr.employee")

    tipus = fields.Selection([
        ('pinya', 'Pinya'),
        ('tronc', 'Tronc')
    ], string='Tipus', required=True)



