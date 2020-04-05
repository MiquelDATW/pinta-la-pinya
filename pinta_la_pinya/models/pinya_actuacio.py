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
    ], string='Tipus', required=True)

    estat = fields.Selection([
        ('draft', 'Esborrany'),
        ('preparat', 'Preparat'),
        ('fet', 'Fet')
    ], string='Estat', required=True, default='draft')

    membre_ids = fields.Many2many('hr.employee', string="Membres")
    muixeranga_ids = fields.One2many('pinya.muixeranga', 'actuacio_id', string="Muixerangues")
    membres_count = fields.Integer(compute='_compute_membres_count', string='Total persones', store=True)
    muixerangues_count = fields.Integer(compute='_compute_muixerangues_count', string='Total muixerangues', store=True)

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

    @api.model
    def default_get(self, fields_list):
        res = super(PinyaActuacio, self).default_get(fields_list)
        tipus = self.env.context.get('tipus', False)
        if bool(tipus):
            res['tipus'] = tipus
            if tipus == 'assaig':
                res['name'] = tipus.capitalize()
        return res

    @api.onchange('data')
    def onchange_data(self):
        tipus = self.tipus
        if tipus != 'assaig':
            return False
        data = self.data
        if not bool(data):
            return False
        data_str = str(data).replace('-', '/')
        self.name = tipus.capitalize() + ' ' + data_str

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

    def mostrar_muixerangues(self):
        view_tree_id = self.env.ref('pinta_la_pinya.view_muixeranga_tree').id
        view_form_id = self.env.ref('pinta_la_pinya.view_muixeranga_form').id
        domain = [('id', 'in', self.muixeranga_ids.ids)]
        action = {
            'type': 'ir.actions.act_window',
            'views': [(view_tree_id, 'tree'), (view_form_id, 'form')],
            'view_mode': 'form',
            'name': "Muixerangues",
            'target': 'current',
            'res_model': 'pinya.muixeranga',
            'context': {},
            'domain': domain,
        }
        return action

    def mostrar_membres(self):
        view_search_id = self.env.ref('pinta_la_pinya.hr_employee_membre_search').id
        view_tree_id = self.env.ref('pinta_la_pinya.hr_employee_membre_tree').id
        view_form_id = self.env.ref('hr.view_employee_form').id
        domain = [('id', 'in', self.membre_ids.ids)]
        action = {
            'type': 'ir.actions.act_window',
            'views': [(view_tree_id, 'tree'), (view_form_id, 'form')],
            'search_view_id': view_search_id,
            'view_mode': 'form',
            'name': "Membres",
            'target': 'current',
            'res_model': 'hr.employee',
            'context': {},
            'domain': domain,
        }
        return action

    def calcular_muixeranga(self):
        print(fields.Datetime.now())

