from dataclasses import dataclass


@dataclass
class MetricInput:
    users_total: int
    requests_total: int
    errors_total: int
    avg_latency_ms: float
    infra_cost_usd: float
    model_cost_usd: float


def build_metrics(data: MetricInput) -> dict:
    error_rate = (data.errors_total / data.requests_total) if data.requests_total else 0.0
    cost_total = data.infra_cost_usd + data.model_cost_usd
    cost_per_request = cost_total / data.requests_total if data.requests_total else 0.0
    return {
        "users_total": data.users_total,
        "requests_total": data.requests_total,
        "error_rate_pct": round(error_rate * 100, 2),
        "avg_latency_ms": round(data.avg_latency_ms, 2),
        "cost_total_usd": round(cost_total, 2),
        "cost_per_request_usd": round(cost_per_request, 5),
    }


if __name__ == "__main__":
    sample = MetricInput(
        users_total=1250,
        requests_total=18400,
        errors_total=92,
        avg_latency_ms=310.4,
        infra_cost_usd=38.5,
        model_cost_usd=71.8,
    )
    print(build_metrics(sample))
