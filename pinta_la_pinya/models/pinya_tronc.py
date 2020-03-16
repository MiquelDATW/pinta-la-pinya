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
    posicio_ids = fields.One2many('pinya.tronc.line', 'tronc_id', string="Posicions de tronc", copy=True)

    @api.multi
    @api.depends('posicio_ids')
    def _compute_membres_count(self):
        for pinya in self:
            posicio = pinya.posicio_ids
            pinya.persones = len(posicio)


class PinyaTroncLine(models.Model):
    _name = "pinya.tronc.line"
    _description = "Posició del tronc d'una muixeranga"
    _order = "pis asc"

    name = fields.Char(string="Nom", index=True)
    plantilla = fields.Boolean('Plantilla', related="tronc_id.plantilla")
    pis = fields.Integer(string="Pis", related="tronc_id.pis")

    tronc_id = fields.Many2one(string="Tronc", comodel_name="pinya.tronc")
    muixeranga_id = fields.Many2one(string="Muixeranga", comodel_name="pinya.muixeranga",
                                    related="tronc_id.muixeranga_id")
    actuacio_id = fields.Many2one(string="Actuació", comodel_name="pinya.actuacio",
                                  related="tronc_id.muixeranga_id.actuacio_id")
    data = fields.Date(string="Data", related="tronc_id.muixeranga_id.actuacio_id.data")

    posicio_id = fields.Many2one('pinya.posicio', string="Posició",
                                 domain="[('tipus', 'in', ['tronc', 'xicalla'])]")

    @api.onchange('posicio_id')
    def onchange_posicio_id(self):
        self.name = self.posicio_id.name

    @api.model
    def create(self, vals):
        posicio = vals.get('posicio_id', False)
        if posicio:
            vals['name'] = self.env['pinya.posicio'].browse(posicio).name
            tronc = vals.get('tronc_id', False)
            tronc = self.env['pinya.tronc'].browse(tronc)
            vals['muixeranga_id'] = tronc.muixeranga_id.id
        res = super(PinyaTroncLine, self).create(vals)
        return res

    @api.multi
    def write(self, vals):
        if 'muixeranga_id' in vals and not vals.get('muixeranga_id', False):
            vals['muixeranga_id'] = self.muixeranga_id.id
        res = super(PinyaTroncLine, self).write(vals)
        return res

