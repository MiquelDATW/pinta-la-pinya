# -*- coding: utf-8 -*-
# (c) 2020 Miquel March <m.marchpuig@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, exceptions, _
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    event_id = fields.Many2one(string="Esdeveniment", comodel_name="event.event")

    @api.multi
    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        actuacions = self.env.ref('pinya_administracio.cat_muixeranga_actuacions')
        products = self.order_line.mapped('product_id').filtered(lambda x: x.categ_id.id == actuacions.id)
        if bool(products):
            event_obj = self.env['event.event']
            data = {
                'name': self.opportunity_id.name,
                'user_id': self.user_id.id,
                'organizer_id': self.partner_id.id,
                'date_begin': self.opportunity_id.data_inici,
                'date_end': self.opportunity_id.data_final,
            }
            event = event_obj.create(data)
            self.event_id = event.id

            actuacio_obj = self.env['pinya.actuacio']
            data = {
                'name': self.opportunity_id.name,
                'tipus': 'actuacio',
                'event_id': event.id,
            }
            actuacio_obj.create(data)

        return res

    @api.multi
    def write(self, vals):
        res = super(SaleOrder, self).write(vals)
        return res

    @api.model
    def create(self, vals):
        res = super(SaleOrder, self).create(vals)
        return res
