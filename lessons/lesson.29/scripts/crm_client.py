from __future__ import annotations

import hashlib
import json
import os
from typing import Protocol

from adapters.amocrm import AmoCrmAdapter
from adapters.bitrix24 import Bitrix24Adapter
from models import CrmResult, LeadPayload


class CrmAdapter(Protocol):
    provider_name: str

    def create_lead(self, payload: LeadPayload, external_id: str) -> CrmResult:
        raise NotImplementedError


class DuplicateGuard:
    def __init__(self, storage_path: str = ".dedup_store.json") -> None:
        self.storage_path = storage_path

    def _read_store(self) -> dict[str, str]:
        if not os.path.exists(self.storage_path):
            return {}
        with open(self.storage_path, "r", encoding="utf-8") as fh:
            return json.load(fh)

    def _write_store(self, data: dict[str, str]) -> None:
        with open(self.storage_path, "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2)

    def check_or_mark(self, provider: str, payload: LeadPayload) -> bool:
        key_raw = f"{provider}:{payload.phone.lower()}:{payload.email.lower()}"
        key = hashlib.sha256(key_raw.encode("utf-8")).hexdigest()
        store = self._read_store()
        if key in store:
            return True
        store[key] = "seen"
        self._write_store(store)
        return False


class CrmClient:
    def __init__(self, adapter: CrmAdapter, dedup_guard: DuplicateGuard | None = None) -> None:
        self.adapter = adapter
        self.dedup_guard = dedup_guard or DuplicateGuard()

    @classmethod
    def from_env(cls) -> "CrmClient":
        provider = os.getenv("CRM_PROVIDER", "bitrix24").strip().lower()
        dry_run = os.getenv("CRM_DRY_RUN", "true").strip().lower() == "true"

        if provider == "amocrm":
            adapter: CrmAdapter = AmoCrmAdapter(
                base_domain=os.getenv("AMOCRM_BASE_DOMAIN", ""),
                access_token=os.getenv("AMOCRM_ACCESS_TOKEN", ""),
                dry_run=dry_run,
            )
        else:
            entity_type_id_raw = os.getenv("BITRIX24_ENTITY_TYPE_ID", "1").strip()
            try:
                entity_type_id = int(entity_type_id_raw)
            except ValueError:
                entity_type_id = 1
            adapter = Bitrix24Adapter(
                webhook_url=os.getenv("BITRIX24_WEBHOOK_URL", ""),
                entity_type_id=entity_type_id,
                dry_run=dry_run,
            )
        return cls(adapter=adapter)

    def create_lead(self, payload: LeadPayload) -> CrmResult:
        is_dup = self.dedup_guard.check_or_mark(self.adapter.provider_name, payload)
        if is_dup:
            return CrmResult(
                ok=True,
                provider=self.adapter.provider_name,
                entity_id="duplicate-skip",
                duplicate=True,
                message="Duplicate detected, create skipped",
            )

        external_id = hashlib.md5(f"{payload.phone}:{payload.email}".encode("utf-8")).hexdigest()
        return self.adapter.create_lead(payload, external_id=external_id)
