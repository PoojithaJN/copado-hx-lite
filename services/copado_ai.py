import os
from dataclasses import dataclass
from typing import Any

import requests
from dotenv import load_dotenv


load_dotenv()


@dataclass
class CopadoAIClient:
    """API-ready AI assistant client that returns deterministic demo output without credentials."""

    base_url: str = os.getenv("COPADO_AI_BASE_URL", "")
    token: str = os.getenv("COPADO_AI_TOKEN", "")
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

    def ask(self, agent: str, prompt: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        if self.demo_mode:
            return {
                "mode": "demo",
                "agent": agent,
                "answer": f"Demo {agent} agent received: {prompt}",
                "context": context or {},
            }

        payload = {"agent": agent, "prompt": prompt, "context": context or {}}
        url = f"{self.base_url.rstrip('/')}/agents/{agent}/ask"
        response = requests.post(url, headers=self._headers(), json=payload, timeout=self.timeout)
        response.raise_for_status()
        return response.json()

    def diagnose_deployment(self, job_id: str) -> dict[str, Any]:
        if self.demo_mode:
            return {
                "mode": "demo",
                "failed_job_id": job_id,
                "root_cause": "Validation rule expects Lead.Score__c before flow assignment.",
                "suggested_fix": "Add a null-safe default in the lead scoring flow.",
                "confidence_score": 0.87,
                "recommended_next_action": "Patch, recommit, and rerun UAT validation.",
            }

        return self.ask("diagnose", f"Diagnose deployment failure {job_id}", {"job_id": job_id})

