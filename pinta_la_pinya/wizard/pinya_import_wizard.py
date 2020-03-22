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


class PinyaImportWizard(models.TransientModel):
    _name = "pinya.import.wizard"

    file_type = fields.Selection(
        selection=[
            ('csv', 'Archivo CSV'),
        ],
        default="csv",
        required=True,
        string="Tipus d'arxiu"
    )

    file_data = fields.Binary('Arxiu', required=True)

    def import_pinya_btn(self):
        actuacio = self.env.context.get('actuacio')
        if not bool(actuacio):
            error_msg = "No hi ha un assaig o actuació guardat❗"
            raise ValidationError(error_msg)

        decoded_data = base64.decodebytes(self.file_data)
        membres = self.import_pinya(decoded_data)
        if not bool(membres):
            error_msg = "No hi ha membres correctes en l'arxiu❗"
            raise ValidationError(error_msg)

        actuacio = self.env['pinya.actuacio'].browse(actuacio)
        actuacio.membre_ids = [(6, 0, membres.ids)]

        return False

    def import_pinya(self, decoded_data):
        csv_file = io.TextIOWrapper(io.BytesIO(decoded_data), encoding='utf-8')
        csv_raw = csv.DictReader(csv_file, delimiter=',')

        membre_obj = self.env['hr.employee']
        validos = self.env['hr.employee']
        error_msg = ""
        for row in csv_raw:
            adult1 = row.get('Adult 1') or membre_obj

            if not bool(adult1):
                continue

            adult = membre_obj.search([('name', 'ilike', adult1)])
            if bool(adult) and len(adult) == 1:
                validos |= adult
            elif bool(adult) and len(adult) > 1:
                if bool(error_msg):
                    error_msg += "\n"
                else:
                    error_msg += "Error❗\n"
                error_names = "'" + "', '".join(adult.mapped('name')) + "'"
                error_msg += "Hi ha més d'una persona amb nom semblant a '{}':\n {}❗".format(adult1, error_names)
            else:
                if bool(error_msg):
                    error_msg += "\n"
                else:
                    error_msg += "Error❗\n"
                error_msg += "No hi ha cap persona amb el nom '{}'❗".format(adult1)

        if bool(error_msg):
            raise ValidationError(error_msg)

        return validos
