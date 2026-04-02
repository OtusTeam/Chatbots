from __future__ import annotations

from dotenv import load_dotenv

from crm_client import CrmClient
from models import LeadPayload


def main() -> None:
    load_dotenv()
    client = CrmClient.from_env()
    payload = LeadPayload(
        name="Ivan Petrov",
        phone="+79991112233",
        email="ivan.petrov4@example.com",
        comment="Заявка из Telegram анкеты",
    )
    result = client.create_lead(payload)
    print(
        f"provider={result.provider} ok={result.ok} duplicate={result.duplicate} "
        f"entity_id={result.entity_id} message={result.message}"
    )


if __name__ == "__main__":
    main()
