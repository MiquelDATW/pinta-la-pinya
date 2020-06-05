# -*- coding: utf-8 -*-
# (c) 2020 Miquel March <m.marchpuig@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from odoo.exceptions import ValidationError
from datetime import datetime
from odoo import api, models, fields

_logger = logging.getLogger(__name__)


class PartnerEmployeeCreateWizard(models.TransientModel):
    """
    Assistent per crear al mateix temps: l'empleat i el contacte
    """
    _name = "partner.employee.create.wizard"

    image = fields.Binary("Image", attachment=True, help="Limitat a 1024x1024px.")

    nom = fields.Char("Nom")
    vat = fields.Char("NIF")
    email = fields.Char("Email")
    phone = fields.Char("Teléfon")
    carrer = fields.Char("Carrer")
    carrer2 = fields.Char("Carrer 2")
    zip_id = fields.Many2one("res.better.zip", "Zip")
    nom_croquis = fields.Char(string="Nom del croquis", help="Nom que apareix en els croquis")
    data_inscripcio = fields.Date(string="Data inscripció")
    data_naixement = fields.Date(string="Data de naixement")
    notes = fields.Text(string="Notes")
    colla_id = fields.Many2one('res.partner', 'Colla', default=1, readonly=True)

    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ], string="Génere")
    marital_status = fields.Selection([
        ('single', 'Single'),
        ('married', 'Married'),
        ('cohabitant', 'Legal Cohabitant'),
        ('widower', 'Widower'),
        ('divorced', 'Divorced')
    ], string='Estat civil')

    employee_skill_ids = fields.One2many("partner.employee.create.wizard.line", "wizard_id", string="Posicions")

    height = fields.Integer("Height")
    alsada_muscle = fields.Integer(string="Alçada muscle")
    alsada_bras = fields.Integer(string="Alçada braços")
    weight = fields.Float(string="Weight", digits=(4, 1))

    @api.model
    def default_get(self, fields_list):
        """
        Alguns valors per defecte
        """
        res = super(PartnerEmployeeCreateWizard, self).default_get(fields_list)
        res.update({'data_inscripcio': datetime.today().date()})
        return res

    def create_partner_employee(self):
        """
        Crea al mateix temps: l'empleat, el contacte i l'usuari
        """
        users_obj = self.env['res.users']
        employee_obj = self.env['hr.employee']
        emp_skill_obj = self.env['hr.employee.skill']
        anthropometry_obj = self.env['hr.employee.anthropometry']

        data = {
            'active': True,
            'company_ids': [[6, False, [1]]],
            'company_id': 1,
            'lang': "ca_ES",
            'tz': "Europe/Madrid",
            'name': self.nom,
            'login': self.nom,
            'image': self.image,
        }
        user = users_obj.create(data)
        pinya_user = self.env.ref("pinya_tecnica.group_pinya_user")
        user.groups_id = [(6, 0, (user.groups_id | pinya_user).ids)]
        _logger.info("Creant usuari: {}❗".format(user.name))

        partner = user.partner_id

        data = {
            'muixeranguera': True,
            'colla_id': self.colla_id.id,
            'email': self.email,
            'mobile': self.phone,
            'vat': self.vat,
            'street': self.carrer,
            'street2': self.carrer2,
            'zip_id': self.zip_id.id,
            'city': self.zip_id.city,
            'country_id': self.zip_id.country_id.id,
            'state_id': self.zip_id.state_id.id,
            'comment': self.notes,
        }
        partner.write(data)
        _logger.info("Creant contacte: {}❗".format(partner.name))

        data = {
            'image': partner.image,
            'name': self.nom,
            'nom_croquis': self.nom_croquis,
            'address_home_id': partner.id,
            'gender': self.gender,
            'marital': self.marital_status,
            'birthday': self.data_naixement,
            'data_inscripcio': self.data_inscripcio,
            'notes': self.notes,
        }
        employee = employee_obj.create(data)
        partner.membre_id = employee.id
        _logger.info("Creant empleat: {}❗".format(employee.name))

        lines = self.employee_skill_ids
        skills = emp_skill_obj
        for line in lines:
            data = {
                'employee_id': employee.id,
                'skill_id': line.skill_id.id,
                'level': line.level,
            }
            skills += emp_skill_obj.create(data)

        mesura = True
        if bool(self.height) and bool(self.weight):
            data = {
                'data': self.data_inscripcio,
                'employee_id': employee.id,
                'height': self.height,
                'weight': self.weight,
                'alsada_muscle': self.alsada_muscle,
                'alsada_bras': self.alsada_bras,
            }
            mesura = anthropometry_obj.create(data)

        res = bool(partner) and bool(employee) and bool(skills) and bool(mesura)
        return res


class PartnerEmployeeCreateWizardLine(models.TransientModel):
    _name = "partner.employee.create.wizard.line"

    wizard_id = fields.Many2one('partner.employee.create.wizard', 'Wizard')
    skill_id = fields.Many2one('hr.skill', string="Posició")
    level = fields.Selection(
        [('0', 'Junior'),
         ('1', 'Intermediate'),
         ('2', 'Senior'),
         ('3', 'Expert')], 'Nivell', default='0')

