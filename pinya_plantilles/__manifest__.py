# -*- coding: utf-8 -*-
# (c) 2020 Miquel March <m.marchpuig@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Pinya Plantilles",
    "summary": "Plantilles de Muixerangues",
    "version": "11.0.1.0.1",
    "category": "Custom",
    'website': 'http://www.pintalapinya.cat/',
    "author": "Miquel March",
    "license": "AGPL-3",
    "installable": True,
    'application': False,
    "depends": [
        "pinta_la_pinya",
    ],
    "data": [
        'data/plantilla_skill_templates.xml',
        'data/plantilla_torreta_templates.xml',
        "report/pinya_reports.xml",
        "report/pinya_muixeranga_templates.xml",
        "report/torreta_templates.xml",
    ],
}