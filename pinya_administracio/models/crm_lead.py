# -*- coding: utf-8 -*-
# (c) 2020 Miquel March <m.marchpuig@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, exceptions, _
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta


class CrmLead(models.Model):
    """
    """
    _inherit = 'crm.lead'

    data_inici = fields.Datetime(string="Data i hora inici", required=True)
    data_final = fields.Datetime(string="Data i hora final", required=True)



