# -*- coding: utf-8 -*-
# (c) 2020 Miquel March <m.marchpuig@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, exceptions, _
from odoo.exceptions import ValidationError


class PinyaTronc(models.Model):
    _name = "pinya.tronc"
    _description = "Tronc"
    _order = "pis asc"

    plantilla = fields.Boolean('Plantilla', related="muixeranga_id.plantilla")

    pis = fields.Integer(string="Pis", index=True, required=True)
    tipus = fields.Selection([
        ('adulta', 'Adulta'),
        ('alsadora', 'Alçadora'),
        ('xicalla', 'Xicalla')
    ], string='Tipus', required=True, default='adulta')

    persones = fields.Integer('Persones per pis')
    muixeranga_id = fields.Many2one(string="Figura", comodel_name="pinya.muixeranga")
    membres_ids = fields.Many2many('pinya.membre', string="Membres")

