# -*- coding: utf-8 -*-
# (c) 2020 Miquel March <m.marchpuig@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "HR Teams",
    "summary": "Manage your employee teams",
    "version": "11.0.1.0.1",
    "category": "Human Resources",
    "website": "http://www.enfaixat.cat/",
    "author": "Miquel March",
    "license": "AGPL-3",
    "installable": True,
    'application': False,
    "depends": ["hr"],
    'data': [
        "views/menus_views.xml",
        "views/hr_employee_views.xml",
        "views/hr_team_views.xml",
        "security/ir.model.access.csv",
    ],
}
