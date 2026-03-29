from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

import httpx


class ApiClientError(Exception):
    """Базовый класс ошибок API-клиента."""


class ApiClientTimeoutError(ApiClientError):
    """Исключение при таймауте внешнего API."""


class ApiClientNetworkError(ApiClientError):
    """Исключение при сетевых сбоях на транспортном уровне."""


class ApiClientHttpError(ApiClientError):
    """Исключение при HTTP-ответах с кодами 4xx/5xx."""

    def __init__(self, status_code: int, message: str) -> None:
        super().__init__(f"HTTP {status_code}: {message}")
        self.status_code = status_code
        self.message = message


@dataclass
class ApiClientConfig:
    timeout: float = 8.0
    connect_timeout: float = 3.0
    retries: int = 1
    backoff_seconds: float = 0.4
    cache_ttl_seconds: int = 120


class ApiClient:
    def __init__(self, config: ApiClientConfig | None = None) -> None:
        self.config = config or ApiClientConfig()
        timeout = httpx.Timeout(self.config.timeout, connect=self.config.connect_timeout)
        self._client = httpx.Client(timeout=timeout)
        self._cache: dict[str, tuple[float, dict[str, Any]]] = {}

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "ApiClient":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def get_json(self, url: str, *, params: dict[str, Any] | None = None, use_cache: bool = True) -> dict[str, Any]:
        cache_key = self._build_cache_key(url, params)
        if use_cache:
            cached = self._read_cache(cache_key)
            if cached is not None:
                return cached

        last_error: Exception | None = None
        attempts = self.config.retries + 1

        for attempt in range(1, attempts + 1):
            try:
                response = self._client.get(url, params=params)
                response.raise_for_status()
                payload = response.json()
                if isinstance(payload, dict):
                    if use_cache:
                        self._write_cache(cache_key, payload)
                    return payload
                raise ApiClientError("Expected JSON object in response")
            except httpx.TimeoutException as err:
                last_error = ApiClientTimeoutError(str(err))
            except httpx.HTTPStatusError as err:
                status = err.response.status_code
                try:
                    message = err.response.text
                except Exception:
                    message = "No response body"
                if status in (408, 429, 500, 502, 503, 504) and attempt < attempts:
                    last_error = ApiClientHttpError(status, message)
                else:
                    raise ApiClientHttpError(status, message) from err
            except httpx.RequestError as err:
                last_error = ApiClientNetworkError(str(err))

            if attempt < attempts:
                time.sleep(self.config.backoff_seconds)

        if last_error is not None:
            raise last_error
        raise ApiClientError("Unknown API client error")

    def _build_cache_key(self, url: str, params: dict[str, Any] | None) -> str:
        if not params:
            return url
        normalized = "&".join(f"{k}={params[k]}" for k in sorted(params))
        return f"{url}?{normalized}"

    def _read_cache(self, key: str) -> dict[str, Any] | None:
        item = self._cache.get(key)
        if item is None:
            return None
        ts, payload = item
        if time.time() - ts > self.config.cache_ttl_seconds:
            self._cache.pop(key, None)
            return None
        return payload

    def _write_cache(self, key: str, payload: dict[str, Any]) -> None:
        self._cache[key] = (time.time(), payload)
