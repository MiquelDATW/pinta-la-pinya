# -*- coding: utf-8 -*-
# (c) 2020 Miquel March <m.marchpuig@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, exceptions, _
from odoo.exceptions import ValidationError


class PinyaActuacio(models.Model):
    _name = "pinya.actuacio"
    _description = "Actuació o Assaig muixeranguer"
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

    membre_ids = fields.Many2many('hr.employee', string="Membres")
    muixeranga_ids = fields.One2many('pinya.muixeranga', 'actuacio_id', string="Muixerangues")
    membres_count = fields.Integer(compute='_compute_membres_count', string='Total persones', store=True)
    muixerangues_count = fields.Integer(compute='_compute_muixerangues_count', string='Total figures', store=True)

    @api.multi
    @api.depends('membre_ids')
    def _compute_membres_count(self):
        for actuacio in self:
            membres = actuacio.membre_ids
            actuacio.membres_count = len(membres)

    @api.multi
    @api.depends('muixeranga_ids')
    def _compute_muixerangues_count(self):
        for actuacio in self:
            muixeranga = actuacio.muixeranga_ids
            actuacio.muixerangues_count = len(muixeranga)

    def action_membres_import(self):
        view_form_id = self.env.ref('pinta_la_pinya.pinya_import_wizard_form_view').id
        action = {
            'type': 'ir.actions.act_window',
            'views': [(view_form_id, 'form')],
            'view_mode': 'form',
            'name': "Importar membres per a l'actuació",
            'target': 'new',
            'res_model': 'pinya.import.wizard',
            'context': {}
        }
        return action

    def pinya_muixeranga_wizard(self):
        view_form_id = self.env.ref('pinta_la_pinya.pinya_muixeranga_wizard_form_view').id
        tipus = self.tipus.replace("actuacio", "actuació")
        action = {
            'type': 'ir.actions.act_window',
            'views': [(view_form_id, 'form')],
            'view_mode': 'form',
            'name': "Afegir figures a l'{}".format(tipus),
            'target': 'new',
            'res_model': 'pinya.muixeranga.wizard',
            'context': {}
        }
        return action
