# -*- coding: utf-8 -*-
# (c) 2020 Miquel March <m.marchpuig@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, exceptions, _
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta


class EventEvent(models.Model):
    _inherit = 'event.event'

    actuacio_id = fields.Many2one(string="Actuació", comodel_name="pinya.actuacio")
    zip_id = fields.Many2one('res.better.zip', 'Ubicació',  related='address_id.zip_id', store=True)

    @api.model
    def create(self, vals):
        res = super(EventEvent, self).create(vals)
        actuacio = vals.get('actuacio_id', False)
        if actuacio:
            actuacio = self.env['pinya.actuacio'].browse(actuacio)
            actuacio.event_id = res.id
        return res

    @api.multi
    def write(self, vals):
        res = super(EventEvent, self).write(vals)
        if 'actuacio_id' in vals:
            actuacio = vals.get('actuacio_id', False)
            if actuacio:
                actuacio = self.env['pinya.actuacio'].browse(actuacio)
                if not actuacio.event_id:
                    actuacio.event_id = self.id
            else:
                act_obj = self.env['pinya.actuacio']
                actuacio = act_obj.search([('event_id', '=', self.id)])
                if actuacio:
                    actuacio.event_id = False
        return res

