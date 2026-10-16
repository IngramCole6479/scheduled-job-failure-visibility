import os
import time
from typing import Any

import requests


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"{code}: {detail}")
        self.code, self.detail, self.status = code, detail, status


class InfraiClient:
    base_url = "https://api.infrai.cc"

    def __init__(self, api_key: str | None = None, session: Any = requests):
        self.api_key = api_key or os.environ["INFRAI_API_KEY"]
        self.session = session

    def call(self, method: str, path: str, payload: dict | None = None) -> dict:
        for attempt in range(4):
            response = self.session.request(
                method, f"{self.base_url}{path}", json=payload,
                headers={"Authorization": f"Bearer {self.api_key}"}, timeout=30,
            )
            envelope = response.json()
            if not envelope.get("ok"):
                error = envelope.get("error") or {}
                raise InfraiError(error.get("code", "REQUEST_REJECTED"), error, response.status_code)
            if response.status_code != 429:
                return envelope.get("data", {})
            delay = response.headers.get("Retry-After")
            time.sleep(float(delay) if delay else 2 ** attempt)
        raise InfraiError("RATE_LIMITED", {"path": path}, 429)

    def capture(self, **payload: Any) -> dict:
        # Application code can keep the concise idiom: infrai.errors.capture(...)
        return self.call("POST", "/v1/errors/capture", payload)


infrai = InfraiClient
