# -*- coding: utf-8 -*-
# (c) 2020 Miquel March <m.marchpuig@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import string
import random
import logging
from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def post_init_hook(cr, registry):

    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})

        root = env.ref('hr.employee_root')
        root.muixeranguera = False

        main_partner = env.ref('base.main_partner')
        main_partner.colla = True
        main_partner.assaig_hora_inici = 10
        main_partner.assaig_hora_final = 12

