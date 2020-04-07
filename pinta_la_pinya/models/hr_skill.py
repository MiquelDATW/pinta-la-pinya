# -*- coding: utf-8 -*-
# (c) 2020 Miquel March <m.marchpuig@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, exceptions, _
from odoo.exceptions import ValidationError
from datetime import datetime
from dateutil.relativedelta import relativedelta


class HrSkill(models.Model):
    _inherit = 'hr.skill'
    _order = 'tipus desc, name asc'

    tipus = fields.Selection([
        ('pinya', 'Pinya'),
        ('tronc', 'Tronc')
    ], string='Tipus', default="pinya", required=True)

    employee_level_ids = fields.One2many('hr.employee.level', 'skill_id', string="Employee Level")
    count_3stars = fields.Char(string="Membres experts", compute="_compute_millors", store=True)
    count_2stars = fields.Char(string="Membres avançats", compute="_compute_millors", store=True)
    count_1stars = fields.Char(string="Membres mitjans", compute="_compute_millors", store=True)

    @api.multi
    @api.depends('employee_level_ids', 'employee_level_ids.level')
    def _compute_millors(self):
        skills = self.filtered(lambda x: bool(x))
        for skill in skills:
            levels = skill.employee_level_ids
            l3 = len(levels.filtered(lambda x: x.level == '3'))
            skill.count_3stars = (str(l3) + ' ⭐⭐⭐') if l3 > 0 else ''
            l2 = len(levels.filtered(lambda x: x.level == '2'))
            skill.count_2stars = (str(l2) + ' ⭐⭐') if l2 > 0 else ''
            l1 = len(levels.filtered(lambda x: x.level == '1'))
            skill.count_1stars = (str(l1) + ' ⭐') if l1 > 0 else ''

    def employee_skill(self):
        view_tree_id = self.env.ref('pinta_la_pinya.view_hr_employee_skill_tree').id
        view_form_id = self.env.ref('pinta_la_pinya.view_hr_employee_skill_form').id
        domain = [('id', 'in', self.employee_skill_ids.ids)]
        action = {
            'type': 'ir.actions.act_window',
            'views': [(view_tree_id, 'tree'), (view_form_id, 'form')],
            'view_mode': 'form',
            'name': "Posicions nivell",
            'target': 'current',
            'res_model': 'hr.employee.skill',
            'context': {},
            'domain': domain,
        }
        return action

    def employee_level(self):
        view_tree_id = self.env.ref('pinta_la_pinya.view_hr_employee_level_tree').id
        view_form_id = self.env.ref('pinta_la_pinya.view_hr_employee_level_form').id
        domain = [('id', 'in', self.employee_level_ids.ids)]
        action = {
            'type': 'ir.actions.act_window',
            'views': [(view_tree_id, 'tree'), (view_form_id, 'form')],
            'view_mode': 'form',
            'name': "Membres nivell",
            'target': 'current',
            'res_model': 'hr.employee.level',
            'context': {},
            'domain': domain,
        }
        return action


class HrEmployeeSkill(models.Model):
    _inherit = 'hr.employee.skill'
    _order = 'level desc, count_sismesos desc, employee_id'

    active = fields.Boolean('Active', related='employee_id.active', default=True, store=True)
    name = fields.Char(string="Nom", index=True, required=True, translate=True)
    tecnica = fields.Selection([
        ('0', 'Inicial'),
        ('1', 'Mitjana'),
        ('2', 'Avançada'),
        ('3', 'Experta'),
    ], string='Tècnica', default="1", required=True)
    count_total = fields.Integer(string="Figures total", compute="_compute_figures", store=True)
    count_sismesos = fields.Integer(string="Figures 6 mesos", compute="_compute_figures", store=True)

    @api.multi
    def _compute_figures(self):
        skills = self.filtered(lambda x: bool(x))
        today = datetime.today().date()
        m6 = str(today - relativedelta(months=6))
        for skill in skills:
            employee = skill.employee_id
            posicio = skill.skill_id
            if posicio.tipus == "pinya":
                total_raw = employee.muixeranga_pinya_ids
            else:
                total_raw = employee.muixeranga_tronc_ids
            total = total_raw.filtered(lambda x: x.posicio_id.id == posicio.id and x.actuacio_id.estat == 'fet')
            sismesos = total.filtered(lambda x: x.actuacio_id.data > m6)

            skill.count_total = len(total)
            skill.count_sismesos = len(sismesos)

    @api.model
    def create(self, vals):
        skill = vals.get('skill_id', False)
        if not skill:
            raise ValidationError("Cal que hi haja una posició❗")

        level = vals.get('level', False)
        if not level:
            raise ValidationError("Cal que hi haja un nivell❗")

        name = self.env['hr.skill'].browse(skill).name
        star = level.replace('0', '').replace('1', ' ⭐').replace('2', ' ⭐⭐').replace('3', ' ⭐⭐⭐')

        vals['name'] = name + star
        res = super(HrEmployeeSkill, self).create(vals)

        emp_level_obj = self.env['hr.employee.level']
        vals_level = {
            'name': res.employee_id.name + star,
            'employee_skill_id': res.id,
        }
        emp_level_obj.create(vals_level)
        return res

    @api.multi
    def write(self, vals):
        if vals.get('level', False):
            star = vals.get('level').replace('0', '').replace('1', ' ⭐').replace('2', ' ⭐⭐').replace('3', ' ⭐⭐⭐')
            name = self.skill_id.name
            vals['name'] = name + star

            emp_level = self.env['hr.employee.level'].search([('employee_id', '=', self.employee_id.id), ('skill_id', '=', self.skill_id.id)])
            data_level = {
                'name': self.employee_id.name + star,
            }
            emp_level.write(data_level)
        res = super(HrEmployeeSkill, self).write(vals)
        return res


class HrEmployeeLevel(models.Model):
    _name = 'hr.employee.level'
    _order = 'level desc, count_sismesos desc, employee_id'

    active = fields.Boolean('Active', related='employee_skill_id.active', default=True, store=True)
    name = fields.Char(string="Nom", index=True, required=True, translate=True)
    employee_skill_id = fields.Many2one('hr.employee.skill', string="Membre/habilitat")

    employee_id = fields.Many2one('hr.employee', string="Membre", related="employee_skill_id.employee_id", store=True)
    skill_id = fields.Many2one('hr.skill', string="Habilitat", related="employee_skill_id.skill_id", store=True)
    level = fields.Selection(string='Nivell', related="employee_skill_id.level", store=True)
    tecnica = fields.Selection(string="Tècnica", related="employee_skill_id.tecnica", store=True)
    count_total = fields.Integer(string="Figures total", related="employee_skill_id.count_total", store=True)
    count_sismesos = fields.Integer(string="Figures 6 mesos", related="employee_skill_id.count_sismesos", store=True)

    _sql_constraints = [
        ('hr_employee_skill_uniq', 'unique(employee_id, skill_id)',
         "This employee already has that skill!"),
    ]

    @api.model
    def create(self, vals):
        res = super(HrEmployeeLevel, self).create(vals)
        return res

    @api.multi
    def write(self, vals):
        res = super(HrEmployeeLevel, self).write(vals)
        return res
