# -*- coding: utf-8 -*-
# (c) 2020 Miquel March <m.marchpuig@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from odoo import api, models, fields

_logger = logging.getLogger(__name__)


class TelegramWizard(models.TransientModel):
    _name = "telegram.wizard"

    partner_id = fields.Many2one('res.partner', string='Contacte', required=True)
    telegram_id = fields.Many2one("res.telegram", related="partner_id.telegram_id", string="Telegram")
    msg_text = fields.Text(string="Text del missatge", required=True)

    msg_image = fields.Binary("Imatge del missatge", attachment=True, help="Limitat a 1024x1024px.")

    @api.model
    def default_get(self, fields_list):
        res = super(TelegramWizard, self).default_get(fields_list)
        partner = self.env.context.get('partner_id')
        res.update({'partner_id': partner})
        return res

    def telegram_btn(self):
        telegram_obj = self.env['res.telegram']

        msg = self.msg_text
        partner = self.partner_id.id
        imatge = self.msg_image if bool(self.msg_image) else False
        res = telegram_obj.send_telegram(msg, partner, imatge)

        return res

