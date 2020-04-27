# -*- coding: utf-8 -*-
# (c) 2020 Miquel March <m.marchpuig@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, exceptions, _
from odoo.exceptions import ValidationError


def _get_action(view_tree_id, view_form_id, name, model, domain):
    action = {
        'type': 'ir.actions.act_window',
        'views': [(view_tree_id, 'tree'), (view_form_id, 'form')],
        'view_mode': 'form',
        'name': name,
        'target': 'current',
        'res_model': model,
        'context': {},
        'domain': domain,
    }
    return action


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
    total_muix2 = fields.Integer(compute='_compute_muixeranga_count', string='Muixerangues', store=True)
    esborrany_muix = fields.Integer(compute='_compute_muixeranga_count', string='Muix. esborrany', store=True)
    descarrega_muix = fields.Integer(compute='_compute_muixeranga_count', string='Muix. descarregades', store=True)
    intent_muix = fields.Integer(compute='_compute_muixeranga_count', string='Muix. intents', store=True)
    caigut_muix = fields.Integer(compute='_compute_muixeranga_count', string='Muix. caigudes', store=True)

    image = fields.Binary("Image", attachment=True, help="Limitat a 1024x1024px.")

    @api.multi
    @api.depends('plantilla_line_ids', 'plantilla_line_ids.rengles')
    def _compute_total_count(self):
        for plantilla in self:
            tronc = plantilla.plantilla_line_ids.filtered(lambda x: x.tipus == 'tronc')
            pinya = plantilla.plantilla_line_ids.filtered(lambda x: x.tipus == 'pinya')
            t = sum(t.rengles for t in tronc)
            p = sum(p.rengles for p in pinya)
            plantilla.tronc_count = t
            plantilla.pinya_count = p
            plantilla.total_count = t + p

    @api.multi
    @api.depends('muixeranga_ids', 'muixeranga_ids.state')
    def _compute_muixeranga_count(self):
        for plantilla in self:
            draft = plantilla.muixeranga_ids.filtered(lambda x: x.state == 'draft')
            desca = plantilla.muixeranga_ids.filtered(lambda x: x.state == 'descarregat')
            intent = plantilla.muixeranga_ids.filtered(lambda x: x.state == 'intent')
            fail = plantilla.muixeranga_ids.filtered(lambda x: x.state == 'caigut')
            plantilla.total_muix = len(plantilla.muixeranga_ids)
            plantilla.total_muix2 = len(plantilla.muixeranga_ids)
            plantilla.esborrany_muix = len(draft)
            plantilla.descarrega_muix = len(desca)
            plantilla.intent_muix = len(intent)
            plantilla.caigut_muix = len(fail)

    @api.multi
    def unlink(self):
        for plantilla in self:
            lines = plantilla.plantilla_line_ids
            for line in lines:
                line.posicio_ids.unlink()
            lines.unlink()
            lines = plantilla.muixeranga_ids
            lines.unlink()
        res = super(PinyaPlantilla, self).unlink()
        return res

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
        troncs = self.plantilla_line_ids.filtered(lambda x: x.tipus == 'tronc')

        line_vals = {}
        line_vals['actuacio_id'] = actuacio
        for tronc in troncs:
            posicions = tronc.posicio_ids
            pis = str(tronc.name)
            line_vals['pis'] = pis
            for pos in posicions:
                qty = len(posicions.filtered(lambda x: x.posicio_id.id == pos.posicio_id.id).ids)
                line_vals['name'] = pos.posicio_id.name + ' / ' + pis
                line_vals['rengle'] = pos.rengle
                line_vals['tecnica'] = pos.tecnica
                line_vals['posicio_id'] = pos.posicio_id.id
                jo = str(self.id).zfill(2) + '_' + str(pos.posicio_id.id).zfill(2)
                jo += '_P' + pis + '_T' + pos.tecnica + '__' + str(pos.rengle) + '.de.' + str(qty)
                line_vals['quisocjo'] = jo
                new_line += obj_tronc.create(line_vals)

        vals['tronc_line_ids'] = [(6, 0, new_line.ids)]

        if self.neta:
            vals['pinya_line_ids'] = False
            res = obj_muixe.create(vals)
            self.muixeranga_count += 1
            return res

        new_line = self.env['pinya.muixeranga.pinya']
        pinyes = self.plantilla_line_ids.filtered(lambda x: x.tipus == 'pinya')
        rengles = max(pinyes.mapped('rengles') or [0])
        if not bool(pinyes) or not bool(rengles):
            error_msg = "A la figura '{}' li falta la pinya❗".format(self.name)
            raise ValidationError(error_msg)

        line_vals = {}
        line_vals['actuacio_id'] = actuacio
        for pinya in pinyes:
            posicions = pinya.posicio_ids
            cordo = str(pinya.name)
            line_vals['cordo'] = cordo
            for pos in posicions:
                qty = len(posicions.filtered(lambda x: x.posicio_id.id == pos.posicio_id.id).ids)
                line_vals['name'] = pos.posicio_id.name + ' / ' + cordo
                line_vals['rengle'] = pos.rengle
                #line_vals['rengle'] = str(pos.rengle).zfill(2)
                #line_vals['rengle'] = str(round(((pos.rengle - 1) / rengles) * 60)).zfill(2) + "'"
                #line_vals['rengle'] = str(round(((pos.rengle - 1) / rengles) * 360)).zfill(3) + "º"
                line_vals['tecnica'] = pos.tecnica
                line_vals['posicio_id'] = pos.posicio_id.id
                jo = str(self.id).zfill(2) + '_' + str(pos.posicio_id.id).zfill(2)
                jo += '_C' + cordo + '_T' + pos.tecnica + '__' + str(pos.rengle) + '.de.' + str(qty)
                line_vals['quisocjo'] = jo
                new_line += obj_pinya.create(line_vals)

        vals['pinya_line_ids'] = [(6, 0, new_line.ids)]
        mestra = obj_actua.browse(actuacio).mestra_id.employee_id.id
        if mestra:
            vals['mestra_id'] = mestra
        res = obj_muixe.create(vals)
        self.muixeranga_count += 1
        return res

    def mostrar_muixerangues(self):
        view_tree_id = self.env.ref('pinya_tecnica.view_muixeranga_tree_selected').id
        view_form_id = self.env.ref('pinya_tecnica.view_muixeranga_form').id
        name = "Muixerangues"
        model = "pinya.muixeranga"
        domain = [('id', 'in', self.muixeranga_ids.ids)]
        action = _get_action(view_tree_id, view_form_id, name, model, domain)
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

    posicio_ids = fields.One2many("pinya.plantilla.skill", "line_id", string="Posicions")
    rengles = fields.Integer(string="Rengles", compute="_compute_rengles", store=True)
    plantilla_id = fields.Many2one(string="Plantilla", comodel_name="pinya.plantilla")

    tipus = fields.Selection([
        ('pinya', 'Pinya'),
        ('tronc', 'Tronc')
    ], string='Tipus', required=True)

    @api.multi
    @api.depends('posicio_ids')
    def _compute_rengles(self):
        for line in self:
            posicions = line.posicio_ids
            line.rengles = len(list(set(posicions.mapped('rengle'))))


class PinyaPlantillaSkill(models.Model):
    _name = "pinya.plantilla.skill"
    _description = "Posicions de línea de plantilla"
    _order = "tipus desc, rengle asc, posicio_id asc"

    name = fields.Char(string="Nom", related="posicio_id.name", index=True)
    line_id = fields.Many2one(string="Línea de plantilla", comodel_name="pinya.plantilla.line", required=True)
    posicio_id = fields.Many2one(string="Posicions", comodel_name="hr.skill", required=True)
    rengle = fields.Integer(string="Rengle")

    tipus = fields.Selection([
        ('pinya', 'Pinya'),
        ('tronc', 'Tronc')
    ], string='Tipus', required=True)

    tecnica = fields.Selection([
        ('0', 'Inicial'),
        ('1', 'Intermedia'),
        ('2', 'Avançada'),
        ('3', 'Experta'),
    ], string='Tècnica', default="1", required=True)
