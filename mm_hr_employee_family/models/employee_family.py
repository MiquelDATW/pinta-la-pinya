# -*- coding: utf-8 -*-
# (c) 2020 Miquel March <m.marchpuig@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, exceptions, _
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
from datetime import datetime


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    family_ids = fields.One2many('hr.employee.family', 'employee_id', string="Família")


class HrEmployeeFamily(models.Model):
    _name = 'hr.employee.family'
    _description = 'HR Employee Family'
    _order = 'employee_id'

    name = fields.Char(string="Nom", index=True, required=True, translate=True, default=".")

    employee_id = fields.Many2one('hr.employee', string="Employee", required=True)
    is_relation = fields.Boolean(string="Employee relationship", default=True)
    family_name = fields.Char(string="Relationship with")
    family_id = fields.Many2one('hr.employee', string="Relationship with")
    inverse_family_id = fields.Many2one('hr.employee.family', string="Inverse family", readonly=True)

    relation_id = fields.Many2one('hr.employee.relation', string='Relation', required=True)

    family_country_id = fields.Many2one(
        'res.country', 'Nationality (Country)', groups="hr.group_hr_user")
    family_gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ], string="Gender", groups="hr.group_hr_user", default="male")
    family_marital = fields.Selection([
        ('single', 'Single'),
        ('married', 'Married'),
        ('cohabitant', 'Legal Cohabitant'),
        ('widower', 'Widower'),
        ('divorced', 'Divorced')
    ], string='Marital Status', groups="hr.group_hr_user", default='single')
    family_birthday = fields.Date('Date of Birth', groups="hr.group_hr_user")
    family_job = fields.Char('Job')
    family_phone_number = fields.Char('Phone Number')
    family_notes = fields.Text('Notes')

    _sql_constraints = [
        ('employee_relation_uniq', 'unique(employee_id, family_id)',
         "These employees already have a family relationship❗"),
    ]

    @api.onchange('is_relation')
    def onchange_is_relation(self):
        self.family_id = False
        self.family_name = False

    @api.onchange('family_id')
    def onchange_relation(self):
        family = self.family_id
        if bool(family):
            self.family_name = family.name
            self.family_country_id = family.country_id
            self.family_gender = family.gender
            self.family_marital = family.marital
            self.family_birthday = family.birthday
            self.family_job = family.job_id.name
            self.family_phone_number = family.address_home_id.phone or family.address_home_id.mobile
        else:
            self.family_name = False
            self.family_country_id = False
            self.family_gender = False
            self.family_marital = False
            self.family_birthday = False
            self.family_job = False
            self.family_phone_number = False

    @api.multi
    def unlink(self):
        familys = self.filtered(lambda x: bool(x.inverse_family_id))
        for family in familys:
            inverse_family = family.inverse_family_id
            inverse_family.inverse_family_id = False
            inverse_family.unlink()
        res = super(HrEmployeeFamily, self).unlink()
        return res

    @api.model
    def create(self, vals):
        family = vals.get('family_id', False)
        family_name = vals.get('family_name', False)
        relation = vals.get('relation_id', False)
        relation = self.env['hr.employee.relation'].browse(relation)
        employee = vals.get('employee_id', False)
        is_relation = vals.get('is_relation', False)

        if employee == family and is_relation:
            raise ValidationError("It's not possible a family relationship with oneself❗")

        if relation and family and is_relation:
            family = self.env['hr.employee'].browse(family)
            name = relation.name + " of " + family.name
            data = {
                'name': name,
                'family_name': family.name,
                'family_country_id': family.country_id.id,
                'family_gender': family.gender,
                'family_marital': family.marital,
                'family_birthday': family.birthday,
                'family_job': family.job_id.name,
                'family_phone_number': family.address_home_id.phone or family.address_home_id.mobile,
            }
            vals.update(data)
        elif relation and family_name and not is_relation:
            name = relation.name + " of " + family_name
            vals.update({'name': name})

        res = super(HrEmployeeFamily, self).create(vals)

        is_inverse = res.inverse_family_id
        is_relation = res.is_relation
        if not is_inverse and is_relation:
            family = res.family_id.id
            employee = res.employee_id.id
            inverse_relation = res.relation_id.inverse_relation_id.id
            new_vals = {
                'employee_id': family,
                'family_id': employee,
                'is_relation': True,
                'relation_id': inverse_relation,
                'inverse_family_id': res.id,
                'name': '.',
            }
            is_inverse = res.create(new_vals)
            res.inverse_family_id = is_inverse.id
        return res

    @api.multi
    def write(self, vals):
        family = 'family_id' in vals
        employee = 'employee_id' in vals
        relation = 'relation_id' in vals
        is_relation = 'is_relation' in vals
        if employee or family or relation or is_relation:
            raise ValidationError("It's not possible to modify a family relationship❗\n"
                                  "Try erasing the current one and creating another.")

        res = super(HrEmployeeFamily, self).write(vals)
        return res

