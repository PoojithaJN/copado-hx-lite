import os
from dataclasses import dataclass
from typing import Any

import requests
from dotenv import load_dotenv


load_dotenv()


@dataclass
class CopadoCRTClient:
    """API-ready Copado Robotic Testing client with demo-mode behavior."""

    base_url: str = os.getenv("COPADO_CRT_BASE_URL", "")
    token: str = os.getenv("COPADO_CRT_TOKEN", "")
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
            return {"mode": "demo", "status": "skipped", "reason": "Missing Copado CRT credentials"}

        url = f"{self.base_url.rstrip('/')}/{path.lstrip('/')}"
        response = requests.request(method, url, headers=self._headers(), timeout=self.timeout, **kwargs)
        response.raise_for_status()
        if not response.content:
            return {}
        return response.json()

    def list_jobs(self) -> dict[str, Any]:
        return self._request("GET", "/jobs")

    def run_job(self, job_id: str) -> dict[str, Any]:
        return self._request("POST", f"/jobs/{job_id}/runs")

    def get_results(self, execution_id: str) -> dict[str, Any]:
        return self._request("GET", f"/executions/{execution_id}/results")

