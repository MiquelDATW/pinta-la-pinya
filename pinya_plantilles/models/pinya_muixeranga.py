# -*- coding: utf-8 -*-
# (c) 2020 Miquel March <m.marchpuig@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import statistics
import random
from odoo import models, fields, api, exceptions, _
from odoo.exceptions import ValidationError


class PinyaMuixeranga(models.Model):
    _inherit = "pinya.muixeranga"

    def _get_plantilla(self):
        torreta = self.env.ref('pinya_plantilles.torreta').id
        plantilla = self.plantilla_id.id
        if plantilla == torreta:
            res = 'torreta'
        else:
            res = False
        return res

    def _get_company(self):
        res = self.env.user.company_id.partner_id
        return res

    def _get_tronc_posicio(self, posicio):
        res = []
        pos = self.env.ref('pinta_la_pinya.' + posicio).id
        troncs = self.tronc_line_ids.filtered(lambda x: x.posicio_id.id == pos)
        for t in troncs:
            res.append(t)
        return res

    def _get_pinya_posicio(self, posicio, cordons):
        res = []
        pos = self.env.ref('pinta_la_pinya.' + posicio).id
        pinyes = self.pinya_line_ids.filtered(lambda x: x.posicio_id.id == pos and x.cordo in cordons)
        for p in pinyes:
            res.append(p.sorted('cordo'))
        return res

