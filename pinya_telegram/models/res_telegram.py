# -*- coding: utf-8 -*-
# (c) 2020 Miquel March <m.marchpuig@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import telegram
import requests
from odoo import models, fields, api, exceptions, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


def _get_wizard(view_form_id, name, model, ctx):
    action = {
        'type': 'ir.actions.act_window',
        'views': [(view_form_id, 'form')],
        'view_mode': 'form',
        'name': name,
        'target': 'new',
        'res_model': model,
        'context': ctx,
    }
    return action


class ResCompany(models.Model):
    _inherit = "res.company"

    bot_token = fields.Char(string='Bot id', required=True)


class ResPartner(models.Model):
    _inherit = "res.partner"

    telegram_id = fields.Many2one("res.telegram", string="Telegram")

    def telegram_msg(self):
        view_form_id = self.env.ref('pinya_telegram.view_telegram_wizard_form').id
        name = "Enviar telegram a {}".format(self.name)
        model = "telegram.wizard"
        ctx = dict(self.env.context)
        ctx.update({'partner_id': self.id})
        action = _get_wizard(view_form_id, name, model, ctx)
        return action


class ResTelegram(models.Model):
    _name = 'res.telegram'
    _description = "Telegram"
    _order = "name"

    name = fields.Char(string='Nom', required=True, translate=True, default="Telegram")
    active = fields.Boolean(string='Active', default=True)

    notes = fields.Text(string='Notes')
    tipus = fields.Selection([
            ('personal', 'Personal'),
            ('canal', 'Canal'),
            ('grup', 'Grup de difusió')
    ], string='Tipus', required=True)

    partner_id = fields.Many2one('res.partner', string='Contacte', required=True)
    identificador = fields.Char(string='Chat id', required=True)

    _sql_constraints = [
        ("partner_unique", "UNIQUE (partner_id)", "Aquest contacte ja té Telegram❗"),
        ("identificador_unique", "UNIQUE (identificador)", "Aquest identificador ja existeix❗"),
    ]

    @api.model
    def default_get(self, fields_list):
        res = super(ResTelegram, self).default_get(fields_list)
        res.update({'partner_id': self.env.context.get('partner_id')})
        return res

    @api.model
    def create(self, vals):
        t_id = vals.get('identificador')
        name = vals.get('tipus').capitalize() + " Telegram: " + t_id[-4:-1] + t_id[-1]
        vals.update({'name': name})
        res = super(ResTelegram, self).create(vals)
        if bool(res):
            partner = res.partner_id
            partner.telegram_id = res.id
        return res

    @api.multi
    def write(self, vals):
        if vals.get('partner_id', False):
            old_partner = self.partner_id
        else:
            old_partner = False
        t_id = vals.get('identificador', False) or self.identificador
        tipus = (vals.get('tipus', False) or self.tipus).capitalize()
        name = tipus + " Telegram: " + t_id[-4:-1] + t_id[-1]
        vals.update({'name': name})
        res = super(ResTelegram, self).write(vals)
        if bool(old_partner):
            old_partner.telegram_id = False
            self.partner_id.telegram_id = self.id
        return res

    @api.multi
    def send_telegram(self, bot_message, partner_id):
        bot_token = self.env.user.company_id.bot_token
        if not bot_token:
            raise ValidationError("Error. No existeix l'identificador del Bot❗")

        partner = self.env['res.partner'].browse(partner_id)
        bot_chat_id = partner.telegram_id.identificador
        if not bot_chat_id:
            raise ValidationError("Error. El contacte no té identificador de Telegram❗")

        _logger.info('Enviant telegram a {} de {}'.format(partner.telegram_id.name, partner.name))

        bot = telegram.Bot(token=bot_token)
        res = bot.sendMessage(chat_id=bot_chat_id, text=bot_message)

        return res

