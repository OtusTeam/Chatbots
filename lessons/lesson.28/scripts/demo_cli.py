from __future__ import annotations

import os

from dotenv import load_dotenv

from adapters.rates import RatesAdapter
from adapters.weather import WeatherAdapter
from api_client import ApiClient, ApiClientConfig


def build_client() -> ApiClient:
    load_dotenv()
    cfg = ApiClientConfig(
        timeout=float(os.getenv("HTTP_TIMEOUT", "8.0")),
        connect_timeout=float(os.getenv("HTTP_CONNECT_TIMEOUT", "3.0")),
        retries=int(os.getenv("HTTP_RETRIES", "1")),
        backoff_seconds=float(os.getenv("HTTP_BACKOFF_SECONDS", "0.4")),
        cache_ttl_seconds=int(os.getenv("CACHE_TTL_SECONDS", "120")),
    )
    return ApiClient(cfg)


def main() -> None:
    with build_client() as client:
        weather = WeatherAdapter(client).get_current_weather("Moscow")
        print(
            f"[WEATHER] {weather.city}: {weather.condition_ru} "
            f"({weather.temperature_c} °C, ветер {weather.wind_speed_ms} м/с)"
        )

        rate = RatesAdapter(client).get_rate("USD", "RUB")
        print(f"[RATE] {rate.base}->{rate.quote} = {rate.rate} ({rate.date})")


if __name__ == "__main__":
    main()
