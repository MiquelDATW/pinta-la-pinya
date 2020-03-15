# -*- coding: utf-8 -*-
# (c) 2020 Miquel March <m.marchpuig@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, exceptions, _
from odoo.exceptions import ValidationError


class PinyaPinyaPosicio(models.Model):
    _name = "pinya.pinya.posicio"
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
    membre_id = fields.Many2one('pinya.membre', string="Membre")

    @api.onchange('posicio_id')
    def onchange_posicio_id(self):
        self.name = self.posicio_id.name

    @api.model
    def create(self, vals):
        posicio = vals.get('posicio_id', False)
        if posicio:
            vals['name'] = self.env['pinya.posicio'].browse(posicio).name
        res = super(PinyaPinyaPosicio, self).create(vals)
        return res
