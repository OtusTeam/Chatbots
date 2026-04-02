from __future__ import annotations

from dataclasses import dataclass


@dataclass
class LeadPayload:
    name: str
    phone: str
    email: str
    comment: str


@dataclass
class CrmResult:
    ok: bool
    provider: str
    entity_id: str
    duplicate: bool
    message: str
