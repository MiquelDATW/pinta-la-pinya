# -*- coding: utf-8 -*-
# (c) 2020 Miquel March <m.marchpuig@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "HR Employee Family",
    "summary": "Manage your employees' family information",
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
        "views/hr_family_views.xml",
        "security/ir.model.access.csv",
    ],
}
