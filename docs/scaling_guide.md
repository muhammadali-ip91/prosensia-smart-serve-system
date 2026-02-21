# ⚡ ProSensia — 100k Realtime Scaling Guide

## Reality Check

Single-machine local mode (SQLite + 1 Uvicorn process) cannot handle 100,000 realtime users.

To approach 100k concurrent realtime connections, you need **horizontal architecture**.

## Required Architecture

- **Load Balancer** with sticky sessions (Nginx/ALB)
- **Multiple Backend Instances** (FastAPI + Socket.IO)
- **Shared Redis** as Socket.IO message bus
- **PostgreSQL (managed + pooled)**, not SQLite
- **Background workers** for non-critical jobs
- **Monitoring stack** (Prometheus/Grafana + centralized logs)

## Backend Changes Already Added

The backend now supports Redis-backed Socket.IO client manager:

- `SOCKETIO_USE_REDIS_MANAGER`
- `SOCKETIO_REDIS_CHANNEL`
- `SOCKETIO_PING_INTERVAL`
- `SOCKETIO_PING_TIMEOUT`
- `SOCKETIO_MAX_HTTP_BUFFER_SIZE`

When `SOCKETIO_USE_REDIS_MANAGER=true`, events are synchronized across backend instances.

## Production Env Example

```env
DEBUG=false
DATABASE_URL=postgresql://<user>:<pass>@<host>:5432/prosensia
REDIS_URL=redis://<redis-host>:6379/0

SOCKETIO_USE_REDIS_MANAGER=true
SOCKETIO_REDIS_CHANNEL=prosensia_socketio
SOCKETIO_PING_INTERVAL=25
SOCKETIO_PING_TIMEOUT=60
SOCKETIO_MAX_HTTP_BUFFER_SIZE=1000000

CORS_ORIGINS=https://app.example.com
```

## Capacity Ramp Plan (Recommended)

- Stage 1: 1k concurrent connections
- Stage 2: 5k concurrent connections
- Stage 3: 20k concurrent connections
- Stage 4: 50k concurrent connections
- Stage 5: 100k concurrent connections

At each stage, track:

- P95 API latency
- P95 websocket event delivery latency
- Error rate
- CPU/memory on app + Redis + DB
- DB connection pool saturation

## Practical Notes

- 100k realtime users usually needs **multiple app nodes** and tuned kernel/network settings.
- Use PostgreSQL connection pooling (PgBouncer) before higher stages.
- Keep websocket payloads minimal and avoid high-frequency global broadcasts.
- Separate critical API traffic from analytics/background tasks.
