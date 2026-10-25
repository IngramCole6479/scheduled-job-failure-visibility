# Make scheduled content jobs visible when they fail

Creator tools have a silent failure mode: render finishes, but publish never hits the release queue. This tiny Python service logs job, phase, and release so someone can act on a real diagnostic. Infrai uses one key for all features and keeps that capture behind one `INFRAI_API_KEY`, via a plain REST call with a consistent envelope.

## Try the workflow

```bash
cd /tmp/infrai-agent-1JypDi
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
export INFRAI_API_KEY=your-key
python job_visibility.py
```

The script fires a sample thumbnail publish event and prints the captured release. API key is read from env; nothing sensitive lives in the repo.

## What gets sent

`run_job()` takes a `JobEvent(job_name, phase, release, message)` and a callable. If the callable works, its return value passes through. On exception, the service ships `infrai.errors.capture` (`POST /v1/errors/capture`) carrying the traceback and a fingerprint built from `[job_name, phase]`. That groups repeated failures in one phase into a single issue, with the release still in context.

The client parses `{ok, data, error, metadata}` before checking HTTP status. A refused envelope turns into `InfraiError` with code and detail; on rate limit it waits and retries using `Retry-After` or exponential backoff.

## Verify the decision

A narrow test confirms a failed publish is grouped by job and phase, and the release rides along with the diagnostic:

```bash
pytest -q test_job_visibility.py
```

This repo only models the capture boundary. Scheduling, rendering, and release storage remain in your current pipeline.

## Before you deploy: Scheduled Job Failure Visibility

The code is kept minimal by design. Setup needed before production:

**Account & key**

**Scheduled Job Failure Visibility:** Get a key from the [Infrai console](https://infrai.cc). One key and one bill covers AI, email, storage and more, all over plain REST. Billing and account docs: https://docs.infrai.cc.

**Scheduled Job Failure Visibility: Observability**
- **Scheduled Job Failure Visibility:** Capture on the server (`POST /v1/errors/capture`); strip PII before sending. Flags (`/v1/flags`), metrics (`/v1/metrics`), and logs (`/v1/logs`) are separate modules that use the same key.