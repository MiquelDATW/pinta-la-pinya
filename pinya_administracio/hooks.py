# -*- coding: utf-8 -*-
# (c) 2020 Miquel March <m.marchpuig@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
import datetime
from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def post_init_hook(cr, registry):

    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})

        root = env.ref('base.user_root')
        account_user = env.ref('account.group_account_user')
        membership_manager = env.ref('membership_extension.group_membership_manager')

        new_ids = list(set(root.groups_id.ids) | {account_user.id} | {membership_manager.id})
        root.groups_id = [(6, 0, new_ids)]

        year = str(datetime.datetime.now().year)
        quota_anual = env.ref('product.membership_anual_quota_member')
        quota_anual.write({
            'name': "Quota completa {}".format(year),
            'description': "Quota de l'any {} membre complet de la colla.".format(year),
            'membership_date_from': "{}/01/01".format(year),
            'membership_date_to': "{}/12/31".format(year),
        })
        quota_anual = env.ref('product.membership_collaborator_quota_anual')
        quota_anual.write({
            'name': "Quota col·laborador {}".format(year),
            'description': "Quota de l'any {} membre col·laborador de la colla.".format(year),
            'membership_date_from': "01/01/{}".format(year),
            'membership_date_to': "31/12/{}".format(year),
        })



