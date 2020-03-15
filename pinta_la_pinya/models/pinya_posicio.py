# -*- coding: utf-8 -*-
# (c) 2020 Miquel March <m.marchpuig@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, exceptions, _


class PinyaPosicio(models.Model):
    _name = "pinya.posicio"
    _description = "Posició en una muixeranga"
    _order = "name asc"

    name = fields.Char(string="Posició", index=True, required=True, translate=True)
    tipus = fields.Selection([
        ('pinya', 'Pinya'),
        ('tronc', 'Tronc'),
        ('xicalla', 'Xicalla')
    ], string='Tipus', required=True)

