# -*- coding: utf-8 -*-
# (c) 2020 Miquel March <m.marchpuig@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import io
import csv
import base64
import logging
from odoo.exceptions import ValidationError
from odoo import api, models, fields

_logger = logging.getLogger(__name__)


class EmployeeImportWizard(models.TransientModel):
    """
    Assistent per importar als membres de la colla
    """
    _name = "employee.import.wizard"

    file_type = fields.Selection(
        selection=[
            ('csv', 'Arxiu CSV'),
        ],
        default="csv",
        required=True,
        string="Tipus d'arxiu"
    )

    file_data = fields.Binary('Arxiu', required=True)

    def import_employee_btn(self):
        """
        Crea els membres de la colla
        """

        decoded_data = base64.decodebytes(self.file_data)
        membres = self.import_employee(decoded_data)
        if not bool(membres):
            error_msg = "No hi ha membres correctes en l'arxiu❗"
            raise ValidationError(error_msg)

        res = True
        posicions = [
            'alsadora', 'base', 'segones', 'terces', 'xicalla',
            'agulla', 'colze', 'contrafort', 'crossa', 'lateral', 'mans', 'peu', 'pinyerista', 'tap', 'vent',
            'cantadora_aixecat', 'contrafort_aixecat', 'forsuda_aixecat'
        ]

        wizard_obj = self.env['partner.employee.create.wizard']
        wizard_line_obj = self.env['partner.employee.create.wizard.line']
        for row in membres:
            zip_id = self.get_zip_id(row.get('zip_cp', False), row.get('zip_ciutat', False))
            data = {
                'nom': row.get('nom', False),
                'vat': row.get('vat', False),
                'email': row.get('email', False),
                'phone': row.get('phone', False),
                'carrer': row.get('carrer', False),
                'carrer2': row.get('carrer2', False),
                'zip_id': zip_id.id,
                'nom_croquis': row.get('nom_croquis', False),
                'data_inscripcio': row.get('data_inscripcio', False),
                'data_naixement': row.get('data_naixement', False),
                'notes': row.get('notes', False),
                'gender': row.get('gender', False),
                'marital_status': row.get('marital_status', False),
                'height': row.get('height', False),
                'alsada_muscle': row.get('alsada_muscle', False),
                'alsada_bras': row.get('alsada_bras', False),
                'weight': row.get('weight', False)
            }

            w = wizard_obj.create(data)

            for posicio in posicions:
                level = row.get(posicio, False)
                if bool(level):
                    hr_skill = self.env.ref('pinya_tecnica.' + posicio)
                    data = {
                        'wizard_id': w.id,
                        'skill_id': hr_skill.id,
                        'level': str(level),
                    }
                    wizard_line_obj.create(data)

            res_w = w.create_partner_employee()
            res = res and res_w

        return res

    def import_employee(self, decoded_data):
        """
        Importa les dades del csv
        """
        csv_file = io.TextIOWrapper(io.BytesIO(decoded_data), encoding='utf-8')
        csv_raw = csv.DictReader(csv_file, delimiter=',')

        return csv_raw

    def get_zip_id(self, cp, ciutat):
        """
        Transforma el codi postal en objecte 'res.better.zip'
        """
        zip_obj = self.env['res.better.zip']
        filtro = [('name', '=', cp)]
        if bool(ciutat):
            filtro.append(('city', 'ilike', ciutat))
        zips = zip_obj.search(filtro)

        if bool(zips) and len(zips) == 1:
            zip_id = zips
        else:
            zip_id = zip_obj

        return zip_id


