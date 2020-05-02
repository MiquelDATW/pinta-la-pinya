# -*- coding: utf-8 -*-
# (c) 2020 Miquel March <m.marchpuig@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Pinya Telegram",
    "summary": "Permet la comunicació amb el servei de missatgeria Telegram",
    "version": "11.0.1.0.1",
    "category": "Custom",
    "website": "http://www.enfaixat.cat/",
    "author": "Miquel March",
    "license": "AGPL-3",
    "installable": True,
    'application': True,
    "depends": [
        "contacts",
        "pinya_tecnica",
    ],
    "external_dependencies": {"python": [
        'telegram',
    ], "bin": []},
    "data": [
        "views/pinya_actuacio_view.xml",
        "views/res_telegram_view.xml",
        "wizard/telegram_wizard_view.xml",
        "security/ir.model.access.csv",
    ],
}
