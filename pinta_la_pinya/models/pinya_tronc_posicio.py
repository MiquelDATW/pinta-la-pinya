# -*- coding: utf-8 -*-
# (c) 2020 Miquel March <m.marchpuig@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, exceptions, _
from odoo.exceptions import ValidationError


class PinyaTroncPosicio(models.Model):
    _name = "pinya.tronc.posicio"
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
    membre_id = fields.Many2one('pinya.membre', string="Membre")
    membre_ids = fields.Many2many('pinya.membre', string="Membres", compute="_compute_membres")

    @api.onchange('posicio_id')
    def onchange_posicio_id(self):
        self.name = self.posicio_id.name

    @api.onchange('membre_id')
    def onchange_membre_id(self):
        print(self.membre_id)

    @api.multi
    def _compute_membres(self):
        self.ensure_one()
        membres = self.actuacio_id.membre_ids
        mem1 = self.muixeranga_id.pinya_ids.mapped('posicio_ids.membre_id')
        mem2 = self.muixeranga_id.tronc_ids.mapped('posicio_ids.membre_id')
        membres -= (mem1 + mem2)
        self.membre_ids = [(6, 0, membres.ids)]

    @api.model
    def create(self, vals):
        posicio = vals.get('posicio_id', False)
        if posicio:
            vals['name'] = self.env['pinya.posicio'].browse(posicio).name
        res = super(PinyaTroncPosicio, self).create(vals)
        return res

    @api.multi
    def write(self, vals):
        if 'muixeranga_id' in vals and not vals.get('muixeranga_id', False):
            vals['muixeranga_id'] = self.muixeranga_id
        res = super(PinyaTroncPosicio, self).write(vals)
        return res

