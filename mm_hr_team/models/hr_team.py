# -*- coding: utf-8 -*-
# (c) 2020 Miquel March <m.marchpuig@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, exceptions, _


class HrTeam(models.Model):
    _name = 'hr.team'
    _description = "HR Team"
    _order = "name"

    name = fields.Char(string='Name', required=True, translate=True)
    active = fields.Boolean(string='Active', default=True)

    date_from = fields.Date(string='Start Date')
    date_to = fields.Date(string='End Date')
    notes = fields.Text(string='Notes')

    manager_id = fields.Many2one('hr.employee', string='Manager', track_visibility='onchange')
    team_member_ids = fields.Many2many('hr.employee', string='Members')
    team_department_ids = fields.Many2many('hr.department', string='Departments',
                                           compute="_compute_team_departments", store=True)
    department_id = fields.Many2one('hr.department', string='Manager department', readonly=True,
                                    related="manager_id.department_id", store=True)
    member_count = fields.Integer(string='Member count', compute="_compute_member_count", store=True)

    @api.multi
    @api.depends('team_member_ids')
    def _compute_member_count(self):
        teams = self.filtered(lambda x: bool(x.team_member_ids))
        for team in teams:
            team.member_count = len(team.team_member_ids.ids)

    @api.multi
    @api.depends('team_member_ids', 'team_member_ids.department_id')
    def _compute_team_departments(self):
        teams = self.filtered(lambda x: bool(x.team_member_ids))
        for team in teams:
            deps = team.team_member_ids.mapped('department_id')
            team.team_department_ids = [(6, 0, deps.ids)]

    @api.model
    def create(self, vals):
        res = super(HrTeam, self).create(vals)
        return res

    @api.multi
    def write(self, vals):
        res = super(HrTeam, self).write(vals)
        return res

