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
    plantilla = fields.Boolean(string="Plantilla", default=False)
    notes = fields.Text(string="Altra informació")

    tipus = fields.Selection([
        ('normal', 'Normal'),
        ('desplega', 'Desplagada'),
        ('aixecat', 'Aixecat')
    ], string='Tipus', required=True, default='normal')

    pisos = fields.Integer('Pisos')
    tronc_ids = fields.One2many('pinya.tronc', 'muixeranga_id', string="Tronc")
    pinya_ids = fields.One2many('pinya.pinya', 'muixeranga_id', string="Pinya")

    membres_ids = fields.Many2many('pinya.membre', string="Membres")
    mestra_id = fields.Many2one('pinya.membre', string="Mestra")
    passadora_id = fields.Many2one('pinya.membre', string="Passadora")
    estiradora_id = fields.Many2one('pinya.membre', string="Estiradora")
    resp_xicalla_ids = fields.Many2many('pinya.membre', string="Responsable de xicalla")
    membres_count = fields.Integer(compute='_compute_membres_count', string='Total persones', store=True)
    pinya_count = fields.Integer(compute='_compute_membres_count', string='Persones pinya', store=True)
    tronc_count = fields.Integer(compute='_compute_membres_count', string='Persones tronc', store=True)

    actuacio_id = fields.Many2one(string="Actuació", comodel_name="pinya.actuacio")

    image = fields.Binary(
        "Photo", attachment=True,
        help="This field holds the image used as photo for the employee, limited to 1024x1024px.")

    @api.multi
    @api.depends('tronc_ids', 'tronc_ids.persones', 'pinya_ids', 'pinya_ids.persones', 'pinya_ids.rengles')
    def _compute_membres_count(self):
        for muix in self:
            tronc = muix.tronc_ids
            pinya = muix.pinya_ids
            t = sum(t.persones for t in tronc)
            p = sum(p.persones * p.rengles for p in pinya)
            muix.tronc_count = t
            muix.pinya_count = p
            muix.membres_count = t + p
