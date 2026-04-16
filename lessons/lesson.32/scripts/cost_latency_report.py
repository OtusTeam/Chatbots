from statistics import mean


def p95(values: list[float]) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    idx = int(0.95 * (len(ordered) - 1))
    return ordered[idx]


def build_report(latencies_ms: list[float], daily_costs_usd: list[float]) -> dict:
    return {
        "latency_avg_ms": round(mean(latencies_ms), 2) if latencies_ms else 0.0,
        "latency_p95_ms": round(p95(latencies_ms), 2),
        "cost_daily_avg_usd": round(mean(daily_costs_usd), 2) if daily_costs_usd else 0.0,
        "cost_7d_total_usd": round(sum(daily_costs_usd), 2),
    }


if __name__ == "__main__":
    latencies = [190, 240, 310, 280, 560, 330, 290, 410, 220, 260]
    costs = [13.5, 14.1, 14.8, 15.2, 14.0, 13.9, 14.4]
    print(build_report(latencies, costs))
