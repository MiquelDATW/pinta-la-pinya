# -*- coding: utf-8 -*-
# (c) 2020 Miquel March <m.marchpuig@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import string
import random
import logging
from datetime import datetime
from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def post_init_hook(cr, registry):

    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})

        skills = env['hr.skill'].search([])
        employee = env['hr.employee']
        emp_skill = env['hr.employee.skill']
        anthropometry = env['hr.employee.anthropometry']

        sequence = [i for i in range(len(skills))]

        for i in range(80):
            name = ''.join([random.choice(string.ascii_lowercase) for n in range(12)]).capitalize()
            als = random.randint(145, 201)
            pes = random.randint(45, 110)
            data = {
                'name': name + ' ' + str(i).zfill(3),
                'nom_croquis': name,
                'gender': 'other'
            }
            muixo = employee.create(data)
            data = {
                'data': datetime.today().date(),
                'employee_id': muixo.id,
                'height': als,
                'weight': pes,
                'alsada_muscle': als - random.randint(20, 30),
                'alsada_bras': als + random.randint(45, 55),
            }
            mesura = anthropometry.create(data)

            len_j = random.randint(0, 6) + 4
            len_s = random.sample(sequence, len_j+1)

            aux = env['hr.employee.skill']
            for j in range(len_j):
                level = str(random.randint(0, 3))
                data = {
                    'level': level,
                    'employee_id': muixo.id,
                    'skill_id': skills[len_s[j]].id,
                }
                aux += emp_skill.create(data)




