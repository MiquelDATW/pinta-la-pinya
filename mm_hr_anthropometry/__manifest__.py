# -*- coding: utf-8 -*-
# (c) 2020 Miquel March <m.marchpuig@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "HR Anthropometry",
    "summary": "Manage your employees' height and weight",
    "version": "11.0.1.0.1",
    "category": "Health",
    "website": "https://github.com/MiquelDATW/pinta-la-pinya",
    "author": "Miquel March",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "hr",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/anthropometry_view.xml",
        "views/hr_employee_view.xml",
    ],
}
