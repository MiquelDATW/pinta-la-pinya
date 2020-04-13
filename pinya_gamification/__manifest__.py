# -*- coding: utf-8 -*-
# (c) 2020 Miquel March <m.marchpuig@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Pinya Gamification",
    "summary": "Permet incloure opcions de gamificació a 'Pinta la Pinya'",
    "version": "11.0.1.0.1",
    "category": "Custom",
    'website': 'http://www.pintalapinya.cat/',
    "author": "Miquel March",
    "license": "AGPL-3",
    "installable": True,
    'application': False,
    "depends": [
        "hr_gamification",
        "pinta_la_pinya",
    ],
    "data": [
        "views/hr_employee_view.xml",
    ],
}
