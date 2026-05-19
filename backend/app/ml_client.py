import asyncio
from typing import Any

import httpx


class MLClient:
    def __init__(
        self,
        base_url: str,
        timeout: float = 10.0,
        connect_attempts: int = 5,
        retry_delay: float = 1.0,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.connect_attempts = connect_attempts
        self.retry_delay = retry_delay

    async def _post(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        last_error: httpx.RequestError | None = None

        for attempt in range(1, self.connect_attempts + 1):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.post(f"{self.base_url}{path}", json=payload)
                    response.raise_for_status()
                    return response.json()
            except httpx.RequestError as exc:
                last_error = exc
                if attempt == self.connect_attempts:
                    break
                await asyncio.sleep(self.retry_delay)

        assert last_error is not None
        raise last_error

    async def classify(self, feature_vector: dict[str, Any]) -> dict[str, Any]:
        return await self._post("/classify", feature_vector)

    async def cluster(
        self,
        vectors: list[dict[str, Any]],
        n_clusters: int = 4,
    ) -> dict[str, Any]:
        payload = {
            "vectors": vectors,
            "n_clusters": n_clusters,
        }
        return await self._post("/cluster", payload)

    async def suggest(
        self,
        vectors: list[dict[str, Any]],
        labels: list[int],
        known: list[str],
    ) -> list[Any]:
        payload = {
            "vectors": vectors,
            "labels": labels,
            "known": known,
        }
        return await self._post("/suggest", payload)

    async def energy_forecast(self, current_hour: int, weekday: int) -> dict[str, Any]:
        return await self._post(
            "/energy/forecast",
            {
                "current_hour": current_hour,
                "weekday": weekday,
            },
        )

    async def anomaly_detect(self, fv: dict[str, Any]) -> dict[str, Any]:
        return await self._post("/anomaly/detect", fv)
