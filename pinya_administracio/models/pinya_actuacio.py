# -*- coding: utf-8 -*-
# (c) 2020 Miquel March <m.marchpuig@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, exceptions, _
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta


class PinyaActuacio(models.Model):
    """
    """
    _inherit = 'pinya.actuacio'

    preparatori_id = fields.Many2one(string="Preparatori", comodel_name="event.event")

