# -*- coding: utf-8 -*-
# (c) 2020 Miquel March <m.marchpuig@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, exceptions, _


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


class PinyaActuacio(models.Model):
    _inherit = "pinya.actuacio"

    missatge_enviat = fields.Boolean(string="Missatge enviat")

    def telegram_msg(self):
        view_form_id = self.env.ref('pinya_telegram.view_telegram_wizard_form').id
        partner = self.env.user.company_id.partner_id
        name = "Enviar telegram a {}".format(partner.name)
        model = "telegram.wizard"
        ctx = dict(self.env.context)
        ctx.update({'partner_id': partner.id})
        action = _get_wizard(view_form_id, name, model, ctx)
        return action

    @api.multi
    def write(self, vals):
        obert = vals.get('missatge_enviat', False)
        if bool(obert):
            vals.update({'obert': True})

        res = super(PinyaActuacio, self).write(vals)
        return res
