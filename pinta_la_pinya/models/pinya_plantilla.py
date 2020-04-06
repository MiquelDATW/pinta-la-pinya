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

    neta = fields.Boolean(string="Sense pinya", default=False)

    plantilla_line_ids = fields.One2many('pinya.plantilla.line', 'plantilla_id', string="Plantilla")
    total_count = fields.Integer(compute='_compute_total_count', string='Total persones', store=True)
    pinya_count = fields.Integer(compute='_compute_total_count', string='Persones pinya', store=True)
    tronc_count = fields.Integer(compute='_compute_total_count', string='Persones tronc', store=True)

    image = fields.Binary("Image", attachment=True, help="Limitat a 1024x1024px.")

    @api.multi
    @api.depends('plantilla_line_ids', 'plantilla_line_ids.posicions_qty', 'plantilla_line_ids.rengles')
    def _compute_total_count(self):
        for plantilla in self:
            tronc = plantilla.plantilla_line_ids.filtered(lambda x: x.tipus == 'tronc')
            pinya = plantilla.plantilla_line_ids.filtered(lambda x: x.tipus == 'pinya')
            t = sum(t.posicions_qty for t in tronc)
            p = sum(p.posicions_qty * p.rengles for p in pinya)
            plantilla.tronc_count = t
            plantilla.pinya_count = p
            plantilla.total_count = t + p

    def crear_muixeranga(self, actuacio):
        def _get_last(ms):
            plantilla_name = ms.mapped('plantilla_id').name
            names = ms.filtered(lambda x: plantilla_name in x.name).mapped('name')
            names2 = [name.replace(plantilla_name + ' #', '') for name in names]
            names3 = [int(name) for name in names2]
            max_name = max(names3)
            return max_name

        obj_actua = self.env['pinya.actuacio']
        obj_muixe = self.env['pinya.muixeranga']
        obj_tronc = self.env['pinya.muixeranga.tronc']
        obj_pinya = self.env['pinya.muixeranga.pinya']

        ms = obj_muixe.search([('plantilla_id', '=', self.id)], order='create_date DESC')
        len_ms = len(ms)
        max_ms = _get_last(ms) if bool(ms) else 0
        max_len = max(len_ms, max_ms)
        name = self.name + ' #' + str(max_len+1).zfill(4)

        vals = {}
        vals['name'] = name
        vals['plantilla_id'] = self.id
        vals['actuacio_id'] = actuacio

        new_line = self.env['pinya.muixeranga.tronc']
        tronc = self.plantilla_line_ids.filtered(lambda x: x.tipus == 'tronc')

        line_vals = {}
        line_vals['actuacio_id'] = actuacio
        line_vals['data'] = obj_actua.browse(actuacio).data
        for aux in tronc:
            posicions = aux.posicio_ids
            line_vals['name'] = str(aux.name)
            for pos in posicions:
                qty = pos.quantity
                line_vals['tecnica'] = pos.tecnica
                line_vals['posicio_id'] = pos.posicio_id.id
                for q in range(qty):
                    new_line += obj_tronc.create(line_vals)

        vals['tronc_line_ids'] = [(6, 0, new_line.ids)]

        if self.neta:
            vals['pinya_line_ids'] = False
            res = obj_muixe.create(vals)
            return res

        new_line = self.env['pinya.muixeranga.pinya']
        pinya = self.plantilla_line_ids.filtered(lambda x: x.tipus == 'pinya')
        rengles = list(set(pinya.mapped('rengles')))
        if not bool(pinya) or not bool(rengles):
            error_msg = "A la figura '{}' li falta la pinya❗".format(self.name)
            raise ValidationError(error_msg)
        rengles = rengles[0]

        line_vals = {}
        line_vals['actuacio_id'] = actuacio
        line_vals['data'] = obj_actua.browse(actuacio).data
        for i in range(rengles):
            line_vals['rengle'] = str(i+1)
            for aux in pinya:
                posicions = aux.posicio_ids
                line_vals['name'] = str(aux.name)
                for pos in posicions:
                    qty = pos.quantity
                    line_vals['tecnica'] = pos.tecnica
                    line_vals['posicio_id'] = pos.posicio_id.id
                    for q in range(qty):
                        new_line += obj_pinya.create(line_vals)

        vals['pinya_line_ids'] = [(6, 0, new_line.ids)]
        res = obj_muixe.create(vals)
        return res


class PinyaPlantillaLine(models.Model):
    _name = "pinya.plantilla.line"
    _description = "Línea de plantilla"
    _order = "tipus desc, name, rengles asc"

    name = fields.Selection([
        ('-1', '-1'), ('0', '0'),
        ('1', '1'), ('2', '2'), ('3', '3'),
        ('4', '4'),  ('5', '5'),  ('6', '6'),
    ], string="Pis/Cordó")
    rengles = fields.Integer(string="Rengles de pinya")

    posicio_ids = fields.Many2many("pinya.plantilla.skill", string="Posicions")
    posicions_qty = fields.Integer(string="Total pis/rengle", compute="_compute_posicions_qty", store=True)
    plantilla_id = fields.Many2one(string="Plantilla", comodel_name="pinya.plantilla")

    tipus = fields.Selection([
        ('pinya', 'Pinya'),
        ('tronc', 'Tronc')
    ], string='Tipus', required=True)

    @api.multi
    @api.depends('posicio_ids', 'posicio_ids.quantity')
    def _compute_posicions_qty(self):
        for line in self:
            posicions = line.posicio_ids
            line.posicions_qty = sum(posicions.mapped('quantity'))


class PinyaPlantillaSkill(models.Model):
    _name = "pinya.plantilla.skill"
    _description = "Posicions de línea de plantilla"
    _order = "tipus desc, posicio_id asc, quantity asc"

    name = fields.Char(string="Nom", related="posicio_id.name", index=True)
    posicio_id = fields.Many2one(string="Posicions", comodel_name="hr.skill", required=True)
    quantity = fields.Integer(string="Quantitat", default=1)

    tipus = fields.Selection([
        ('pinya', 'Pinya'),
        ('tronc', 'Tronc')
    ], string='Tipus', required=True)

    tecnica = fields.Selection([
        ('0', 'Inicial'),
        ('1', 'Mitjana'),
        ('2', 'Avançada'),
        ('3', 'Experta'),
    ], string='Tècnica', default="1", required=True)
