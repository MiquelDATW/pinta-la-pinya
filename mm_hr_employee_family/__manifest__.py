# -*- coding: utf-8 -*-
# Copyright (C) 2018 Brainbean Apps (https://brainbeanapps.com)
# (c) 2020 Miquel March <m.marchpuig@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "HR Employee Family",
    "summary": "Manage your employees' family information",
    "version": "11.0.1.0.1",
    "category": "Human Resources",
    "website": "http://www.enfaixat.cat/",
    "author": "Miquel March, Brainbean Apps",
    "license": "AGPL-3",
    "installable": True,
    'application': False,
    "depends": [
        "hr",
    ],
    'data': [
        "data/data_relation.xml",
        "views/employee_family_views.xml",
        "views/employee_relation_views.xml",
        "views/menu_views.xml",
        "security/ir.model.access.csv",
    ],
    "post_init_hook": "post_init_hook",
}
