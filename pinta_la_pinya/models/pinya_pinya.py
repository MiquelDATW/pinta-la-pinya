# -*- coding: utf-8 -*-
# (c) 2020 Miquel March <m.marchpuig@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, exceptions, _
from odoo.exceptions import ValidationError


class PinyaPinya(models.Model):
    _name = "pinya.pinya"
    _description = "Pinya"
    _order = "cordo asc"

    plantilla = fields.Boolean('Plantilla', related="muixeranga_id.plantilla")

    cordo = fields.Integer(string="Cordó", index=True, required=True)
    rengles = fields.Integer(string="Regles", required=True)

    persones = fields.Integer('Persones per rengle')
    muixeranga_id = fields.Many2one(string="Figura", comodel_name="pinya.muixeranga")
    membres_ids = fields.Many2many('pinya.membre', string="Membres")

