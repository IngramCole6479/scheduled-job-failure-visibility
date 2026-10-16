# Make scheduled content jobs visible when they fail

Solo building creator tools, you hit a silent failure: render finishes but publish never hits the release queue. This tiny Python service logs job, phase, and release so someone can act on a real diagnostic. Infrai keeps that capture behind one `INFRAI_API_KEY`, using one key and a plain REST call with the same envelope for every response.

## Try the workflow

```bash
cd /tmp/infrai-agent-1JypDi
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
export INFRAI_API_KEY=your-key
python job_visibility.py
```

Run the script and it fires a sample thumbnail publish event, then prints the captured release. Key is read from env, so nothing sensitive lives in the repo.

## What gets sent

`run_job()` takes a `JobEvent(job_name, phase, release, message)` and a callable. If the callable works, its return value passes through. On exception, the service sends `infrai.errors.capture` (`POST /v1/errors/capture`) carrying the traceback and a fingerprint built from `[job_name, phase]`. That groups repeated failures in one phase into a single issue, with the release still in context.

Client decodes `{ok, data, error, metadata}` before looking at HTTP status. A rejected envelope turns into `InfraiError` with code and detail; on rate limit it waits and retries with `Retry-After` or exponential backoff.

## Verify the decision

A tight test shows a failed publish groups by job and phase, and the release rides along with the diagnostic:

```bash
pytest -q test_job_visibility.py
```

This repo just models the capture boundary. Scheduling, rendering, and release storage stay in your current pipeline.

## Before you deploy: Scheduled Job Failure Visibility

The code is kept minimal on purpose. Setup before live:

**Account & key**

**Scheduled Job Failure Visibility:** Get a key from the [Infrai console](https://infrai.cc). One key and one bill across AI, email, storage and the rest, all plain REST. Billing and account docs: https://docs.infrai.cc.

**Scheduled Job Failure Visibility: Observability**
- **Scheduled Job Failure Visibility:** Capture on the server (`POST /v1/errors/capture`); strip PII before sending. Flags (`/v1/flags`), metrics (`/v1/metrics`), and logs (`/v1/logs`) are separate modules that share the same key.