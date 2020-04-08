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
    muixeranga_count = fields.Integer(string='Muixerangues creades', readonly=True)

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

    muixeranga_ids = fields.One2many('pinya.muixeranga', 'plantilla_id', string="Muixerangues")
    total_muix = fields.Integer(compute='_compute_muixeranga_count', string='Total muix.', store=True)
    esborrany_muix = fields.Integer(compute='_compute_muixeranga_count', string='Muix. esborrany', store=True)
    descarrega_muix = fields.Integer(compute='_compute_muixeranga_count', string='Muix. descarregades', store=True)
    intent_muix = fields.Integer(compute='_compute_muixeranga_count', string='Muix. intents', store=True)
    caigut_muix = fields.Integer(compute='_compute_muixeranga_count', string='Muix. caigudes', store=True)

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

    @api.multi
    @api.depends('muixeranga_ids', 'muixeranga_ids.estat')
    def _compute_muixeranga_count(self):
        for plantilla in self:
            draft = plantilla.muixeranga_ids.filtered(lambda x: x.estat == 'draft')
            desca = plantilla.muixeranga_ids.filtered(lambda x: x.estat == 'desca')
            intent = plantilla.muixeranga_ids.filtered(lambda x: x.estat == 'intent')
            fail = plantilla.muixeranga_ids.filtered(lambda x: x.estat == 'fail')
            plantilla.total_muix = len(plantilla.muixeranga_ids)
            plantilla.esborrany_muix = len(draft)
            plantilla.descarrega_muix = len(desca)
            plantilla.intent_muix = len(intent)
            plantilla.caigut_muix = len(fail)

    def crear_muixeranga(self, actuacio):
        obj_actua = self.env['pinya.actuacio']
        obj_muixe = self.env['pinya.muixeranga']
        obj_tronc = self.env['pinya.muixeranga.tronc']
        obj_pinya = self.env['pinya.muixeranga.pinya']

        count = self.muixeranga_count
        name = self.name + ' #' + str(count+1).zfill(4)

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
            self.muixeranga_count += 1
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
        self.muixeranga_count += 1
        return res

    def mostrar_muixerangues(self):
        view_tree_id = self.env.ref('pinta_la_pinya.view_muixeranga_tree').id
        view_form_id = self.env.ref('pinta_la_pinya.view_muixeranga_form').id
        domain = [('id', 'in', self.muixeranga_ids.ids)]
        action = {
            'type': 'ir.actions.act_window',
            'views': [(view_tree_id, 'tree'), (view_form_id, 'form')],
            'view_mode': 'form',
            'name': "Muixerangues",
            'target': 'current',
            'res_model': 'pinya.muixeranga',
            'context': {},
            'domain': domain,
        }
        return action


class PinyaPlantillaLine(models.Model):
    _name = "pinya.plantilla.line"
    _description = "Línea de plantilla"
    _order = "tipus desc, name, rengles asc"

    name = fields.Selection([
        ('0', '0'),
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
