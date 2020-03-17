# -*- coding: utf-8 -*-
# (c) 2020 Miquel March <m.marchpuig@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Pinta la Pinya",
    "summary": "Permet fer una gestió tècnica completa d'una colla muixeranguera",
    "version": "11.0.1.0.1",
    "category": "Custom",
    'website': 'http://www.pintalapinya.cat/',
    "author": "Miquel March",
    "license": "AGPL-3",
    "installable": True,
    'application': True,
    "depends": [
        "hr",
        "base_location",
    ],
    "data": [
        # 'security/ir.model.access.csv',
        "views/pinya_actuacio_view.xml",
        "views/pinya_membre_view.xml",
        "views/pinya_muixeranga_view.xml",
        "views/pinya_pinya_view.xml",
        "views/pinya_posicio_view.xml",
        "views/pinya_tronc_view.xml",
        "wizard/pinya_import_wizard_view.xml",
        "wizard/pinya_muixeranga_wizard_view.xml",
        "views/menus_views.xml",
    ],
}
