# -*- coding: utf-8 -*-
# (c) 2020 Miquel March <m.marchpuig@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, exceptions, _
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta


def _get_action(view_tree_id, view_form_id, view_search_id, name, model, domain, ctx):
    action = {
        'type': 'ir.actions.act_window',
        'views': [(view_tree_id, 'tree'), (view_form_id, 'form')],
        'search_view_id': view_search_id,
        'view_mode': 'form',
        'name': name,
        'target': 'current',
        'res_model': model,
        'context': ctx,
        'domain': domain,
    }
    return action


class EventEvent(models.Model):
    """
    Faig herència d'esta classe per gastar-la per concentrat actuacions i assajos preparatoris.
    """
    _inherit = 'event.event'

    assaig_ids = fields.One2many(comodel_name="pinya.actuacio",
                                 inverse_name="preparatori_id",
                                 string="Assajos preparatoris")
    assaig_count = fields.Integer("Assajos", compute="_compute_assaig_count", store=True)

    @api.multi
    @api.depends('assaig_ids')
    def _compute_assaig_count(self):
        """
        """
        events = self.filtered(lambda x: bool(x.actuacio_id))
        for event in events:
            event.assaig_count = len(event.assaig_ids.ids)

    def action_assajos_event(self):
        """
        Funció per mostrar assajos de l'esdeveniment
        """
        view_search_id = self.env.ref('pinya_tecnica.view_actuacio_filter').id
        view_tree_id = self.env.ref('pinya_tecnica.view_actuacio_tree').id
        view_form_id = self.env.ref('pinya_tecnica.view_actuacio_form').id
        name = "Assajos preparatoris"
        model = "pinya.actuacio"
        domain = [('tipus', '=', 'assaig'), ('id', 'in', self.assaig_ids.ids)]
        ctx = {}
        action = _get_action(view_tree_id, view_form_id, view_search_id, name, model, domain, ctx)
        return action

    @api.model
    def create(self, vals):
        """
        """
        res = super(EventEvent, self).create(vals)
        return res

    @api.multi
    def write(self, vals):
        """
        """
        res = super(EventEvent, self).write(vals)
        return res

