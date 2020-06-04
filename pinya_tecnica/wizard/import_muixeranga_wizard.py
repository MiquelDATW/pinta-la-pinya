# -*- coding: utf-8 -*-
# (c) 2020 Miquel March <m.marchpuig@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo import api, models, fields


class PinyaMuixerangaWizard(models.TransientModel):
    """
    Assistent per importar i crear les muixerangues
    """
    _name = "pinya.muixeranga.wizard"

    lines = fields.One2many(comodel_name='pinya.muixeranga.line.wizard', inverse_name='wizard_id', string='Líneas')

    @api.model
    def default_get(self, fields_list):
        res = super(PinyaMuixerangaWizard, self).default_get(fields_list)
        return res

    def afegir_figures_btn(self):
        actuacio = self.env.context.get('actuacio_id', False)
        if not bool(actuacio):
            error_msg = "No hi ha cap assaig o actuació guardada❗"
            raise ValidationError(error_msg)
        lines = self.lines.filtered(lambda x: x.plantilla_id.id)
        if not bool(lines):
            return False
        for line in lines:
            for i in range(line.numero):
                line.plantilla_id.crear_muixeranga(actuacio)
        return True


class PinyaMuixerangaLineWizard(models.TransientModel):
    _name = 'pinya.muixeranga.line.wizard'

    wizard_id = fields.Many2one('pinya.muixeranga.wizard', string='Wizard')
    plantilla_id = fields.Many2one('pinya.plantilla', string='Plantilla')
    numero = fields.Integer(string='Número', default=1)
