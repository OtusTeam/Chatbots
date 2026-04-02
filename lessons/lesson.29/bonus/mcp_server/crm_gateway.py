from __future__ import annotations

from crm.crm_client import CrmClient
from crm.models import LeadPayload


class CrmGateway:
    def __init__(self) -> None:
        self.client = CrmClient.from_env()

    def create_lead(
        self,
        *,
        name: str,
        phone: str,
        email: str,
        comment: str,
        source: str = "mcp-bot",
    ) -> dict[str, object]:
        name = (name or "").strip()
        phone = (phone or "").strip()
        email = (email or "").strip()
        comment = (comment or "").strip()
        source = (source or "mcp-bot").strip()

        if not name:
            raise ValueError("name is required")
        if not phone:
            raise ValueError("phone is required")
        if "@" not in email:
            raise ValueError("email must contain @")

        payload = LeadPayload(
            name=name,
            phone=phone,
            email=email,
            comment=f"{comment}\nsource={source}",
        )
        result = self.client.create_lead(payload)
        return {
            "ok": result.ok,
            "provider": result.provider,
            "entity_id": result.entity_id,
            "duplicate": result.duplicate,
            "message": result.message,
        }
