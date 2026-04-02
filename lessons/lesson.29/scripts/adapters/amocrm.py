from __future__ import annotations

import httpx

from models import CrmResult, LeadPayload


class AmoCrmAdapter:
    provider_name = "amocrm"

    def __init__(self, base_domain: str, access_token: str, dry_run: bool = True, timeout: float = 8.0) -> None:
        self.base_domain = base_domain.strip()
        self.access_token = access_token.strip()
        self.dry_run = dry_run
        self.timeout = timeout

    def create_lead(self, payload: LeadPayload, external_id: str) -> CrmResult:
        lead_data = [
            {
                "name": f"TG lead: {payload.name}",
                "custom_fields_values": [
                    {"field_name": "Phone", "values": [{"value": payload.phone}]},
                    {"field_name": "Email", "values": [{"value": payload.email}]},
                    {"field_name": "Comment", "values": [{"value": payload.comment}]},
                    {"field_name": "ExternalId", "values": [{"value": external_id}]},
                ],
            }
        ]

        if self.dry_run or not self.base_domain or not self.access_token:
            return CrmResult(
                ok=True,
                provider=self.provider_name,
                entity_id=f"dryrun-{external_id[:8]}",
                duplicate=False,
                message=f"Dry-run lead payload ready: {lead_data[0]['name']}",
            )

        url = f"https://{self.base_domain}/api/v4/leads"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = httpx.post(url, json=lead_data, headers=headers, timeout=self.timeout)
        response.raise_for_status()
        body = response.json()
        embedded = body.get("_embedded", {})
        leads = embedded.get("leads", [])
        entity_id = str(leads[0]["id"]) if leads else "unknown"
        return CrmResult(ok=True, provider=self.provider_name, entity_id=entity_id, duplicate=False, message="Lead created")
