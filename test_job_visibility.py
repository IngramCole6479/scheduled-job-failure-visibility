import pytest

from job_visibility import JobEvent, run_job


class StubClient:
    def __init__(self):
        self.payload = None

    def capture(self, **payload):
        self.payload = payload
        return {"event_id": "local-test"}


def test_failed_publish_is_grouped_by_job_and_phase():
    client = StubClient()
    event = JobEvent("thumbnail-render", "publish", "r17", "cdn manifest missing")

    with pytest.raises(RuntimeError):
        run_job(event, lambda: (_ for _ in ()).throw(RuntimeError("missing manifest")), client)

    assert client.payload["fingerprint"] == ["thumbnail-render", "publish"]
    assert client.payload["context"]["release"] == "r17"
