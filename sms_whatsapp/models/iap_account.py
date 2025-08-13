# Copyright 2023 ForgeFlow S.L. (https://www.forgeflow.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class IapAccount(models.Model):
    _inherit = "iap.account"

    provider = fields.Selection(
        selection_add=[("whatsapp", "Whatsapp"), ("evolution", "Evolution Api")],
        ondelete={
            "whatsapp": "set default",
            "evolution": "set default",
        },
    )
    
    ## Evolution Api
    evolution_api_key = fields.Char(string="Evolution Api Key")
    evolution_instance_id = fields.Char(string="Evolution Instance Id")
    evolution_api_url = fields.Char(string="Evolution Api Url")

    def _get_service_from_provider(self):
        if self.provider == "whatsapp":
            return "sms"
        elif self.provider == "evolution":
            return "sms"

        return super()._get_service_from_provider()