# -*- coding: utf-8 -*-
# (c) 2020 Miquel March <m.marchpuig@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, exceptions, _
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime
import pytz


def _get_action(view_tree_id, view_form_id, view_search_id, name, model, domain, ctx):
    action = {
        'type': 'ir.actions.act_window',
        'views': [(view_tree_id, 'tree'), (view_form_id, 'form')],
        'search_view_id': view_search_id,
        'view_mode': 'form',
        'name': name,
        'target': 'current',
        'res_model': model,
        'context': ctx,
        'domain': domain,
    }
    return action


def _get_wizard(view_form_id, name, model):
    action = {
        'type': 'ir.actions.act_window',
        'views': [(view_form_id, 'form')],
        'view_mode': 'form',
        'name': name,
        'target': 'new',
        'res_model': model,
        'context': {}
    }
    return action


class PinyaActuacio(models.Model):
    """
    Cree esta classe com a base de les actuacions o assajos.
    """
    _name = "pinya.actuacio"
    _description = "Actuació o Assaig muixeranguer"
    _order = "id desc"
    _inherit = ['mail.thread']

    name = fields.Char(string="Nom", index=True, required=True, translate=True)
    active = fields.Boolean(string="Actiu", default=True)
    data_inici = fields.Datetime(string="Data inicial")
    data_final = fields.Datetime(string="Data final")
    data_xicalla = fields.Datetime(string="Assaig xicalla")
    data_general = fields.Datetime(string="Assaig general")
    notes = fields.Html(string="Altra informació")
    organizer_id = fields.Many2one(string="Organitzador", comodel_name="res.partner",
                                      related="event_id.organizer_id", store=True)
    event_id = fields.Many2one(string="Esdeveniment", comodel_name="event.event")
    temporada_id = fields.Many2one(string="Temporada", comodel_name="pinya.temporada", required=True)
    actual = fields.Boolean(string="Actual", related="temporada_id.actual", store=True)
    zip_id = fields.Many2one(string="Lloc", comodel_name="res.better.zip")
    tipus = fields.Selection([
            ('actuacio', 'Actuació'),
            ('assaig', 'Assaig')
    ], string='Tipus', required=True)

    state = fields.Selection([
        ('cancel', 'Cancel·lat'),
        ('draft', 'Esborrany'),
        ('ready', 'Preparat'),
        ('done', 'Fet')
    ], string='Estat', required=True, default='draft')
    obert = fields.Boolean(string="Encara obert", readonly=True)

    mestra_id = fields.Many2one('hr.employee.actuacio', string="Mestra")
    membre_actuacio_ids = fields.One2many('hr.employee.actuacio', 'actuacio_id', string="Membres")
    muixeranga_ids = fields.One2many('pinya.muixeranga', 'actuacio_id', string="Muixerangues")
    membres_count_calc = fields.Integer(compute='_compute_assistencia', string='Total persones')
    membres_count = fields.Integer(string='Total persones', readonly=True)
    actives_count = fields.Integer(string='Total actives', readonly=True)
    muixerangues_count = fields.Integer(compute='_compute_muixerangues_count', string='Total muixerangues', store=True)

    @api.multi
    @api.depends('muixeranga_ids')
    def _compute_muixerangues_count(self):
        """
        Calcula el total de muixerangues de l'actuació
        """
        for actuacio in self:
            muixeranga = actuacio.muixeranga_ids
            actuacio.muixerangues_count = len(muixeranga)

    @api.multi
    def _compute_assistencia(self):
        """
        Calcula el total de persones de l'actuació
        """
        for actuacio in self:
            membres = actuacio.membre_actuacio_ids.filtered(lambda x: x.assistencia)
            actives = membres.filtered(lambda x: bool(x.count_actuacio_total))
            len_actives = len(actives)
            len_membres = len(membres)
            data = {}
            if len_actives != actuacio.actives_count:
                data.update({'actives_count': len_actives})
            if len_membres != actuacio.membres_count:
                data.update({'membres_count': len_membres})
            if bool(data):
                actuacio.sudo().write(data)
            actuacio.membres_count_calc = len_membres

    @api.multi
    @api.constrains('data_inici', 'data_final')
    def _check_future_dates(self):
        """
        Ens assegurem que les dates d'inici i de final siguen coherents
        """
        actuacions = self.filtered(lambda x: bool(x.data_inici) and bool(x.data_final))
        for actuacio in actuacions:
            inici = fields.Datetime.from_string(actuacio.data_inici)
            final = fields.Datetime.from_string(actuacio.data_final)
            if inici > final:
                raise ValidationError("No és possible una data inicial major que la data final❗")

    @api.model
    def default_get(self, fields_list):
        """
        Alguns valors per defecte
        """
        res = super(PinyaActuacio, self).default_get(fields_list)
        res['temporada_id'] = self.env['pinya.temporada'].search([('actual', '=', True)]).id
        tipus = self.env.context.get('tipus', False)
        if bool(tipus):
            res['tipus'] = tipus
            if tipus == 'assaig':
                partner = self.env.user.company_id.partner_id
                assaig_dia = int(partner.assaig_dia)
                hora_inici = partner.assaig_hora_inici
                hora_final = partner.assaig_hora_final
                hora_xicalla = partner.assaig_hora_xicalla
                hora_general = partner.assaig_hora_general
                today = datetime.today()
                today_day = today.weekday()
                dies_que_falten = assaig_dia - today_day
                dies_fins_assaig = relativedelta(days=(dies_que_falten)) if dies_que_falten > 0 else relativedelta(days=(dies_que_falten+7))
                dia_assaig = (today + dies_fins_assaig).date()
                inici = dia_assaig + relativedelta(hours=int(hora_inici), minutes=int((hora_inici - int(hora_inici))*60))
                res['data_inici'] = self._tz_to_utc(str(inici))
                final = dia_assaig + relativedelta(hours=int(hora_final), minutes=int((hora_final - int(hora_final))*60))
                res['data_final'] = self._tz_to_utc(str(final))
                if bool(hora_xicalla):
                    xicalla = dia_assaig + relativedelta(hours=int(hora_xicalla), minutes=int((hora_xicalla - int(hora_xicalla))*60))
                    res['data_xicalla'] = self._tz_to_utc(str(xicalla))
                if bool(hora_general):
                    general = dia_assaig + relativedelta(hours=int(hora_general), minutes=int((hora_general - int(hora_general))*60))
                    res['data_general'] = self._tz_to_utc(str(general))

                res['name'] = tipus.capitalize()
                res['zip_id'] = partner.zip_id.id
        return res

    @api.onchange('event_id')
    def onchange_event(self):
        """
        Alguns valors els prenem de l'esdeveniment
        """
        event = self.event_id
        if bool(event):
            self.data_inici = event.date_begin
            self.data_final = event.date_end
            self.zip_id = event.address_id.zip_id.id
        elif self.tipus == 'actuacio':
            self.data_inici = False
            self.data_final = False
            self.zip_id = False

    @api.onchange('data_inici')
    def onchange_data(self):
        """
        El nom dels assajos depén de la data
        """
        tipus = self.tipus
        if tipus != 'assaig':
            return False
        data = self.data_inici
        if not bool(data):
            return False
        data_str = str(datetime.strptime(data, DEFAULT_SERVER_DATETIME_FORMAT).date()).replace('-', '/')
        self.name = tipus.capitalize() + ' ' + data_str

    def action_membres_import(self):
        """
        Funció per importar membres
        """
        view_form_id = self.env.ref('pinya_tecnica.pinya_import_wizard_form_view').id
        name = "Importar membres per a l'actuació"
        model = "pinya.import.wizard"
        action = _get_wizard(view_form_id, name, model)
        return action

    def pinya_muixeranga_wizard(self):
        """
        Funció per importar muixerangues
        """
        view_form_id = self.env.ref('pinya_tecnica.pinya_muixeranga_wizard_form_view').id
        name = "Afegir figures a l'{}".format(self.tipus.replace("actuacio", "actuació"))
        model = "pinya.muixeranga.wizard"
        action = _get_wizard(view_form_id, name, model)
        return action

    def mostrar_muixerangues(self):
        """
        Funció per mostrar muixerangues
        """
        view_search_id = self.env.ref('pinya_tecnica.view_muixeranga_search').id
        view_tree_id = self.env.ref('pinya_tecnica.view_muixeranga_tree_all').id
        view_form_id = self.env.ref('pinya_tecnica.view_muixeranga_form').id
        name = "Muixerangues"
        model = "pinya.muixeranga"
        domain = [('id', 'in', self.muixeranga_ids.ids)]
        ctx = {}
        action = _get_action(view_tree_id, view_form_id, view_search_id, name, model, domain, ctx)
        return action

    def mostrar_membres(self):
        """
        Funció per mostrar membres
        """
        view_search_id = self.env.ref('pinya_tecnica.hr_employee_actuacio_search').id
        view_tree_id = self.env.ref('pinya_tecnica.hr_employee_actuacio_tree').id
        view_form_id = self.env.ref('pinya_tecnica.hr_employee_actuacio_form').id
        name = "Membres"
        model = "hr.employee.actuacio"
        people = self.membre_actuacio_ids.filtered(lambda x: x.assistencia)
        domain = [('id', 'in', people.ids)]
        ctx = dict(self.env.context)
        ctx.update({'actuacio_id': self.id})
        action = _get_action(view_tree_id, view_form_id, view_search_id, name, model, domain, ctx)
        return action

    def action_ready(self):
        """
        Comproba que totes les muixerangues estan preparades per passar a "Preparat"
        """
        i = "' i '"
        muixerangues = self.muixeranga_ids.filtered(lambda x: x.state != 'cancel')
        if not bool(muixerangues):
            error_msg = "Cal que hi hagen muixerangues actives❗"
            raise ValidationError(error_msg)
        not_draft_ready = muixerangues.filtered(lambda x: x.state not in ['ready', 'draft'])
        if bool(not_draft_ready):
            names = not_draft_ready.mapped('name')
            if len(names) == 1:
                names = names[0]
                error_msg = "La muixeranga '{}' no està 'Preparada'❗".format(names)
            else:
                names = "'" + "', '".join(names[0:-1]) + i + names[-1] + "'"
                error_msg = "Les muixerangues {} no estan 'Preparades'❗".format(names)
            raise ValidationError(error_msg)
        draft = muixerangues.filtered(lambda x: x.state == 'draft')
        if bool(draft):
            not_troncs = draft.mapped('tronc_line_ids').filtered(lambda x: not x.membre_tronc_id)
            not_pinyes = draft.mapped('pinya_line_ids').filtered(lambda x: not x.membre_pinya_id)
            if not_troncs or not_pinyes:
                names_t = not_troncs.mapped('muixeranga_tronc_id').sorted('name').mapped('name')
                names_p = not_pinyes.mapped('muixeranga_pinya_id').sorted('name').mapped('name')
                if len(names_t) == 1 and len(names_p) == 1 and names_p == names_t:
                    falta = "el tronc i la pinya"
                    names_t = names_t[0]
                    error_msg = "La muixeranga '{}' li falta preparar {}❗".format(names_t, falta)
                elif len(names_t) == 1 and len(names_p) == 1 and names_p != names_t:
                    falta_t = "li falta preparar el tronc"
                    falta_p = "li falta preparar la pinya"
                    names_t = names_t[0]
                    names_p = names_p[0]
                    error_msg = "La muixeranga '{}' {} i la muixeranga '{}' {}❗".format(names_t, falta_t, names_p, falta_p)
                elif len(names_t) > 1 and len(names_p) > 1 and names_p == names_t:
                    falta_t = "els falten preparar els troncs i les pinyes"
                    names_t = "'" + "', '".join(names_t[0:-1]) + i + names_t[-1] + "'"
                    error_msg = "Les muixerangues {} {}❗".format(names_t, falta_t)
                elif len(names_t) > 1 and len(names_p) > 1 and names_p != names_t:
                    falta_t = "els falta preparar els troncs"
                    falta_p = "els falta preparar les pinyes"
                    names_t = "'" + "', '".join(names_t[0:-1]) + i + names_t[-1] + "'"
                    names_p = "'" + "', '".join(names_p[0:-1]) + i + names_p[-1] + "'"
                    error_msg = "Les muixerangues {} {} i les muixerangues {} {}❗".format(names_t, falta_t, names_p, falta_p)
                elif len(names_t) > 1 and len(names_p) == 1 and names_p != names_t:
                    falta_t = "els falta preparar els troncs"
                    falta_p = "li falta preparar la pinya"
                    names_t = "'" + "', '".join(names_t[0:-1]) + i + names_t[-1] + "'"
                    names_p = names_p[0]
                    error_msg = "Les muixerangues {} {} i la muixeranga '{}' {}❗".format(names_t, falta_t, names_p, falta_p)
                elif len(names_t) == 1 and len(names_p) > 1 and names_p != names_t:
                    falta_t = "li falta preparar el tronc"
                    falta_p = "els falta preparar les pinyes"
                    names_t = names_t[0]
                    names_p = "'" + "', '".join(names_p[0:-1]) + i + names_p[-1] + "'"
                    error_msg = "La muixeranga '{}' {} i les muixerangues {} {}❗".format(names_t, falta_t, names_p, falta_p)
                else:
                    error_msg = "Error❗"
                raise ValidationError(error_msg)
            else:
                for d in draft:
                    d.state = 'ready'
        self.state = 'ready'

    def action_done(self):
        """
        Comproba que totes les muixerangues estan preparades per passar a "Fet"
        """
        i = "' i '"
        not_ready = self.muixeranga_ids.filtered(lambda x: x.state != 'ready')
        if bool(not_ready):
            names = not_ready.mapped('name')
            if len(names) == 1:
                names = names[0]
                error_msg = "La muixeranga '{}' no està 'Preparada'❗".format(names)
            else:
                names = "'" + "', '".join(names[0:-1]) + i + names[-1] + "'"
                error_msg = "Les muixerangues {} no estan 'Preparades'❗".format(names)
            raise ValidationError(error_msg)
        self.state = 'done'

    def action_obrir_assaig(self):
        """
        Obrim l'assaig per a que s'apunte la gent
        """
        self.obert = True

    def action_tancar_assaig(self):
        """
        Tanquem l'assaig per a que no s'apunte la gent
        """
        self.obert = False

    def action_cancel(self):
        """
        Cancelem l'actuació
        """
        muixes = self.muixeranga_ids.filtered(lambda x: x.state != 'cancel')
        for muix in muixes:
            muix.action_cancel()
        self.state = 'cancel'

    def action_draft(self):
        """
        Passem a esborrany l'actuació
        """
        muixes = self.muixeranga_ids.filtered(lambda x: x.state != 'cancel')
        for muix in muixes:
            muix.action_draft()
        self.state = 'draft'

    def calcular_muixerangues(self):
        """
        Calculem totes les muixerangues de l'actuació
        """
        muixes = self.muixeranga_ids.filtered(lambda x: x.state != 'cancel')
        for muix in muixes:
            muix.calcular_muixeranga()
        self.state = 'ready'

    def reset_muixerangues(self):
        """
        Reinicialitzem totes les muixerangues de l'actuació
        """
        self.state = 'draft'
        muixes = self.muixeranga_ids.filtered(lambda x: x.state != 'cancel')
        for muix in muixes:
            muix.reset_muixeranga()

    @api.model
    def _tz_to_utc(self, date):
        """
        Funció auxiliar per passar de tz a utc
        """
        date_dt1 = datetime.strptime(date, DEFAULT_SERVER_DATETIME_FORMAT)
        tz = pytz.timezone('Europe/Madrid')
        date_dt2 = tz.localize(date_dt1, is_dst=None)
        date_dt3 = date_dt2.astimezone(pytz.utc)
        return date_dt3.strftime(DEFAULT_SERVER_DATETIME_FORMAT)

    @api.multi
    def unlink(self):
        """
        Si s'elimina l'actuació, ens assegurem que les muixerangues i els membres, tb s'eliminen
        Compobrar si funciona més senzill amb: ondelete="cascade"
        """
        for actuacio in self:
            actuacio.muixeranga_ids.unlink()
            actuacio.membre_actuacio_ids.unlink()
        res = super(PinyaActuacio, self).unlink()
        return res

    @api.model
    def create(self, vals):
        """
        Afegim els valors de l'esdeveniment i
        Creem els membres en estat assistencia = False
        """
        event = vals.get('event_id', False)
        if event:
            event = self.env['event.event'].browse(event)
            vals['data_inici'] = event.date_begin
            vals['data_final'] = event.date_end
            vals['zip_id'] = event.address_id.zip_id.id
        res = super(PinyaActuacio, self).create(vals)

        empls = self.env['hr.employee'].search([('muixeranguera', '=', True)])
        muix_act_obj = self.env['hr.employee.actuacio']
        data = {
            'actuacio_id': res.id,
        }
        for membre in empls:
            data['employee_id'] = membre.id
            data['name'] = membre.name
            muix_act_obj.create(data)

        if event:
            event.actuacio_id = res.id
        return res

    @api.multi
    def write(self, vals):
        """
        Modifiquem els valors de l'esdeveniment si hi ha canvis
        """
        event = False
        if 'event_id' in vals:
            event = vals.get('event_id', False)
            if event:
                event = self.env['event.event'].browse(event)
                vals['data_inici'] = event.date_begin
                vals['data_final'] = event.date_end
                vals['zip_id'] = event.address_id.zip_id.id
            else:
                vals['data_inici'] = False
                vals['data_final'] = False
                vals['zip_id'] = False
        res = super(PinyaActuacio, self).write(vals)
        if 'event_id' in vals and event:
            event.actuacio_id = self.id
        elif 'event_id' in vals and not event:
            event_obj = self.env['event.event']
            event = event_obj.search([('actuacio_id', '=', self.id)])
            if event:
                event.actuacio_id = False
        return res

