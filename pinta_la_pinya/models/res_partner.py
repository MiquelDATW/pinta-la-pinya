# -*- coding: utf-8 -*-
# (c) 2020 Miquel March <m.marchpuig@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, exceptions, _
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta


class ResPartner(models.Model):
    _inherit = 'res.partner'

    muixeranguera = fields.Boolean(string="Muixeranguera")
    colla = fields.Boolean(string="Colla muixeranguera")

    assaig_dia = fields.Selection([
        ('0', 'Dilluns'),
        ('1', 'Dimarts'),
        ('2', 'Dimecres'),
        ('3', 'Dijous'),
        ('4', 'Divendres'),
        ('5', 'Dissabte'),
        ('6', 'Diumenge')
    ], string="Dia d'assaig")

    assaig_hora_inici = fields.Float(string="Hora d'inici d'assaig")
    assaig_hora_final = fields.Float(string="Hora de final d'assaig")

    fundacio_data = fields.Date(string="Data de fundació")
    fundacio_anys = fields.Integer(string='Anys', readonly=True)

    federacio = fields.Boolean(string="Membre de la FCM")
    federacio_data = fields.Date(string="Data de federació")
    federacio_anys = fields.Integer(string='Anys de federació', readonly=True)

    federacio_tipus_colla = fields.Selection([
        ('0', 'Colla tradicional'),
        ('3', 'Colla de 3'),
        ('4', 'Colla de 4'),
        ('5', 'Colla de 5'),
        ('6', 'Colla de 6'),
    ], string="Tipus de colla")

    jd_presidencia = fields.Char(string="Presidència")
    jd_secretaria = fields.Char(string="Secretaria")
    jd_tresoreria = fields.Char(string="Tresoreria")

    at_mestra = fields.Char(string="Mestra")
    at_cap_de_pinya = fields.Char(string="Cap de pinya")
    at_cap_de_tronc = fields.Char(string="Cap de tronc")
    at_cap_de_xicalla = fields.Char(string="Cap de xicalla")

    @api.multi
    def _compute_anys_colla(self):
        date_now = fields.Date.from_string(fields.Date.today())
        colles = self.search([('colla', '=', True)])

        colles1 = colles.filtered(lambda x: bool(x.fundacio_data))
        for colla in colles1:
            age = relativedelta(date_now, fields.Date.from_string(colla.fundacio_data)).years
            colla.fundacio_anys = age

        colles2 = colles.filtered(lambda x: bool(x.federacio_data))
        for colla in colles2:
            age = relativedelta(date_now, fields.Date.from_string(colla.federacio_data)).years
            colla.federacio_anys = age

