# -*- coding: utf-8 -*-
# (c) 2020 Miquel March <m.marchpuig@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import pytz
import logging
from odoo import api, models, fields
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

import requests, json

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
        convocar = self.env.context.get('convocar', False)
        if convocar and convocar == 'assaig':
            msg_text = self.env.user.company_id.msg_assaig
        elif convocar and convocar == 'actuacio':
            msg_text = self.env.user.company_id.msg_actuac
        else:
            msg_text = ""
        if bool(msg_text):
            model_id = self.env.context.get('active_model')
            active_id = self.env.context.get('active_id')
            pinya = self.env[model_id].browse(active_id)

            weekDays = ("dilluns", "dimarts", "dimecres", "dijous", "divendres", "dissabte", "diumenge")
            xicalla = fields.Datetime.from_string(pinya.data_xicalla)
            general = fields.Datetime.from_string(pinya.data_general)
            if bool(xicalla):
                h_xicalla = fields.Datetime.from_string(self._utc_to_tz(str(xicalla))).strftime("%H:%M")
                msg_text = msg_text.replace("{xicalla}", h_xicalla)
            if bool(general):
                h_general = fields.Datetime.from_string(self._utc_to_tz(str(general))).strftime("%H:%M")
                msg_text = msg_text.replace("{general}", h_general)

            data = fields.Datetime.from_string(pinya.data_inici)
            if bool(data):
                d_data = data.strftime("%d/%m/%Y")
                d_dia = weekDays[data.weekday()]
                msg_text = msg_text.replace("{data}", d_data).replace("{dia}", d_dia)
                if not bool(xicalla) and not bool(general):
                    h_hora = fields.Datetime.from_string(self._utc_to_tz(str(data))).strftime("%H:%M")
                    msg_text = msg_text.replace("en el lloc i hora habituals;", "a les")
                    msg_text = msg_text.replace("{xicalla} xicalla, {general} general", h_hora)
            elif bool(xicalla) or bool(general):
                d1 = xicalla if bool(xicalla) else False
                d2 = general if bool(general) else False
                inici = (d1 if d1 <= d2 else d2) if d1 and d2 else (d1 if d1 else d2)
                d_data = inici.strftime("%d/%m/%Y")
                d_dia = weekDays[inici.weekday()]
                msg_text = msg_text.replace("en el lloc i hora habituals;", "a les")
                msg_text = msg_text.replace("{data}", d_data).replace("{dia}", d_dia)

            res.update({'msg_text': msg_text})
        return res

    def telegram_btn(self):
        telegram_obj = self.env['res.telegram']

        msg = self.msg_text
        partner = self.partner_id.id
        imatge = self.msg_image if bool(self.msg_image) else False
        res = telegram_obj.send_telegram(msg, partner, imatge)

        convocar = self.env.context.get('convocar', False)
        if convocar:
            model_id = self.env.context.get('active_model')
            active_id = self.env.context.get('active_id')
            pinya = self.env[model_id].browse(active_id)
            pinya.missatge_enviat = True

        # headers = {
        #     'content-type': 'application/x-www-form-urlencoded',
        #     'charset': 'utf-8'
        # }
        #
        # data = {
        #     'login': 'admin',
        #     'password': '1234',
        #     'db': 'pinya_0428'
        # }
        # base_url = 'http://localhost:8069'
        #
        # req = requests.get('{}/api/auth/token'.format(base_url), data=data, headers=headers)
        #
        # content = json.loads(req.content.decode('utf-8'))
        #
        # headers['access-token'] = content.get('access_token')  # add the access token to the header
        # print(headers)

        return res

    @api.model
    def _utc_to_tz(self, date):
        date_dt = datetime.strptime(date, DEFAULT_SERVER_DATETIME_FORMAT)
        tz_info = fields.Datetime.context_timestamp(self, date_dt).tzinfo
        tz = pytz.timezone('Europe/Madrid')
        date_dt = date_dt.replace(tzinfo=pytz.UTC).astimezone(tz).replace(tzinfo=None)
        return date_dt.strftime(DEFAULT_SERVER_DATETIME_FORMAT)

