from prometheus_client import Counter, Gauge

SITES_CHECKED_TOTAL = Counter(
    "sites_checked_total",
    "HTTP checks performed by checker",
    ["result"],
)

SITE_UP = Gauge(
    "site_up",
    "Last known availability (1=up,0=down)",
    ["site_id", "url"],
)
