import os
from dataclasses import dataclass
from typing import Any

import requests
from dotenv import load_dotenv


load_dotenv()


@dataclass
class CopadoCICDClient:
    """API-ready Copado CI/CD client with a safe demo-mode fallback."""

    base_url: str = os.getenv("COPADO_CICD_BASE_URL", "")
    token: str = os.getenv("COPADO_CICD_TOKEN", "")
    timeout: int = int(os.getenv("COPADO_HTTP_TIMEOUT", "15"))

    @property
    def demo_mode(self) -> bool:
        return not (self.base_url and self.token)

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "User-Agent": "copado-hx-lite/1.0",
        }

    def _request(self, method: str, path: str, **kwargs: Any) -> dict[str, Any]:
        if self.demo_mode:
            return {"mode": "demo", "status": "skipped", "reason": "Missing Copado CI/CD credentials"}

        url = f"{self.base_url.rstrip('/')}/{path.lstrip('/')}"
        response = requests.request(method, url, headers=self._headers(), timeout=self.timeout, **kwargs)
        response.raise_for_status()
        if not response.content:
            return {}
        return response.json()

    def list_user_stories(self) -> dict[str, Any]:
        return self._request("GET", "/user-stories")

    def create_commit(self, story_id: str, message: str, metadata: list[str]) -> dict[str, Any]:
        payload = {"storyId": story_id, "message": message, "metadata": metadata}
        return self._request("POST", "/commits", json=payload)

    def validate_promotion(self, story_id: str, target_env: str) -> dict[str, Any]:
        payload = {"storyId": story_id, "targetEnvironment": target_env, "validateOnly": True}
        return self._request("POST", "/promotions/validate", json=payload)

