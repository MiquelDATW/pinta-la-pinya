# -*- coding: utf-8 -*-
# (c) 2020 Miquel March <m.marchpuig@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import models, fields, api, exceptions, _


class HrEmployeeAnthropometry(models.Model):
    """
    Faig herència d'esta classe afegir alçades de muscle i de braços
    """
    _inherit = 'hr.employee.anthropometry'

    alsada_muscle = fields.Integer(string="Alçada muscle")
    alsada_bras = fields.Integer(string="Alçada braços")

