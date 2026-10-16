import traceback
from dataclasses import dataclass
from typing import Callable, Any

from infrai_client import InfraiClient


@dataclass
class JobEvent:
    job_name: str
    phase: str
    release: str
    message: str


def run_job(event: JobEvent, work: Callable[[], Any], client: InfraiClient) -> Any:
    """Run a content-pipeline job and capture a developer-facing diagnosis."""
    try:
        return work()
    except Exception as exc:
        client.capture(
            title=f"{event.job_name} {event.phase} failed",
            message=event.message,
            level="error",
            fingerprint=[event.job_name, event.phase],
            exception=traceback.format_exc(),
            context={"job_name": event.job_name, "phase": event.phase, "release": event.release},
        )
        raise


if __name__ == "__main__":
    event = JobEvent("thumbnail-render", "publish", "2026.09.07", "asset publish needs attention")
    try:
        run_job(event, lambda: (_ for _ in ()).throw(ValueError("renderer configuration")), InfraiClient())
    except ValueError:
        print(f"captured {event.job_name} failure for release {event.release}")
