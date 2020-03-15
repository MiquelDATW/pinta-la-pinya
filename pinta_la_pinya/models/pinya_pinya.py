# -*- coding: utf-8 -*-
# (c) 2020 Miquel March <m.marchpuig@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, exceptions, _
from odoo.exceptions import ValidationError


class PinyaPinya(models.Model):
    _name = "pinya.pinya"
    _description = "Pinya d'una muixeranga"
    _order = "cordo asc"

    plantilla = fields.Boolean('Plantilla', related="muixeranga_id.plantilla")

    cordo = fields.Integer(string="Cordó", index=True, required=True)
    rengles = fields.Integer(string="Rengles", required=True)

    persones = fields.Integer(compute='_compute_membres_count', string='Persones per rengle', store=True)
    muixeranga_id = fields.Many2one(string="Figura", comodel_name="pinya.muixeranga")
    posicio_ids = fields.One2many('pinya.pinya.posicio', 'pinya_id', string="Posicions de pinya", copy=True)
    membre_ids = fields.Many2many('pinya.membre', string="Membres")

    @api.multi
    @api.depends('posicio_ids')
    def _compute_membres_count(self):
        for pinya in self:
            posicio = pinya.posicio_ids
            pinya.persones = len(posicio)
