# -*- coding: utf-8 -*-
# (c) 2020 Miquel March <m.marchpuig@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, exceptions, _
from odoo.exceptions import ValidationError


class PinyaTronc(models.Model):
    _name = "pinya.tronc"
    _description = "Tronc d'una muixeranga"
    _order = "pis asc"

    plantilla = fields.Boolean('Plantilla', related="muixeranga_id.plantilla")

    pis = fields.Integer(string="Pis", index=True, required=True)
    tipus = fields.Selection([
        ('adulta', 'Adulta'),
        ('alsadora', 'Alçadora'),
        ('xicalla', 'Xicalla')
    ], string='Tipus', required=True, default='adulta')

    persones = fields.Integer(compute='_compute_membres_count', string='Persones per pis', store=True)
    muixeranga_id = fields.Many2one(string="Figura", comodel_name="pinya.muixeranga")
    posicio_ids = fields.One2many('pinya.tronc.posicio', 'tronc_id', string="Posicions de tronc", copy=True)
    membre_ids = fields.Many2many('pinya.membre', string="Membres")
    present_ids = fields.Many2many('pinya.membre', string="Presents", related="muixeranga_id.actuacio_id.membre_ids")

    @api.multi
    @api.depends('posicio_ids')
    def _compute_membres_count(self):
        for pinya in self:
            posicio = pinya.posicio_ids
            pinya.persones = len(posicio)
