from __future__ import annotations

from dataclasses import dataclass

from api_client import ApiClient

# Коды интерпретации погоды WMO (WW) по документации Open-Meteo:
_OPEN_METEO_WEATHER_CODE_RU: dict[int, str] = {
    0: "Ясно",
    1: "Преимущественно ясно",
    2: "Переменная облачность",
    3: "Пасмурно",
    45: "Туман",
    48: "Инейный туман",
    51: "Слабая морось",
    53: "Умеренная морось",
    55: "Сильная морось",
    56: "Слабая ледяная морось",
    57: "Сильная ледяная морось",
    61: "Слабый дождь",
    63: "Умеренный дождь",
    65: "Сильный дождь",
    66: "Слабый ледяной дождь",
    67: "Сильный ледяной дождь",
    71: "Слабый снег",
    73: "Умеренный снег",
    75: "Сильный снег",
    77: "Снежная крупа",
    80: "Слабые ливни",
    81: "Умеренные ливни",
    82: "Сильные ливни",
    85: "Слабые снегопады",
    86: "Сильные снегопады",
    95: "Гроза (слабая или умеренная)",
    96: "Гроза с небольшим градом",
    99: "Гроза с сильным градом",
}


def open_meteo_weather_description_ru(code: int) -> str:
    return _OPEN_METEO_WEATHER_CODE_RU.get(code, f"Неизвестный код погоды ({code})")


@dataclass
class WeatherResult:
    city: str
    temperature_c: float
    wind_speed_ms: float
    weather_code: int
    condition_ru: str


class WeatherAdapter:
    GEO_URL = "https://geocoding-api.open-meteo.com/v1/search"
    FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

    def __init__(self, client: ApiClient) -> None:
        self.client = client

    def get_current_weather(self, city: str) -> WeatherResult:
        geo = self.client.get_json(self.GEO_URL, params={"name": city, "count": 1, "language": "ru"})
        results = geo.get("results", [])

        if not results:
            raise ValueError(f"City not found: {city}")

        first = results[0]
        latitude = first["latitude"]
        longitude = first["longitude"]
        city_name = first["name"]

        payload = self.client.get_json(
            self.FORECAST_URL,
            params={
                "latitude": latitude,
                "longitude": longitude,
                "current": "temperature_2m,wind_speed_10m,weather_code",
            },
        )

        current = payload.get("current")
        if not current:
            raise ValueError("Open-Meteo response does not contain current weather")

        wcode = int(current["weather_code"])
        return WeatherResult(
            city=city_name,
            temperature_c=float(current["temperature_2m"]),
            wind_speed_ms=float(current["wind_speed_10m"]),
            weather_code=wcode,
            condition_ru=open_meteo_weather_description_ru(wcode),
        )
