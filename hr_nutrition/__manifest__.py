# -*- coding: utf-8 -*-
# Copyright 2016 Ursa Information Systems <http://ursainfosystems.com>
# (c) 2020 Miquel March <m.marchpuig@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "HR Nutrition",
    "summary": "Manage your employees' nutrition",
    "version": "11.0.1.0.2",
    "category": "Health",
    'website': 'http://www.pintalapinya.cat/',
    "author": "Ursa Information Systems, Miquel March",
    "license": "AGPL-3",
    "application": True,
    "installable": True,
    "depends": [
        "hr"
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/nutrition_diet.xml",
        "data/nutrition_food.xml",
        "views/hr_employee_view.xml",
        "views/nutrition_view.xml",
    ],
}
