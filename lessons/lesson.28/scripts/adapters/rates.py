from __future__ import annotations

from dataclasses import dataclass

from api_client import ApiClient


@dataclass
class RateResult:
    base: str
    quote: str
    rate: float
    date: str


class RatesAdapter:
    # Публичный API без ключа доступа.
    BASE_URL = "https://open.er-api.com/v6/latest"

    def __init__(self, client: ApiClient) -> None:
        self.client = client

    def get_rate(self, base: str, quote: str) -> RateResult:
        base_u = base.upper()
        quote_u = quote.upper()
        payload = self.client.get_json(f"{self.BASE_URL}/{base_u}", params=None)
        rates = payload.get("rates", {})
        if quote_u not in rates:
            raise ValueError(f"Rate {base_u}->{quote_u} not found")
        date = str(payload.get("time_last_update_utc", ""))
        return RateResult(base=base_u, quote=quote_u, rate=float(rates[quote_u]), date=date)
