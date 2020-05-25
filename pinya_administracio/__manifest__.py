# -*- coding: utf-8 -*-
# (c) 2020 Miquel March <m.marchpuig@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Pinya Administrativa",
    "summary": "Permet fer una gestió administrativa completa d'una colla muixeranguera",
    "version": "11.0.1.0.1",
    "category": "Custom",
    "website": "http://www.enfaixat.cat/",
    "author": "Miquel March",
    "license": "AGPL-3",
    "installable": True,
    'application': True,
    "depends": [
        "l10n_es",
        "association",
        "membership_extension",
        "membership_withdrawal",
        "mm_hr_employee_family",
        "pinya_tecnica",
    ],
    "data": [
        "views/hr_employee_view.xml",
        "views/membership_views.xml",
        "data/membership_category_data.xml",
        "data/product_template_data.xml",
    ],
    "post_init_hook": "post_init_hook",
}
