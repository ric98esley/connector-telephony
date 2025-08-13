# Copyright 2023 ForgeFlow S.L. (https://www.forgeflow.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging
from typing import Dict, List, Optional

import requests

_logger = logging.getLogger(__name__)


class SmsApiEvolution:
    """Lightweight client for Evolution API using the same interface as Odoo's SmsApi.

    This class intentionally does not inherit from Odoo models; it mimics
    `addons/sms/tools/sms_api.SmsApi` so it can be dropped-in where needed.
    """

    def __init__(self, env, account=None):
        self.env = env
        self.account = account or self.env['iap.account'].get('sms')

    # Public API compatible with SmsApi
    def _send_sms_batch(self, messages: List[Dict], delivery_reports_url: Optional[str] = False):
        """Send SMS using Evolution API.

        Arguments mirror Odoo's SmsApi._send_sms_batch to remain compatible.
        `messages` is a list of dicts:
          - content: str
          - numbers: list[ { 'uuid': str, 'number': str } ]
        Returns a list of results: [{ 'uuid': str, 'state': str, 'credit': int }]
        """
        if not self.env.registry.ready:
            # Align with Odoo's behavior: do not contact external services during installation
            from odoo import exceptions
            raise exceptions.AccessError("Unavailable during module installation.")

        account = self.account.sudo()
        if not account or getattr(account, 'provider', None) != 'evolution':
            # Defensive: Only this client should be used when provider is Evolution
            # Callers should route here conditionally. We log and fail with server_error otherwise.
            _logger.warning("SmsApiEvolution used with non-evolution provider; aborting call.")
            return [
                {"uuid": number.get('uuid'), "state": "server_error"}
                for message in messages for number in message.get('numbers', [])
            ]

        base_url = (account.evolution_api_url or '').rstrip('/')
        instance_id = (account.evolution_instance_id or '').strip()
        api_key = (account.evolution_api_key or '').strip()

        if not base_url or not instance_id or not api_key:
            _logger.error("Evolution credentials are missing on iap.account %s", account.id)
            return [
                {"uuid": number.get('uuid'), "state": "server_error"}
                for message in messages for number in message.get('numbers', [])
            ]

        url = f"{base_url}/message/sendText/{instance_id}"
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'odoo/18.0',
            'apikey': api_key,
        }

        timeout_seconds = 15
        results: List[Dict] = []

        for message in messages:
            text = message.get('content') or ''
            for number_info in message.get('numbers', []):
                uuid = number_info.get('uuid')
                number = (number_info.get('number') or '').strip()

                if not number:
                    results.append({'uuid': uuid, 'state': 'wrong_number_format'})
                    continue

                payload = {
                    'number': number,
                    'text': text,
                    # Optional fields supported by Evolution; not strictly required
                    # Uncomment or parameterize via ir.config_parameter if needed
                    # 'delay': 0,
                    # 'linkPreview': True,
                }

                try:
                    response = requests.post(url, json=payload, headers=headers, timeout=timeout_seconds)
                except Exception as exc:
                    _logger.exception("Evolution send failed for uuid %s: %s", uuid, exc)
                    results.append({'uuid': uuid, 'state': 'server_error'})
                    continue

                state = self._map_response_to_state(response)
                results.append({'uuid': uuid, 'state': state})

        return results

    def _map_response_to_state(self, response: requests.Response) -> str:
        """Map Evolution HTTP response to IAP-like state strings expected by Odoo.

        success -> 'success'
        4xx with likely number issue -> 'wrong_number_format'
        401/403 -> 'unregistered'
        otherwise -> 'server_error'
        """
        if 200 <= response.status_code < 300:
            return 'success'

        if response.status_code in (401, 403):
            return 'unregistered'

        if response.status_code in (400, 404):
            # Try to refine using payload if available
            try:
                data = response.json()
                message = (data.get('message') or data.get('error') or '').lower()
            except Exception:
                message = ''
            if any(token in message for token in ['invalid', 'number', 'format']):
                return 'wrong_number_format'
            return 'server_error'

        return 'server_error'