from __future__ import annotations

import asyncio
from typing import Any, Optional

import httpx


class MLClient:
    def __init__(
        self,
        base_url: str,
        timeout: float = 10.0,
        connect_attempts: int = 5,
        retry_delay: float = 1.0,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.connect_attempts = connect_attempts
        self.retry_delay = retry_delay

    async def _request(
        self,
        method: str,
        path: str,
        payload: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        last_error: Optional[httpx.RequestError] = None

        for attempt in range(1, self.connect_attempts + 1):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.request(
                        method,
                        f"{self.base_url}{path}",
                        json=payload,
                    )
                    response.raise_for_status()
                    return response.json()
            except httpx.RequestError as exc:
                last_error = exc
                if attempt == self.connect_attempts:
                    break
                await asyncio.sleep(self.retry_delay)

        assert last_error is not None
        raise last_error

    async def hems_forecast(self) -> dict[str, Any]:
        return await self._request("GET", "/hems/forecast")

    async def hems_status(self) -> dict[str, Any]:
        return await self._request("GET", "/hems/status")

    async def hems_optimize(self, payload: dict[str, Any]) -> dict[str, Any]:
        return await self._request("POST", "/hems/optimize", payload)

    async def classify(self, feature_vector: dict[str, Any]) -> dict[str, Any]:
        return await self._request("POST", "/classify", {"features": feature_vector})
