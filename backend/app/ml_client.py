from typing import Any

import httpx


class MLClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    async def classify(self, feature_vector: dict[str, Any]) -> dict[str, Any]:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{self.base_url}/classify", json=feature_vector)
            response.raise_for_status()
            return response.json()

    async def cluster(
        self,
        vectors: list[dict[str, Any]],
        n_clusters: int = 4,
    ) -> dict[str, Any]:
        payload = {
            "vectors": vectors,
            "n_clusters": n_clusters,
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{self.base_url}/cluster", json=payload)
            response.raise_for_status()
            return response.json()

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
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{self.base_url}/suggest", json=payload)
            response.raise_for_status()
            return response.json()
