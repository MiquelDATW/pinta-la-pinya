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
    _order = 'employee_id'

    name = fields.Char(string="Nom", index=True, required=True, translate=True, default=".")

    employee_id = fields.Many2one('hr.employee', string="Membre", required=True)
    is_relation = fields.Boolean(string="Relació dins la colla", default=True)
    relation_name = fields.Char(string="Relació amb")
    relation_id = fields.Many2one('hr.employee', string="Relació amb",
                                  domain=[('muixeranguera', '=', True)])

    FAMILY_SELECTION = [
        ('parella', 'És parella de'),
        ('mare_filla', 'És mare de'),
        ('filla_mare', 'És filla de'),
        ('germana', 'És germana de'),
        ('avia_neta', 'És àvia de'),
        ('neta_avia', 'És neta de'),
        ('tia_neboda', 'És tia de'),
        ('neboda_tia', 'És neboda de'),
        ('cosina', 'És cosina de')]

    family = fields.Selection(FAMILY_SELECTION,
                              string='Relació', required=True,
                              help="Relació familiar entre A i B.")

    inverse_family = fields.Selection(FAMILY_SELECTION,
                                      string='Relació inversa', readonly=True,
                                      help="Relació inversa entre A i B.")

    _sql_constraints = [
        ('employee_relation_uniq', 'unique(employee_id, relation_id)',
         "Aquestes membres ja tenen una relació familiar❗"),
    ]

    @api.onchange('is_relation')
    def onchange_is_relation(self):
        self.relation_name = False
        self.relation_id = False

    @api.onchange('relation_id')
    def onchange_relation(self):
        relation = self.relation_id
        if bool(relation):
            self.relation_name = relation.name
        else:
            self.relation_name = False

    @api.model
    def default_get(self, fields_list):
        res = super(HrEmployeeFamily, self).default_get(fields_list)
        res.update({'employee_id': self.env.context.get('employee_id')})
        return res

    @api.multi
    def unlink(self):
        if self.relation_id:
            is_inverse = self.search(
                [('employee_id', '=', self.relation_id.id), ('relation_id', '=', self.employee_id.id)])
            if is_inverse:
                is_inverse.relation_id = False
                is_inverse.unlink()
        res = super(HrEmployeeFamily, self).unlink()
        return res

    @api.model
    def create(self, vals):
        employee = vals.get('employee_id', False)
        relation = vals.get('relation_id', False)
        if employee == relation:
            raise ValidationError("No és possible tindre una relació con una mateixa❗")

        family = vals.get('family', False)
        if family:
            family_ = family.split('_')
            if len(family_) == 1:
                inv_family = family_[0]
            else:
                inv_family = family_[1] + '_' + family_[0]
            vals.update({'inverse_family': inv_family})
        relation_name = vals.get('relation_name', False)
        if family and relation_name:
            new_f = family or self.family or ''
            new_name = relation_name or self.relation_name or ''
            new_f2 = new_f.replace('parella', 'És parella de').\
                replace('mare_filla', 'És mare de').\
                replace('filla_mare', 'És filla de').\
                replace('germana', 'És germana de').\
                replace('avia_neta', 'És àvia de').\
                replace('neta_avia', 'És neta de').\
                replace('tia_neboda', 'És tia de').\
                replace('neboda_tia', 'És neboda de').\
                replace('cosina', 'És cosina de')
            name = new_f2 + " " + new_name
            vals.update({'name': name})
        res = super(HrEmployeeFamily, self).create(vals)

        rela = res.relation_id.id
        if rela:
            empl = res.employee_id.id
            inverse_family = res.inverse_family
            is_inverse = res.search([('employee_id', '=', rela), ('relation_id', '=', empl), ('family', '=', inverse_family)])
            if not is_inverse:
                new_vals = {
                    'family': inverse_family,
                    'employee_id': rela,
                    'relation_id': empl,
                    'is_relation': True,
                    'relation_name': res.employee_id.name,
                    'name': '.',
                }
                new_res = res.create(new_vals)
        return res

    @api.multi
    def write(self, vals):
        employee = vals.get('employee_id', False) or self.employee_id.id
        relation = vals.get('relation_id', False) or self.relation_id.id
        if employee == relation:
            raise ValidationError("No és possible tindre una relació con una mateixa❗")

        family = vals.get('family', False)
        if family:
            family_ = family.split('_')
            if len(family_) == 1:
                inv_family = family_[0]
            else:
                inv_family = family_[1] + '_' + family_[0]
            vals.update({'inverse_family': inv_family})
        relation_name = vals.get('relation_name', False)
        if family or relation_name:
            new_f = family or self.family
            new_name = relation_name or self.relation_name
            new_f2 = new_f.replace('parella', 'És parella de').\
                replace('mare_filla', 'És mare de').\
                replace('filla_mare', 'És filla de').\
                replace('germana', 'És germana de').\
                replace('avia_neta', 'És àvia de').\
                replace('neta_avia', 'És neta de').\
                replace('tia_neboda', 'És tia de').\
                replace('neboda_tia', 'És neboda de').\
                replace('cosina', 'És cosina de')
            name = new_f2 + " " + new_name
            vals.update({'name': name})
        res = super(HrEmployeeFamily, self).write(vals)

        rela = self.relation_id.id
        if rela:
            empl = self.employee_id.id
            inverse_family = self.inverse_family
            is_inverse = self.search([('employee_id', '=', rela), ('relation_id', '=', empl)])
            is_ok = (self.inverse_family == is_inverse.family) and (is_inverse.inverse_family == self.family) \
                    and (is_inverse.employee_id == self.relation_id) and (is_inverse.relation_id == self.employee_id)
            if is_ok:
                return res

            if is_inverse:
                new_vals = {
                    'family': inverse_family,
                    'employee_id': rela,
                    'relation_id': empl,
                    'is_relation': True,
                    'relation_name': self.employee_id.name,
                    'name': '.',
                }
                new_res = is_inverse.write(new_vals)
        return res


