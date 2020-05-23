# -*- coding: utf-8 -*-
# (c) 2020 Miquel March <m.marchpuig@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "HR Employee Age",
    "summary": "Adds and computes age field on employee",
    "version": "11.0.1.0.1",
    "category": "Human Resources",
    "website": "http://www.enfaixat.cat/",
    "author": "Miquel March",
    "license": "AGPL-3",
    "installable": True,
    'application': False,
    "depends": [
        "hr",
    ],
    'data': [
        'data/cron.xml',
        "views/hr_employee_views.xml",
    ],
}
