# -*- coding: utf-8 -*-
# (c) 2020 Miquel March <m.marchpuig@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, exceptions, _
from odoo.exceptions import ValidationError


class PinyaActuacio(models.Model):
    _name = "pinya.actuacio"
    _description = "Actuació"
    _order = "id desc"
    _inherit = ['mail.thread']

    name = fields.Char(string="Nom", index=True, required=True, translate=True)
    active = fields.Boolean(string="Actiu", default=True)
    data = fields.Date(string="Data")
    notes = fields.Text(string="Altra informació")
    zip_id = fields.Many2one(string="Lloc", comodel_name="res.better.zip")
    tipus = fields.Selection([
            ('actuacio', 'Actuació'),
            ('assaig', 'Assaig')
    ], string='Tipus', required=True, default='assaig')

    estat = fields.Selection([
        ('draft', 'Esborrany'),
        ('preparat', 'Preparat'),
        ('fet', 'Fet')
    ], string='Estat', required=True, default='draft')

    membres_ids = fields.Many2many('pinya.membre', string="Membres")
    muixerangues_ids = fields.One2many('pinya.muixeranga', 'actuacio_id', string="Muixerangues")
    membres_count = fields.Integer(compute='_compute_membres_count', string='Total persones', store=True)

    @api.multi
    @api.depends('membres_ids')
    def _compute_membres_count(self):
        for actuacio in self:
            membres = actuacio.membres_ids
            actuacio.membres_count = len(membres)


