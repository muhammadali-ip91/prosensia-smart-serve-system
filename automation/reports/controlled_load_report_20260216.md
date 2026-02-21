# Controlled Load Test Report (PostgreSQL)

Date: 2026-02-16
Target: `http://127.0.0.1:8000`
DB: PostgreSQL (`prosensia_db`)
Tool: Locust 2.20.1 (headless)

## Test Profiles
- 1k users: `--users 1000 --spawn-rate 100 --run-time 30s`
- 5k users: `--users 5000 --spawn-rate 250 --run-time 40s`
- 10k users: `--users 10000 --spawn-rate 400 --run-time 45s`
- 50k users: `--users 50000 --spawn-rate 1200 --run-time 60s`

## Results (Aggregated)

| Users | Requests | Failures | Failure % | Median | Avg | Max | Req/s |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1k | 1265 | 1077 | 85.14% | 2100 ms | 3051 ms | 28989 ms | 43.47 |
| 5k | 7251 | 7202 | 99.32% | 2100 ms | 2255 ms | 39183 ms | 184.05 |
| 10k | 15783 | 15711 | 99.54% | 2200 ms | 2274 ms | 43976 ms | 348.48 |
| 50k | 33024 | 32836 | 99.43% | 27000 ms | 21382 ms | 61793 ms | 484.55 |

## Main Failure Patterns
- `ConnectionRefusedError [WinError 10061]` dominated at all scales (server saturation / accept queue collapse)
- Extra functional failures from workload mix:
  - `GET /orders/my-orders` returned 404 in some flows
  - `POST /orders` returned 400 in some flows

## Artifacts
- `automation/reports/locust_1k_stats.csv`
- `automation/reports/locust_5k_stats.csv`
- `automation/reports/locust_10k_stats.csv`
- `automation/reports/locust_50k_stats.csv`

## Conclusion
Current single-node local deployment is not capable of high-concurrency realtime traffic. Even at 1k virtual users, failure rate is already very high. 50k is not supportable in this topology.

## Next Infra Steps for Higher Scale
- Multiple backend instances behind load balancer
- Redis-backed Socket.IO manager (already integrated in code)
- PostgreSQL tuning + pooler (PgBouncer)
- Route-level test profile cleanup (`/orders/my-orders` mismatch)
- Distributed load generation (single machine should not generate 50k realistically)
