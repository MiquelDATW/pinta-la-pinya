# -*- coding: utf-8 -*-
# (c) 2020 Miquel March <m.marchpuig@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import statistics
import random
from odoo import models, fields, api, exceptions, _
from odoo.exceptions import ValidationError


class PinyaActuacio(models.Model):
    _inherit = "pinya.actuacio"

    def _get_company(self):
        res = self.env.user.company_id.partner_id
        return res

