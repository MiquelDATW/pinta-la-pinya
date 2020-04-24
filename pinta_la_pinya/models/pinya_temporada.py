# -*- coding: utf-8 -*-
# (c) 2020 Miquel March <m.marchpuig@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, exceptions, _
from odoo.exceptions import ValidationError


class PinyaTemporada(models.Model):
    _name = "pinya.temporada"
    _description = "Temporada muixeranguera"
    _order = "temp_inici desc"

    name = fields.Char(string="Nom", index=True, required=True, translate=True)
    actual = fields.Boolean(string="Actual")
    temp_inici = fields.Date(string="Inici de la temporada")
    temp_final = fields.Date(string="Final de la temporada")
    notes = fields.Text(string="Altra informació")

    figura_ids = fields.Many2many('pinya.plantilla', string="Figures", compute='_compute_figures', store=True)

    muixeranga_ids = fields.One2many('pinya.muixeranga', 'temporada_id', string="Muixerangues")
    no_oficials_count = fields.Integer(string='Figures assajos', compute='_compute_muixerangues_count', store=True)
    oficials_count = fields.Integer(string='Figures oficials', compute='_compute_muixerangues_count', store=True)
    muixerangues_count = fields.Integer(string='Total figures', compute='_compute_muixerangues_count', store=True)

    actuacio_ids = fields.One2many('pinya.actuacio', 'temporada_id', string="Actuacions")
    actuacions_count = fields.Integer(string='Total actuacions', compute='_compute_actuacions_count', store=True)
    assajos_count = fields.Integer(string='Total assajos', compute='_compute_actuacions_count', store=True)

    @api.multi
    @api.depends('muixeranga_ids')
    def _compute_muixerangues_count(self):
        for temporada in self:
            muixeranga = temporada.muixeranga_ids
            no_oficials = muixeranga.filtered(lambda x: x.actuacio_id.tipus == 'assaig')
            oficials = muixeranga.filtered(lambda x: x.actuacio_id.tipus == 'actuacio')
            temporada.muixerangues_count = len(muixeranga)
            temporada.no_oficials_count = len(no_oficials)
            temporada.oficials_count = len(oficials)

    @api.multi
    @api.depends('actuacio_ids')
    def _compute_actuacions_count(self):
        for temporada in self:
            actuacio = temporada.actuacio_ids.filtered(lambda x: x.tipus == 'actuacio')
            assaig = temporada.actuacio_ids.filtered(lambda x: x.tipus == 'assaig')
            temporada.actuacions_count = len(actuacio)
            temporada.assajos_count = len(assaig)

    @api.multi
    @api.depends('muixeranga_ids', 'muixeranga_ids.plantilla_id')
    def _compute_figures(self):
        for temporada in self:
            actuacio = temporada.muixeranga_ids.filtered(lambda x: x.actuacio_id.tipus == 'actuacio')
            figures = actuacio.mapped('plantilla_id')
            temporada.figura_ids = [(6, 0, figures.sorted('name').ids)]

    def mostrar_oficials(self):
        res = self.mostrar_pinya_muixeranga('actuacio')
        return res

    def mostrar_no_oficials(self):
        res = self.mostrar_pinya_muixeranga('assaig')
        return res

    def mostrar_pinya_muixeranga(self, tipus):
        view_tree_id = self.env.ref('pinta_la_pinya.view_muixeranga_tree_all').id
        view_form_id = self.env.ref('pinta_la_pinya.view_muixeranga_form').id
        pinya_muixeranga = self.muixeranga_ids.filtered(lambda x: x.actuacio_id.tipus == tipus)
        domain = [('id', 'in', pinya_muixeranga.ids)]
        tipus2 = "Oficials" if tipus == 'actuacio' else "Assajos"
        name = "Muix. {} {}".format(tipus2, self.name)
        action = {
            'type': 'ir.actions.act_window',
            'views': [(view_tree_id, 'tree'), (view_form_id, 'form')],
            'view_mode': 'form',
            'name': name,
            'target': 'current',
            'res_model': 'pinya.muixeranga',
            'context': {},
            'domain': domain,
        }
        return action

    def mostrar_actuacions(self):
        res = self.mostrar_pinya_actuacio('actuacio')
        return res

    def mostrar_assajos(self):
        res = self.mostrar_pinya_actuacio('assaig')
        return res

    def mostrar_pinya_actuacio(self, tipus):
        view_tree_id = self.env.ref('pinta_la_pinya.view_actuacio_tree').id
        view_form_id = self.env.ref('pinta_la_pinya.view_actuacio_form').id
        actuacions = self.actuacio_ids.filtered(lambda x: x.tipus == tipus)
        domain = [('id', 'in', actuacions.ids)]
        tipus2 = "Actuacions" if tipus == 'actuacio' else "Assajos"
        name = "{} {}".format(tipus2, self.name)
        action = {
            'type': 'ir.actions.act_window',
            'views': [(view_tree_id, 'tree'), (view_form_id, 'form')],
            'view_mode': 'form',
            'name': name,
            'target': 'current',
            'res_model': 'pinya.actuacio',
            'context': {},
            'domain': domain,
        }
        return action

    @api.model
    def create(self, vals):
        if 'actual' in vals and vals.get('actual', False):
            altra_actual = self.env['pinya.temporada'].search([('actual', '=', True)])
            if bool(altra_actual):
                raise ValidationError("Ja hi ha una temporada actual❗")
        res = super(PinyaTemporada, self).create(vals)
        return res

    @api.multi
    def unlink(self):
        res = super(PinyaTemporada, self).unlink()
        return res

    @api.multi
    def write(self, vals):
        if 'actual' in vals and vals.get('actual', False):
            altra_actual = self.env['pinya.temporada'].search([('actual', '=', True)])
            if bool(altra_actual):
                raise ValidationError("Ja hi ha una temporada actual❗")
        res = super(PinyaTemporada, self).write(vals)
        return res

