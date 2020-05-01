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
        "pinya_tecnica",
    ],
    "external_dependencies": {"python": [
        'telebot',
        'emoji',
    ], "bin": []},
    "data": [
        "views/res_partner_view.xml",
    ],
}
