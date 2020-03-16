# -*- coding: utf-8 -*-
# (c) 2020 Miquel March <m.marchpuig@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, exceptions, _
from odoo.exceptions import ValidationError


class PinyaMembre(models.Model):
    _name = "pinya.membre"
    _description = "Membre d'una muixeranga"
    _order = "id desc"
    _inherit = ['mail.thread']

    name = fields.Char(string="Nom", index=True, required=True, translate=True)
    date = fields.Date(string="Data")
    notes = fields.Text(string="Altra informació")
    active = fields.Boolean(string="Actiu", default=True)
    employee_id = fields.Many2one(string="Persona", comodel_name="hr.employee")

    posicio_ids = fields.Many2many('pinya.posicio', string="Posició")
    pinya_ids = fields.Many2many("pinya.pinya.line", string="Pinya")
    tronc_ids = fields.Many2many("pinya.tronc.line", string="Tronc")

    image = fields.Binary("Image", attachment=True, related="employee_id.image",
                          help="Limitat a 1024x1024px.")
