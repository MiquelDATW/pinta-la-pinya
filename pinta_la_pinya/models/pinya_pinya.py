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
    posicio_ids = fields.One2many('pinya.pinya.line', 'pinya_id', string="Posicions de pinya", copy=True)

    @api.multi
    @api.depends('posicio_ids')
    def _compute_membres_count(self):
        for pinya in self:
            posicio = pinya.posicio_ids
            pinya.persones = len(posicio)


class PinyaPinyaLine(models.Model):
    _name = "pinya.pinya.line"
    _description = "Posició de la pinya d'una muixeranga"
    _order = "rengle asc"

    name = fields.Char(string="Nom", index=True)
    plantilla = fields.Boolean('Plantilla', related="pinya_id.plantilla")
    cordo = fields.Integer(string="Cordó", related="pinya_id.cordo")
    rengle = fields.Integer(string="Rengle", index=True, required=True)

    pinya_id = fields.Many2one(string="Pinya", comodel_name="pinya.pinya")
    muixeranga_id = fields.Many2one(string="Figura", comodel_name="pinya.muixeranga",
                                    related="pinya_id.muixeranga_id")
    actuacio_id = fields.Many2one(string="Actuació", comodel_name="pinya.actuacio",
                                  related="pinya_id.muixeranga_id.actuacio_id")
    data = fields.Date(string="Data", related="pinya_id.muixeranga_id.actuacio_id.data")

    posicio_id = fields.Many2one('pinya.posicio', string="Posició",
                                 domain="[('tipus', '=', 'pinya')]")

    @api.onchange('posicio_id')
    def onchange_posicio_id(self):
        self.name = self.posicio_id.name

    @api.model
    def create(self, vals):
        posicio = vals.get('posicio_id', False)
        if posicio:
            vals['name'] = self.env['pinya.posicio'].browse(posicio).name
            pinya = vals.get('pinya_id', False)
            pinya = self.env['pinya.pinya'].browse(pinya)
            vals['muixeranga_id'] = pinya.muixeranga_id.id
        res = super(PinyaPinyaLine, self).create(vals)
        return res

    @api.multi
    def write(self, vals):
        if 'muixeranga_id' in vals and not vals.get('muixeranga_id', False):
            vals['muixeranga_id'] = self.muixeranga_id.id
        res = super(PinyaPinyaLine, self).write(vals)
        return res
