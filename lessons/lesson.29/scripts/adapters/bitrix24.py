from __future__ import annotations

import httpx

from models import CrmResult, LeadPayload


class Bitrix24Adapter:
    provider_name = "bitrix24"

    def __init__(
        self,
        webhook_url: str,
        entity_type_id: int = 1,
        dry_run: bool = True,
        timeout: float = 8.0,
    ) -> None:
        self.webhook_url = webhook_url.rstrip("/")
        self.entity_type_id = entity_type_id
        self.dry_run = dry_run
        self.timeout = timeout

    def create_lead(self, payload: LeadPayload, external_id: str) -> CrmResult:
        data = {
            "entityTypeId": self.entity_type_id,
            "fields": {
                "TITLE": f"TG lead: {payload.name}",
                "NAME": payload.name,
                "PHONE": [{"VALUE": payload.phone, "VALUE_TYPE": "WORK"}],
                "EMAIL": [{"VALUE": payload.email, "VALUE_TYPE": "WORK"}],
                "COMMENTS": f"{payload.comment}\nexternal_id={external_id}",
                "SOURCE_ID": "WEB",
                "STATUS_ID": "NEW",
            },
            "params": {"REGISTER_SONET_EVENT": "Y"},
        }

        if self.dry_run or not self.webhook_url:
            return CrmResult(
                ok=True,
                provider=self.provider_name,
                entity_id=f"dryrun-{external_id[:8]}",
                duplicate=False,
                message=f"Dry-run lead payload ready: {data['fields']['TITLE']}",
            )

        url = f"{self.webhook_url}/crm.item.add"
        response = httpx.post(url, json=data, timeout=self.timeout)
        response.raise_for_status()
        body = response.json()
        result = body.get("result")
        entity_id = "unknown"
        if isinstance(result, dict):
            item = result.get("item")
            if isinstance(item, dict) and item.get("id") is not None:
                entity_id = str(item.get("id"))
            elif result.get("id") is not None:
                entity_id = str(result.get("id"))
        elif result is not None:
            entity_id = str(result)
        return CrmResult(ok=True, provider=self.provider_name, entity_id=entity_id, duplicate=False, message="Lead created")
