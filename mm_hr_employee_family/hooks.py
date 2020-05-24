# -*- coding: utf-8 -*-
# (c) 2020 Miquel March <m.marchpuig@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def post_init_hook(cr, registry):

    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})

        significant_other = env.ref('mm_hr_employee_family.relation_significant_other')
        significant_other.inverse_relation_id = significant_other.id

        parent = env.ref('mm_hr_employee_family.relation_parent')
        child = env.ref('mm_hr_employee_family.relation_child')
        parent.inverse_relation_id = child.id
        child.inverse_relation_id = parent.id

        sibling = env.ref('mm_hr_employee_family.relation_sibling')
        sibling.inverse_relation_id = sibling.id

        grandparent = env.ref('mm_hr_employee_family.relation_grandparent')
        grandchild = env.ref('mm_hr_employee_family.relation_grandchild')
        grandparent.inverse_relation_id = grandchild.id
        grandchild.inverse_relation_id = grandparent.id

        uncle_aunt = env.ref('mm_hr_employee_family.relation_uncle_aunt')
        nephew_niece = env.ref('mm_hr_employee_family.relation_nephew_niece')
        uncle_aunt.inverse_relation_id = nephew_niece.id
        nephew_niece.inverse_relation_id = uncle_aunt.id

        cousin = env.ref('mm_hr_employee_family.relation_cousin')
        cousin.inverse_relation_id = cousin.id

        cousin_2nd = env.ref('mm_hr_employee_family.relation_cousin_2nd')
        cousin_2nd.inverse_relation_id = cousin_2nd.id


