"""One-time local helper to (re)generate the static MongoDB seed data.

This script is NOT run inside Docker - run it locally whenever you want to
regenerate the sample dataset. Its output (the JSON file under
mongodb/init/data/) is committed to the repo and imported automatically by
mongodb/init/02-import-seed-data.sh when the mongodb container starts for the
first time.

Usage:
    python generate_seed_data.py
"""
import json
import pathlib
import random
from datetime import datetime, timedelta, timezone

random.seed(42)

DAYS = 30
# Latest 30 days, starting at midnight UTC
START_DATE = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=DAYS)
ENVIRONMENT = "staging"

# (endpoint, method, typical avg response time in ms)
ENDPOINTS = [
    ("/api/orders", "POST", 180),
    # ("/api/products", "GET", 90),
]

#HOSTS = ["app-server-01", "app-server-02", "db-server-01"]  # disabled for now


def iso(dt: datetime) -> dict:
    """MongoDB Extended JSON date, understood natively by mongoimport."""
    return {"$date": dt.strftime("%Y-%m-%dT%H:%M:%SZ")}


def generate_api_metrics() -> list[dict]:
    docs = []
    for day in range(DAYS):
        date = START_DATE + timedelta(days=day)
        # occasional "bad day" with elevated latency/error rate across all endpoints
        incident = random.random() < 0.12

        for endpoint, method, base_latency in ENDPOINTS:
            multiplier = random.uniform(1.5, 3.0) if incident else random.uniform(0.85, 1.25)
            avg = round(base_latency * multiplier, 1)
            p50 = round(avg * random.uniform(0.9, 1.0), 1)
            p90 = round(avg * random.uniform(1.4, 1.7), 1)
            p95 = round(avg * random.uniform(1.7, 2.1), 1)
            p99 = round(avg * random.uniform(2.2, 3.0), 1)
            min_ms = round(avg * random.uniform(0.3, 0.5), 1)
            max_ms = round(p99 * random.uniform(1.1, 1.6), 1)

            total_requests = random.randint(5000, 20000)
            error_rate = round(random.uniform(3.0, 8.0) if incident else random.uniform(0.1, 2.0), 2)
            nok_count = round(total_requests * error_rate / 100)
            ok_count = total_requests - nok_count
            throughput = round(total_requests / 86400, 3)

            docs.append({
                "date": iso(date),
                "meta": {"endpoint": endpoint, "method": method, "environment": ENVIRONMENT},
                "total_requests": total_requests,
                "ok_count": ok_count,
                "nok_count": nok_count,
                "error_rate_percent": error_rate,
                "avg_response_time_ms": avg,
                "min_response_time_ms": min_ms,
                "max_response_time_ms": max_ms,
                "p50_ms": p50,
                "p90_ms": p90,
                "p95_ms": p95,
                "p99_ms": p99,
                "throughput_rps": throughput,
            })
    return docs


def generate_infra_metrics() -> list[dict]:
    docs = []
    for day in range(DAYS):
        day_incident = random.random() < 0.12
        ts = START_DATE + timedelta(days=day)
        for host in ["app-server-01"]:
            is_db_host = host.startswith("db")
            base_cpu = 55 if is_db_host else 35
            base_ram = 65 if is_db_host else 45
            spike = day_incident and random.random() < 0.5

            cpu = round(min(99.0, base_cpu + random.uniform(-10, 10) + (30 if spike else 0)), 1)
            ram = round(min(98.0, base_ram + random.uniform(-8, 8) + (20 if spike else 0)), 1)
            ram_total = 16384 if is_db_host else 8192
            ram_used = round(ram_total * ram / 100)
            disk = round(random.uniform(40, 75), 1)
            net_in = round(random.uniform(5, 80), 2)
            net_out = round(random.uniform(5, 60), 2)

            docs.append({
                "timestamp": iso(ts),
                "meta": {"host": host},
                "cpu_usage_percent": cpu,
                "ram_usage_percent": ram,
                "ram_used_mb": ram_used,
                "ram_total_mb": ram_total,
                "disk_usage_percent": disk,
                "network_in_mbps": net_in,
                "network_out_mbps": net_out,
            })
    return docs


def main() -> None:
    out_dir = pathlib.Path(__file__).parent / "init" / "data"
    out_dir.mkdir(parents=True, exist_ok=True)

    api_docs = generate_api_metrics()
    # infra_docs = generate_infra_metrics()  # disabled for now

    (out_dir / "api_performance_metrics.json").write_text(json.dumps(api_docs, indent=2))
    # (out_dir / "infra_metrics.json").write_text(json.dumps(infra_docs, indent=2))

    print(f"Wrote {len(api_docs)} docs to {out_dir / 'api_performance_metrics.json'}")
    # print(f"Wrote {len(infra_docs)} docs to {out_dir / 'infra_metrics.json'}")


if __name__ == "__main__":
    main()
