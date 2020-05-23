# -*- coding: utf-8 -*-
# (c) 2020 Miquel March <m.marchpuig@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, exceptions, _


def _get_action(view_tree_id, view_form_id, name, model, domain):
    action = {
        'type': 'ir.actions.act_window',
        'views': [(view_tree_id, 'tree'), (view_form_id, 'form')],
        'view_mode': 'form',
        'name': name,
        'target': 'current',
        'res_model': model,
        'context': {},
        'domain': domain,
    }
    return action


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    team_ids = fields.Many2many('hr.team', string='Teams')
    count_teams = fields.Integer(string="Equips total", compute="_compute_count_teams", store=True)

    @api.multi
    @api.depends('team_ids')
    def _compute_count_teams(self):
        muixeranguers = self.filtered(lambda x: bool(x.team_ids))
        for muixeranguer in muixeranguers:
            teams = muixeranguer.team_ids
            muixeranguer.count_teams = len(teams.ids)

    def pinya_teams(self):
        view_tree_id = self.env.ref('mm_hr_team.view_hr_team_tree').id
        view_form_id = self.env.ref('mm_hr_team.view_hr_team_form').id
        name = "Equips de {}".format(self.name)
        model = "hr.team"
        domain = [('id', 'in', self.team_ids.ids)]
        action = _get_action(view_tree_id, view_form_id, name, model, domain)
        return action

