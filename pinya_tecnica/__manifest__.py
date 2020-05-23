# -*- coding: utf-8 -*-
# (c) 2020 Miquel March <m.marchpuig@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Pinya Tècnica",
    "summary": "Permet fer una gestió tècnica completa d'una colla muixeranguera",
    "version": "11.0.1.0.9",
    "category": "Custom",
    "website": "http://www.enfaixat.cat/",
    "author": "Miquel March",
    "license": "AGPL-3",
    "installable": True,
    'application': True,
    "depends": [
        "contacts",
        "event",
        "hr_skill",
        "hr_team",
        "hr_nutrition",
        "pinya_complements",
    ],
    "data": [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/cron.xml',
        'data/event_templates.xml',
        'data/hr_skill_templates.xml',
        "views/anthropometry_view.xml",
        "views/event_view.xml",
        "views/hr_employee_view.xml",
        "views/hr_skill_view.xml",
        "views/hr_team_view.xml",
        "views/pinya_actuacio_view.xml",
        "views/pinya_muixeranga_view.xml",
        "views/pinya_plantilla_view.xml",
        "views/pinya_temporada_view.xml",
        "views/res_partner_view.xml",
        "wizard/import_pinya_wizard_view.xml",
        "wizard/import_muixeranga_wizard_view.xml",
        "views/menus_views.xml",
    ],
    "post_init_hook": "post_init_hook",
}
