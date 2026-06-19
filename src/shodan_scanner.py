"""
Shodan Scanner — Fortinet SSL VPN vulnerability detection.

Queries Shodan for internet-exposed Fortinet SSL VPN instances and maps
findings against known CVEs for defensive triage and asset inventory.
"""

import httpx
from datetime import datetime
from typing import Optional

# ---------------------------------------------------------------------------
# Known Fortinet SSL VPN CVEs used for classification
# ---------------------------------------------------------------------------
FORTINET_CVES = {
    "CVE-2018-13379": {
        "cvss": 9.8,
        "summary": "Path traversal in FortiOS SSL VPN web portal allows "
                   "unauthenticated attacker to download system files.",
        "affected": ["FortiOS 6.0.0-6.0.4", "FortiOS 5.6.3-5.6.7",
                     "FortiOS 5.4.6-5.4.12"],
        "patch_version": "FortiOS 6.0.5 / 5.6.8 / 5.4.13",
    },
    "CVE-2022-42475": {
        "cvss": 9.3,
        "summary": "Heap-based buffer overflow in FortiOS SSL-VPN allows "
                   "remote unauthenticated attacker to execute arbitrary code.",
        "affected": ["FortiOS 7.2.0-7.2.2", "FortiOS 7.0.0-7.0.8",
                     "FortiOS 6.4.0-6.4.10", "FortiOS 6.2.x", "FortiOS 6.0.x"],
        "patch_version": "FortiOS 7.2.3 / 7.0.9 / 6.4.11",
    },
    "CVE-2023-27997": {
        "cvss": 9.8,
        "summary": "Heap-based buffer overflow in FortiOS and FortiProxy "
                   "SSL-VPN allows remote unauthenticated attacker to execute "
                   "arbitrary code or commands.",
        "affected": ["FortiOS 6.0.x", "FortiOS 6.2.x", "FortiOS 6.4.0-6.4.12",
                     "FortiOS 7.0.0-7.0.9", "FortiOS 7.2.0-7.2.4"],
        "patch_version": "FortiOS 6.4.13 / 7.0.10 / 7.2.5",
    },
    "CVE-2024-21762": {
        "cvss": 9.8,
        "summary": "Out-of-bounds write in FortiOS allows remote unauthenticated "
                   "attacker to execute arbitrary code via crafted HTTP requests.",
        "affected": ["FortiOS 6.0.x", "FortiOS 6.2.x", "FortiOS 6.4.x",
                     "FortiOS 7.0.0-7.0.13", "FortiOS 7.2.0-7.2.6",
                     "FortiOS 7.4.0-7.4.2"],
        "patch_version": "FortiOS 7.4.3 / 7.2.7 / 7.0.14",
    },
}

# Shodan search queries that surface Fortinet SSL VPN instances
SHODAN_QUERIES = [
    'ssl.cert.subject.cn:"FortiGate"',
    'product:"Fortinet SSL VPN"',
    'http.title:"SSL-VPN" ssl:"Fortinet"',
]

# In-memory result store  {scan_id: scan_dict}
scans: dict[str, dict] = {}


def _build_shodan_url(query: str, api_key: str, page: int = 1) -> str:
    """Return Shodan search API URL."""
    import urllib.parse
    return (
        f"https://api.shodan.io/shodan/host/search"
        f"?key={api_key}&query={urllib.parse.quote(query)}&page={page}"
    )


def _classify_host(banner: dict) -> dict:
    """Extract version info and flag likely-vulnerable CVEs from a Shodan banner."""
    version_str = ""

    # Pull version clues from various banner fields
    for field in ("version", "info", "data", "http.server"):
        val = banner.get(field, "")
        if val:
            version_str += " " + str(val)

    ssl_info = banner.get("ssl", {})
    cert_subject = ssl_info.get("cert", {}).get("subject", {}) if ssl_info else {}
    cn = cert_subject.get("CN", "")

    likely_cves: list[str] = []
    version_lower = version_str.lower()

    # Heuristic: flag all critical CVEs for unversioned hosts; refined matching
    # would require banner-level version parsing per CVE's affected range.
    for cve_id, info in FORTINET_CVES.items():
        if info["cvss"] >= 9.0:
            likely_cves.append(cve_id)

    return {
        "ip": banner.get("ip_str", ""),
        "port": banner.get("port", 443),
        "org": banner.get("org", ""),
        "isp": banner.get("isp", ""),
        "country": banner.get("location", {}).get("country_name", ""),
        "city": banner.get("location", {}).get("city", ""),
        "hostnames": banner.get("hostnames", []),
        "ssl_cn": cn,
        "version_hint": version_str.strip(),
        "likely_cves": likely_cves,
        "highest_cvss": max(
            (FORTINET_CVES[c]["cvss"] for c in likely_cves), default=0.0
        ),
        "last_update": banner.get("timestamp", ""),
    }


async def run_scan(api_key: str, max_results: int = 100) -> dict:
    """
    Query Shodan for Fortinet SSL VPN hosts and return classified results.

    This is a defensive reconnaissance tool — results should be used to
    identify and remediate exposure in your own infrastructure.
    """
    scan_id = f"scan_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
    hosts: list[dict] = []
    errors: list[str] = []

    async with httpx.AsyncClient(timeout=30.0) as client:
        for query in SHODAN_QUERIES:
            if len(hosts) >= max_results:
                break
            try:
                url = _build_shodan_url(query, api_key)
                resp = await client.get(url)
                resp.raise_for_status()
                data = resp.json()
                for match in data.get("matches", []):
                    if len(hosts) >= max_results:
                        break
                    hosts.append(_classify_host(match))
            except httpx.HTTPStatusError as exc:
                errors.append(f"Shodan API error for query '{query}': {exc.response.status_code}")
            except Exception as exc:
                errors.append(f"Error querying '{query}': {str(exc)}")

    # Deduplicate by IP
    seen: set[str] = set()
    unique_hosts: list[dict] = []
    for h in hosts:
        if h["ip"] not in seen:
            seen.add(h["ip"])
            unique_hosts.append(h)

    critical = [h for h in unique_hosts if h["highest_cvss"] >= 9.0]

    result = {
        "scan_id": scan_id,
        "completed_at": datetime.utcnow().isoformat() + "Z",
        "queries_used": SHODAN_QUERIES,
        "total_hosts": len(unique_hosts),
        "critical_count": len(critical),
        "hosts": unique_hosts,
        "cve_reference": FORTINET_CVES,
        "errors": errors,
    }
    scans[scan_id] = result
    return result


def get_scan(scan_id: str) -> Optional[dict]:
    return scans.get(scan_id)


def list_scans() -> list[dict]:
    return [
        {
            "scan_id": s["scan_id"],
            "completed_at": s["completed_at"],
            "total_hosts": s["total_hosts"],
            "critical_count": s["critical_count"],
            "errors": s["errors"],
        }
        for s in scans.values()
    ]


def get_cve_info() -> dict:
    return FORTINET_CVES
