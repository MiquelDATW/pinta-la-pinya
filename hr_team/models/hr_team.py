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
    member_ids = fields.Many2many('hr.employee', string='Members')
    department_ids = fields.Many2many('hr.department', string='Departments', compute="_compute_department", store=True)
    member_count = fields.Integer(string='Member count', compute="_compute_member_count", store=True)

    @api.multi
    @api.depends('member_ids')
    def _compute_member_count(self):
        teams = self.filtered(lambda x: bool(x.member_ids))
        for team in teams:
            team.member_count = len(team.member_ids.ids)

    @api.multi
    @api.depends('member_ids', 'member_ids.department_id')
    def _compute_department(self):
        teams = self.filtered(lambda x: bool(x.member_ids))
        for team in teams:
            depts = team.member_ids.mapped('department_id')
            team.department_ids = [(6, 0, depts.ids)]

    @api.model
    def create(self, vals):
        res = super(HrTeam, self).create(vals)
        return res

    @api.multi
    def write(self, vals):
        res = super(HrTeam, self).write(vals)
        return res

