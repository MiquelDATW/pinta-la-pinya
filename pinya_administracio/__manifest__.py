# -*- coding: utf-8 -*-
# (c) 2020 Miquel March <m.marchpuig@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Pinya Administrativa",
    "summary": "Permet fer una gestió administrativa completa d'una colla muixeranguera",
    "version": "11.0.1.0.2",
    "category": "Custom",
    "website": "https://github.com/MiquelDATW/pinta-la-pinya",
    "author": "Miquel March",
    "license": "AGPL-3",
    "installable": True,
    'application': True,
    "depends": [
        "l10n_es",
        "association",
        "crm",
        "stock",
        "sale_management",
        "purchase",
        "membership_extension",
        "membership_withdrawal",
        "pinya_tecnica",
    ],
    "data": [
        "views/crm_views.xml",
        "views/event_views.xml",
        "views/hr_employee_views.xml",
        "views/membership_views.xml",
        "views/pinya_actuacio_views.xml",
        "data/membership_data.xml",
        "data/products_data.xml",
    ],
    "post_init_hook": "post_init_hook",
}
