# -*- coding: utf-8 -*-
# Copyright (C) 2018 Brainbean Apps (https://brainbeanapps.com)
# (c) 2020 Miquel March <m.marchpuig@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import models, fields, api, exceptions, _


class HrEmployeeRelation(models.Model):
    _name = 'hr.employee.relation'
    _description = 'HR Employee Relation'
    _order = 'kinship_degree'

    name = fields.Char(string='Relation', required=True, translate=True)
    kinship_degree = fields.Integer("Degree of kinship", required=True)
    inverse_relation_id = fields.Many2one('hr.employee.relation', string='Inverse relation')

