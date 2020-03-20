# -*- coding: utf-8 -*-
# (c) 2020 Miquel March <m.marchpuig@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, exceptions, _
from odoo.exceptions import ValidationError


class PinyaMuixeranga(models.Model):
    _name = "pinya.muixeranga"
    _description = "Muixeranga"
    _order = "name asc"
    _inherit = ['mail.thread']

    name = fields.Char(string="Nom", index=True, required=True, translate=True)
    active = fields.Boolean(string="Actiu", default=True)
    plantilla = fields.Boolean(string="Plantilla", default=False)
    plantilla_id = fields.Many2one("pinya.plantilla", string="Plantilla")
    notes = fields.Text(string="Altra informació")

    tipus = fields.Selection(related="plantilla_id.tipus", string='Tipus', required=True)
    pisos = fields.Selection(related="plantilla_id.pisos", string='Pisos', required=True)

    tronc_ids = fields.One2many('pinya.tronc', 'muixeranga_id', string="Tronc", copy=True)
    pinya_ids = fields.One2many('pinya.pinya', 'muixeranga_id', string="Pinya", copy=True)

    tronc_line_ids = fields.One2many('pinya.muixeranga.line', 'muixeranga_tronc_id', string="Tronc", copy=True)
    pinya_line_ids = fields.One2many('pinya.muixeranga.line', 'muixeranga_pinya_id', string="Pinya", copy=True)

    mestra_id = fields.Many2one('hr.employee', string="Mestra")
    passadora_id = fields.Many2one('hr.employee', string="Passadora")
    estiradora_id = fields.Many2one('hr.employee', string="Estiradora")
    resp_xicalla_ids = fields.Many2many('hr.employee', string="Responsable de xicalla")
    membres_count = fields.Integer(compute='_compute_membres_count', string='Total persones', store=True)
    pinya_count = fields.Integer(compute='_compute_membres_count', string='Persones pinya', store=True)
    tronc_count = fields.Integer(compute='_compute_membres_count', string='Persones tronc', store=True)

    actuacio_id = fields.Many2one(string="Actuació", comodel_name="pinya.actuacio")
    membre_ids = fields.Many2many('hr.employee', string="Membres", related="actuacio_id.membre_ids")

    estat = fields.Selection([
        ('draft', 'Esborrany'),
        ('desca', 'Descarregat'),
        ('intent', 'Intent'),
        ('fail', 'Caigut')
    ], string='Estat', required=True, default='draft')

    image = fields.Binary("Image", attachment=True, help="Limitat a 1024x1024px.")

    @api.multi
    @api.depends('tronc_ids', 'tronc_ids.persones', 'pinya_ids', 'pinya_ids.persones', 'pinya_ids.rengles')
    def _compute_membres_count(self):
        for muix in self:
            tronc = muix.tronc_ids
            pinya = muix.pinya_ids
            t = sum(t.persones for t in tronc)
            p = sum(p.persones * p.rengles for p in pinya)
            muix.tronc_count = t
            muix.pinya_count = p
            muix.membres_count = t + p

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


class PinyaMuixerangaLine(models.Model):
    _name = "pinya.muixeranga.line"
    _description = "Línea de muixeranga"
    _order = "name asc, rengle asc"

    name = fields.Char(string="Pis/Cordó", index=True, required=True, translate=True)
    pis = fields.Integer(string="Pis")
    cordo = fields.Integer(string="Cordó")
    rengle = fields.Integer(string="Rengle")
    active = fields.Boolean(string="Actiu", default=True)

    posicio_id = fields.Many2one(string="Posició", comodel_name="pinya.posicio")
    membre_id = fields.Many2one(string="Membre", comodel_name="hr.employee")
    muixeranga_tronc_id = fields.Many2one(string="Figura", comodel_name="pinya.muixeranga")
    muixeranga_pinya_id = fields.Many2one(string="Figura", comodel_name="pinya.muixeranga")

    tipus = fields.Selection([
        ('pinya', 'Pinya'),
        ('tronc', 'Tronc')
    ], string='Tipus', required=True)



