# -*- coding: utf-8 -*-
# (c) 2020 Miquel March <m.marchpuig@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Pinta la Pinya",
    "summary": "Permet fer una gestió tècnica completa d'una colla muixeranguera",
    "version": "11.0.1.0.7",
    "category": "Custom",
    'website': 'http://www.pintalapinya.cat/',
    "author": "Miquel March",
    "license": "AGPL-3",
    "installable": True,
    'application': True,
    "depends": [
        "contacts",
        "event",
        "hr_skill",
        "hr_team",
        "pinya_complements",
    ],
    "data": [
        'security/ir.model.access.csv',
        'data/cron.xml',
        'data/event_templates.xml',
        'data/hr_skill_templates.xml',
        "views/event_view.xml",
        "views/hr_employee_view.xml",
        "views/hr_family_view.xml",
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
