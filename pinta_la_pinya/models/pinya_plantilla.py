# -*- coding: utf-8 -*-
# (c) 2020 Miquel March <m.marchpuig@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, exceptions, _
from odoo.exceptions import ValidationError


class PinyaPlantilla(models.Model):
    _name = "pinya.plantilla"
    _description = "Plantilla"
    _order = "name asc"
    _inherit = ['mail.thread']

    name = fields.Char(string="Nom", index=True, required=True, translate=True)
    active = fields.Boolean(string="Actiu", default=True)

    notes = fields.Text(string="Altra informació")

    tipus = fields.Selection([
        ('normal', 'Normal'),
        ('desplega', 'Desplegada'),
        ('aixecat', 'Aixecat')
    ], string='Tipus', required=True, default='normal')

    pisos = fields.Selection([
        ('2', '2'), ('3', '3'),
        ('4', '4'),  ('5', '5'),  ('6', '6'),
    ], string='Pisos', required=True)

    plantilla_line_ids = fields.One2many('pinya.plantilla.line', 'plantilla_id', string="Plantilla")

    image = fields.Binary("Image", attachment=True, help="Limitat a 1024x1024px.")

    def crear_muixeranga(self, actuacio):
        obj = self.env['pinya.muixeranga.line']
        vals = {}
        vals['actuacio_id'] = actuacio
        vals['tronc_ids'] = [(6, 0, False)]
        vals['pinya_ids'] = [(6, 0, False)]
        tronc = self.tronc_ids
        for aux in tronc.mapped('posicio_ids'):
            line_vals = {}
            line_vals['name'] = str(aux.pis)
            line_vals['pis'] = aux.pis
            line_vals['tipus'] = 'tronc'
            line_vals['muixeranga_tronc_id'] = aux.muixeranga_id.id
            line_vals['posicio_id'] = aux.posicio_id.id
            obj.create(line_vals)

        pinya = self.pinya_ids
        rengles = list(set(pinya.mapped('rengles')))
        if not bool(rengles) or len(rengles) != 1:
            error_msg = "Error❗"
            raise ValidationError(error_msg)
        rengles = rengles[0]
        for i in range(rengles):
            for aux in pinya.mapped('posicio_ids'):
                line_vals = {}
                line_vals['name'] = str(aux.cordo)
                line_vals['cordo'] = aux.cordo
                line_vals['rengle'] = i+1
                line_vals['tipus'] = 'pinya'
                line_vals['muixeranga_pinya_id'] = aux.muixeranga_id.id
                line_vals['posicio_id'] = aux.posicio_id.id
                obj.create(line_vals)

        res = self.write(vals)
        return res


class PinyaPlantillaLine(models.Model):
    _name = "pinya.plantilla.line"
    _description = "Línea de plantilla"
    _order = "tipus desc, name, rengles asc"

    name = fields.Selection([
        ('1', '1'), ('2', '2'), ('3', '3'),
        ('4', '4'),  ('5', '5'),  ('6', '6'),
    ], string="Pis/Cordó")
    rengles = fields.Integer(string="Rengles de pinya")

    # posicio_ids = fields.One2many("pinya.plantilla.skill", "line_id", string="Posicions")
    posicio_ids = fields.Char(string="Posicions")
    plantilla_id = fields.Many2one(string="Plantilla", comodel_name="pinya.plantilla")

    tipus = fields.Selection([
        ('pinya', 'Pinya'),
        ('tronc', 'Tronc')
    ], string='Tipus', required=True)


# class PinyaPlantillaSkill(models.Model):
#     _name = "pinya.plantilla.skill"
#     _description = "Posicions de línea de plantilla"
#     _order = "name asc"
#
#     name = fields.Char(string="Nom", index=True, translate=True)
#
#     line_id = fields.Many2one(string="Línea", comodel_name="pinya.plantilla.line")
#     posicio_id = fields.Many2one(string="Posicions", comodel_name="hr.skill")
#     tipus = fields.Selection(related="line_id.tipus", string='Tipus', required=True)
#
#     @api.onchange('posicio_id')
#     def _onchange_posicio_id(self):
#         if self.posicio_id:
#             self.name = self.posicio_id.name
#         else:
#             self.name = "Pinya"
#         return True
