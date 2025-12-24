#!/usr/bin/env python3
"""
Daily GA4 email report -> Resend.

Requires:
- GA_PROPERTY_ID (numeric GA4 property id)
- GOOGLE_APPLICATION_CREDENTIALS (service account JSON path) OR ADC
- RESEND_API_KEY

Optional:
- DAILY_ANALYTICS_TO (default: randy@salrs.nert)
- DAILY_ANALYTICS_FROM (default: FROM_EMAIL, else Dreamweaving Reports <reports@salars.net>)
- FROM_EMAIL (common across salarsu apps; used as sender fallback)
- DAILY_ANALYTICS_TZ (default: America/Denver)
- DAILY_ANALYTICS_SITE_NAME (default: salars.net)
"""

from __future__ import annotations

import argparse
import os
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from zoneinfo import ZoneInfo


class ConfigError(RuntimeError):
    pass


@dataclass(frozen=True)
class ReportConfig:
    ga_property_id: str
    google_credentials_path: Optional[str]
    resend_api_key: str
    sender: str
    recipient: str
    timezone: str
    site_name: str

    @classmethod
    def from_env(cls, *, strict: bool = True) -> "ReportConfig":
        ga_property_id = os.getenv("GA_PROPERTY_ID", "").strip()
        resend_api_key = os.getenv("RESEND_API_KEY", "").strip()

        recipient = os.getenv("DAILY_ANALYTICS_TO", "randy@salrs.nert").strip()
        sender = os.getenv("DAILY_ANALYTICS_FROM", "").strip()
        if not sender:
            sender = os.getenv("FROM_EMAIL", "").strip()
        if not sender:
            sender = "Dreamweaving Reports <reports@salars.net>"
        timezone = os.getenv("DAILY_ANALYTICS_TZ", "America/Denver").strip()
        site_name = os.getenv("DAILY_ANALYTICS_SITE_NAME", "salars.net").strip()

        if strict:
            if not resend_api_key:
                raise ConfigError("Missing RESEND_API_KEY.")
            if not recipient:
                raise ConfigError("Missing DAILY_ANALYTICS_TO.")
            if not timezone:
                raise ConfigError("Missing DAILY_ANALYTICS_TZ.")
            if not site_name:
                raise ConfigError("Missing DAILY_ANALYTICS_SITE_NAME.")

        return cls(
            ga_property_id=ga_property_id,
            google_credentials_path=os.getenv("GOOGLE_APPLICATION_CREDENTIALS"),
            resend_api_key=resend_api_key,
            sender=sender,
            recipient=recipient,
            timezone=timezone,
            site_name=site_name,
        )


def _pct_change(current: float, previous: float) -> Optional[float]:
    if previous == 0:
        return None
    return (current - previous) / previous * 100.0


def _fmt_int(value: Optional[float]) -> str:
    if value is None:
        return "—"
    return f"{int(round(value)):,}"


def _fmt_float(value: Optional[float], digits: int = 1) -> str:
    if value is None:
        return "—"
    return f"{value:.{digits}f}"


def _fmt_pct(value: Optional[float], digits: int = 1) -> str:
    if value is None:
        return "—"
    return f"{value:.{digits}f}%"


def _fmt_delta(delta: Optional[float], as_percent: bool = False) -> str:
    if delta is None:
        return "—"
    if as_percent:
        sign = "+" if delta > 0 else ""
        return f"{sign}{_fmt_pct(delta, digits=1)}"
    sign = "+" if delta > 0 else ""
    return f"{sign}{_fmt_int(delta)}"


def _to_date_strings(d: date) -> str:
    return d.strftime("%Y-%m-%d")


def _get_ga4_client(credentials_path: Optional[str]):
    from google.analytics.data_v1beta import BetaAnalyticsDataClient

    if credentials_path:
        return BetaAnalyticsDataClient.from_service_account_file(credentials_path)
    return BetaAnalyticsDataClient()


def _run_report(
    *,
    client: Any,
    property_id: str,
    date_ranges: Sequence[Tuple[str, str]],
    dimensions: Sequence[str],
    metrics: Sequence[str],
    dimension_filter: Optional[Any] = None,
    order_bys: Optional[Sequence[Tuple[str, bool]]] = None,  # (field_name, desc)
    limit: int = 0,
):
    from google.analytics.data_v1beta.types import (
        DateRange,
        Dimension,
        Metric,
        OrderBy,
        RunReportRequest,
    )

    req = RunReportRequest(
        property=f"properties/{property_id}",
        date_ranges=[DateRange(start_date=s, end_date=e) for (s, e) in date_ranges],
        dimensions=[Dimension(name=d) for d in dimensions],
        metrics=[Metric(name=m) for m in metrics],
        dimension_filter=dimension_filter,
        limit=limit if limit > 0 else None,
        order_bys=[
            OrderBy(
                desc=desc,
                metric=OrderBy.MetricOrderBy(metric_name=field),
            )
            for (field, desc) in (order_bys or [])
        ]
        if order_bys
        else None,
    )
    return client.run_report(req)


def _ga4_filter_in_list(field_name: str, values: Sequence[str]):
    from google.analytics.data_v1beta.types import Filter, FilterExpression

    return FilterExpression(
        filter=Filter(
            field_name=field_name,
            in_list_filter=Filter.InListFilter(values=list(values), case_sensitive=True),
        )
    )


def _extract_row_metrics(row: Any, num_metrics: int, num_date_ranges: int) -> List[List[float]]:
    """
    Returns values[date_range_idx][metric_idx] as floats.
    """
    values: List[List[float]] = []
    idx = 0
    for _ in range(num_date_ranges):
        dr: List[float] = []
        for _ in range(num_metrics):
            v = row.metric_values[idx].value
            try:
                dr.append(float(v))
            except Exception:
                dr.append(0.0)
            idx += 1
        values.append(dr)
    return values


def _report_overview(client: Any, cfg: ReportConfig, y: date) -> Dict[str, Any]:
    # date ranges: yesterday vs day before, and last 7 vs previous 7
    day_before = y - timedelta(days=1)
    last7_start = y - timedelta(days=6)
    prev7_end = y - timedelta(days=7)
    prev7_start = y - timedelta(days=13)

    date_ranges = [
        (_to_date_strings(y), _to_date_strings(y)),
        (_to_date_strings(day_before), _to_date_strings(day_before)),
        (_to_date_strings(last7_start), _to_date_strings(y)),
        (_to_date_strings(prev7_start), _to_date_strings(prev7_end)),
    ]

    metric_names = [
        "totalUsers",
        "sessions",
        "screenPageViews",
        "engagedSessions",
        "engagementRate",
        "averageSessionDuration",
    ]

    response = _run_report(
        client=client,
        property_id=cfg.ga_property_id,
        date_ranges=date_ranges,
        dimensions=[],
        metrics=metric_names,
        limit=1,
    )

    row = response.rows[0] if response.rows else None
    if not row:
        return {"metrics": {}, "notes": ["No rows returned for overview."]}

    values = _extract_row_metrics(row, num_metrics=len(metric_names), num_date_ranges=len(date_ranges))
    by_range = {
        "yesterday": dict(zip(metric_names, values[0])),
        "day_before": dict(zip(metric_names, values[1])),
        "last7": dict(zip(metric_names, values[2])),
        "prev7": dict(zip(metric_names, values[3])),
    }

    def delta(m: str, a: str, b: str) -> Optional[float]:
        return by_range[a].get(m, 0.0) - by_range[b].get(m, 0.0)

    def pct(m: str, a: str, b: str) -> Optional[float]:
        return _pct_change(by_range[a].get(m, 0.0), by_range[b].get(m, 0.0))

    return {
        "metrics": by_range,
        "dod": {m: pct(m, "yesterday", "day_before") for m in metric_names},
        "wow": {m: pct(m, "last7", "prev7") for m in metric_names},
        "ranges": {
            "yesterday": _to_date_strings(y),
            "day_before": _to_date_strings(day_before),
            "last7": f"{_to_date_strings(last7_start)} → {_to_date_strings(y)}",
            "prev7": f"{_to_date_strings(prev7_start)} → {_to_date_strings(prev7_end)}",
        },
    }


def _report_acquisition(client: Any, cfg: ReportConfig, y: date, limit: int = 8) -> Dict[str, Any]:
    day_before = y - timedelta(days=1)
    date_ranges = [
        (_to_date_strings(y), _to_date_strings(y)),
        (_to_date_strings(day_before), _to_date_strings(day_before)),
    ]

    metrics = ["sessions", "totalUsers"]
    dims = ["sessionSourceMedium"]

    response = _run_report(
        client=client,
        property_id=cfg.ga_property_id,
        date_ranges=date_ranges,
        dimensions=dims,
        metrics=metrics,
        order_bys=[("sessions", True)],
        limit=limit,
    )

    rows = []
    for row in response.rows or []:
        source = row.dimension_values[0].value or "(not set)"
        vals = _extract_row_metrics(row, num_metrics=len(metrics), num_date_ranges=len(date_ranges))
        y_sessions, y_users = vals[0]
        d_sessions, d_users = vals[1]
        rows.append(
            {
                "source": source,
                "sessions": y_sessions,
                "users": y_users,
                "sessions_dod_pct": _pct_change(y_sessions, d_sessions),
                "users_dod_pct": _pct_change(y_users, d_users),
            }
        )

    return {"rows": rows}


def _report_top_pages(client: Any, cfg: ReportConfig, y: date, limit: int = 8) -> Dict[str, Any]:
    date_ranges = [(_to_date_strings(y), _to_date_strings(y))]
    metrics = ["screenPageViews", "totalUsers"]
    dims = ["pagePath"]

    response = _run_report(
        client=client,
        property_id=cfg.ga_property_id,
        date_ranges=date_ranges,
        dimensions=dims,
        metrics=metrics,
        order_bys=[("screenPageViews", True)],
        limit=limit,
    )

    rows = []
    for row in response.rows or []:
        path = row.dimension_values[0].value or "/"
        vals = _extract_row_metrics(row, num_metrics=len(metrics), num_date_ranges=1)[0]
        rows.append({"path": path, "views": vals[0], "users": vals[1]})

    return {"rows": rows}


def _report_events(client: Any, cfg: ReportConfig, y: date) -> Dict[str, Any]:
    day_before = y - timedelta(days=1)
    last7_start = y - timedelta(days=6)
    prev7_end = y - timedelta(days=7)
    prev7_start = y - timedelta(days=13)

    date_ranges = [
        (_to_date_strings(y), _to_date_strings(y)),
        (_to_date_strings(day_before), _to_date_strings(day_before)),
        (_to_date_strings(last7_start), _to_date_strings(y)),
        (_to_date_strings(prev7_start), _to_date_strings(prev7_end)),
    ]

    key_events = [
        "donation_cta_click",
        "paypal_opened",
        "donation_success",
        "donation_abandon",
        "video_start",
        "video_complete",
        "share_click",
    ]

    metrics = ["eventCount", "eventValue"]
    dims = ["eventName"]

    response = _run_report(
        client=client,
        property_id=cfg.ga_property_id,
        date_ranges=date_ranges,
        dimensions=dims,
        metrics=metrics,
        dimension_filter=_ga4_filter_in_list("eventName", key_events),
        order_bys=[("eventCount", True)],
        limit=len(key_events),
    )

    by_event: Dict[str, Dict[str, float]] = {}
    for row in response.rows or []:
        name = row.dimension_values[0].value
        vals = _extract_row_metrics(row, num_metrics=len(metrics), num_date_ranges=len(date_ranges))
        by_event[name] = {
            "y_eventCount": vals[0][0],
            "d_eventCount": vals[1][0],
            "last7_eventCount": vals[2][0],
            "prev7_eventCount": vals[3][0],
            "y_eventValue": vals[0][1],
            "d_eventValue": vals[1][1],
            "last7_eventValue": vals[2][1],
            "prev7_eventValue": vals[3][1],
        }

    def get_count(event_name: str, key: str) -> float:
        return float(by_event.get(event_name, {}).get(key, 0.0))

    funnel = {
        "donation_cta_click": get_count("donation_cta_click", "y_eventCount"),
        "paypal_opened": get_count("paypal_opened", "y_eventCount"),
        "donation_success": get_count("donation_success", "y_eventCount"),
        "donation_abandon": get_count("donation_abandon", "y_eventCount"),
        "donation_value": get_count("donation_success", "y_eventValue"),
        "paypal_to_success_rate": (
            (get_count("donation_success", "y_eventCount") / get_count("paypal_opened", "y_eventCount"))
            if get_count("paypal_opened", "y_eventCount") > 0
            else None
        ),
        "cta_to_paypal_rate": (
            (get_count("paypal_opened", "y_eventCount") / get_count("donation_cta_click", "y_eventCount"))
            if get_count("donation_cta_click", "y_eventCount") > 0
            else None
        ),
    }

    return {"events": by_event, "funnel": funnel}


def _render_html(
    *,
    cfg: ReportConfig,
    report_date: date,
    generated_at: datetime,
    overview: Dict[str, Any],
    acquisition: Dict[str, Any],
    events: Dict[str, Any],
    top_pages: Dict[str, Any],
    warnings: Sequence[str],
) -> str:
    ranges = overview.get("ranges", {})
    y_metrics = overview.get("metrics", {}).get("yesterday", {})
    dod = overview.get("dod", {})
    wow = overview.get("wow", {})

    def metric_row(label: str, key: str, fmt: str = "int") -> str:
        val = y_metrics.get(key)
        if fmt == "pct":
            val_str = _fmt_pct((val or 0.0) * 100.0, digits=1)
        elif fmt == "sec":
            val_str = _fmt_float(val or 0.0, digits=0) + "s"
        else:
            val_str = _fmt_int(val)

        dod_str = _fmt_pct(dod.get(key), digits=1) if dod.get(key) is not None else "—"
        wow_str = _fmt_pct(wow.get(key), digits=1) if wow.get(key) is not None else "—"
        return f"""
          <tr>
            <td style="padding:6px 10px;border-bottom:1px solid #eee;">{label}</td>
            <td style="padding:6px 10px;border-bottom:1px solid #eee;text-align:right;font-variant-numeric:tabular-nums;">{val_str}</td>
            <td style="padding:6px 10px;border-bottom:1px solid #eee;text-align:right;font-variant-numeric:tabular-nums;">{dod_str}</td>
            <td style="padding:6px 10px;border-bottom:1px solid #eee;text-align:right;font-variant-numeric:tabular-nums;">{wow_str}</td>
          </tr>
        """

    acq_rows_html = ""
    for r in acquisition.get("rows", []):
        acq_rows_html += f"""
          <tr>
            <td style="padding:6px 10px;border-bottom:1px solid #eee;">{r["source"]}</td>
            <td style="padding:6px 10px;border-bottom:1px solid #eee;text-align:right;font-variant-numeric:tabular-nums;">{_fmt_int(r["sessions"])}</td>
            <td style="padding:6px 10px;border-bottom:1px solid #eee;text-align:right;font-variant-numeric:tabular-nums;">{_fmt_pct(r["sessions_dod_pct"], digits=1)}</td>
            <td style="padding:6px 10px;border-bottom:1px solid #eee;text-align:right;font-variant-numeric:tabular-nums;">{_fmt_int(r["users"])}</td>
          </tr>
        """
    if not acq_rows_html:
        acq_rows_html = """
          <tr><td colspan="4" style="padding:10px;color:#666;">No data.</td></tr>
        """

    pages_rows_html = ""
    for r in top_pages.get("rows", []):
        pages_rows_html += f"""
          <tr>
            <td style="padding:6px 10px;border-bottom:1px solid #eee;">{r["path"]}</td>
            <td style="padding:6px 10px;border-bottom:1px solid #eee;text-align:right;font-variant-numeric:tabular-nums;">{_fmt_int(r["views"])}</td>
            <td style="padding:6px 10px;border-bottom:1px solid #eee;text-align:right;font-variant-numeric:tabular-nums;">{_fmt_int(r["users"])}</td>
          </tr>
        """
    if not pages_rows_html:
        pages_rows_html = """
          <tr><td colspan="3" style="padding:10px;color:#666;">No data.</td></tr>
        """

    funnel = events.get("funnel", {})
    funnel_html = f"""
      <table style="width:100%;border-collapse:collapse;border:1px solid #eee;">
        <thead>
          <tr style="background:#fafafa;">
            <th style="padding:8px 10px;text-align:left;border-bottom:1px solid #eee;">Funnel (yesterday)</th>
            <th style="padding:8px 10px;text-align:right;border-bottom:1px solid #eee;">Count</th>
          </tr>
        </thead>
        <tbody>
          <tr><td style="padding:6px 10px;border-bottom:1px solid #eee;">CTA clicks</td><td style="padding:6px 10px;border-bottom:1px solid #eee;text-align:right;font-variant-numeric:tabular-nums;">{_fmt_int(funnel.get("donation_cta_click"))}</td></tr>
          <tr><td style="padding:6px 10px;border-bottom:1px solid #eee;">PayPal opened</td><td style="padding:6px 10px;border-bottom:1px solid #eee;text-align:right;font-variant-numeric:tabular-nums;">{_fmt_int(funnel.get("paypal_opened"))}</td></tr>
          <tr><td style="padding:6px 10px;border-bottom:1px solid #eee;">Donation success</td><td style="padding:6px 10px;border-bottom:1px solid #eee;text-align:right;font-variant-numeric:tabular-nums;">{_fmt_int(funnel.get("donation_success"))}</td></tr>
          <tr><td style="padding:6px 10px;border-bottom:1px solid #eee;">Donation abandon</td><td style="padding:6px 10px;border-bottom:1px solid #eee;text-align:right;font-variant-numeric:tabular-nums;">{_fmt_int(funnel.get("donation_abandon"))}</td></tr>
          <tr><td style="padding:6px 10px;border-bottom:1px solid #eee;">Donation value (sum)</td><td style="padding:6px 10px;border-bottom:1px solid #eee;text-align:right;font-variant-numeric:tabular-nums;">{_fmt_float(funnel.get("donation_value"), digits=2)}</td></tr>
          <tr><td style="padding:6px 10px;border-bottom:1px solid #eee;">CTA → PayPal</td><td style="padding:6px 10px;border-bottom:1px solid #eee;text-align:right;font-variant-numeric:tabular-nums;">{_fmt_pct((funnel.get("cta_to_paypal_rate") or 0.0) * 100.0, digits=1) if funnel.get("cta_to_paypal_rate") is not None else "—"}</td></tr>
          <tr><td style="padding:6px 10px;">PayPal → Success</td><td style="padding:6px 10px;text-align:right;font-variant-numeric:tabular-nums;">{_fmt_pct((funnel.get("paypal_to_success_rate") or 0.0) * 100.0, digits=1) if funnel.get("paypal_to_success_rate") is not None else "—"}</td></tr>
        </tbody>
      </table>
    """

    warnings_html = ""
    if warnings:
        warnings_html = "<ul>" + "".join(f"<li>{w}</li>" for w in warnings) + "</ul>"

    return f"""<!doctype html>
<html>
  <body style="margin:0;padding:0;background:#ffffff;color:#111;font-family:ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,Helvetica,Arial;">
    <div style="max-width:720px;margin:0 auto;padding:18px 16px;">
      <div style="margin-bottom:14px;">
        <div style="font-size:18px;font-weight:700;">Daily Analytics — {cfg.site_name}</div>
        <div style="color:#555;font-size:12px;margin-top:2px;">
          Report date: {ranges.get("yesterday", _to_date_strings(report_date))} • Generated: {generated_at.strftime("%Y-%m-%d %H:%M %Z")}
        </div>
      </div>

      <h2 style="font-size:14px;margin:18px 0 8px 0;">1) Overview (DoD and WoW)</h2>
      <table style="width:100%;border-collapse:collapse;border:1px solid #eee;">
        <thead>
          <tr style="background:#fafafa;">
            <th style="padding:8px 10px;text-align:left;border-bottom:1px solid #eee;">Metric</th>
            <th style="padding:8px 10px;text-align:right;border-bottom:1px solid #eee;">Yesterday</th>
            <th style="padding:8px 10px;text-align:right;border-bottom:1px solid #eee;">DoD</th>
            <th style="padding:8px 10px;text-align:right;border-bottom:1px solid #eee;">WoW (7d)</th>
          </tr>
        </thead>
        <tbody>
          {metric_row("Users", "totalUsers")}
          {metric_row("Sessions", "sessions")}
          {metric_row("Pageviews", "screenPageViews")}
          {metric_row("Engaged sessions", "engagedSessions")}
          {metric_row("Engagement rate", "engagementRate", fmt="pct")}
          {metric_row("Avg session duration", "averageSessionDuration", fmt="sec")}
        </tbody>
      </table>

      <h2 style="font-size:14px;margin:18px 0 8px 0;">2) Acquisition (top sources)</h2>
      <table style="width:100%;border-collapse:collapse;border:1px solid #eee;">
        <thead>
          <tr style="background:#fafafa;">
            <th style="padding:8px 10px;text-align:left;border-bottom:1px solid #eee;">Source / medium</th>
            <th style="padding:8px 10px;text-align:right;border-bottom:1px solid #eee;">Sessions</th>
            <th style="padding:8px 10px;text-align:right;border-bottom:1px solid #eee;">DoD</th>
            <th style="padding:8px 10px;text-align:right;border-bottom:1px solid #eee;">Users</th>
          </tr>
        </thead>
        <tbody>
          {acq_rows_html}
        </tbody>
      </table>

      <h2 style="font-size:14px;margin:18px 0 8px 0;">3) Conversions (donations)</h2>
      {funnel_html}

      <h2 style="font-size:14px;margin:18px 0 8px 0;">4) Top pages</h2>
      <table style="width:100%;border-collapse:collapse;border:1px solid #eee;">
        <thead>
          <tr style="background:#fafafa;">
            <th style="padding:8px 10px;text-align:left;border-bottom:1px solid #eee;">Path</th>
            <th style="padding:8px 10px;text-align:right;border-bottom:1px solid #eee;">Views</th>
            <th style="padding:8px 10px;text-align:right;border-bottom:1px solid #eee;">Users</th>
          </tr>
        </thead>
        <tbody>
          {pages_rows_html}
        </tbody>
      </table>

      {f'<h2 style=\"font-size:14px;margin:18px 0 8px 0;\">Notes</h2>{warnings_html}' if warnings_html else ''}

      <div style="margin-top:16px;color:#666;font-size:11px;line-height:1.4;">
        Tips: Large day-to-day swings are normal at low volume; look at WoW (7d) for trend.
      </div>
    </div>
  </body>
</html>
"""


def _render_text(
    *,
    cfg: ReportConfig,
    report_date: date,
    generated_at: datetime,
    overview: Dict[str, Any],
    acquisition: Dict[str, Any],
    events: Dict[str, Any],
    top_pages: Dict[str, Any],
    warnings: Sequence[str],
) -> str:
    ranges = overview.get("ranges", {})
    y_metrics = overview.get("metrics", {}).get("yesterday", {})
    dod = overview.get("dod", {})
    wow = overview.get("wow", {})

    def line(label: str, key: str, fmt: str = "int") -> str:
        val = y_metrics.get(key)
        if fmt == "pct":
            val_str = _fmt_pct((val or 0.0) * 100.0, digits=1)
        elif fmt == "sec":
            val_str = _fmt_float(val or 0.0, digits=0) + "s"
        else:
            val_str = _fmt_int(val)
        return f"- {label}: {val_str} (DoD {_fmt_pct(dod.get(key), 1)}, WoW {_fmt_pct(wow.get(key), 1)})"

    funnel = events.get("funnel", {})

    lines = [
        f"Daily Analytics — {cfg.site_name}",
        f"Report date: {ranges.get('yesterday', _to_date_strings(report_date))} • Generated: {generated_at.strftime('%Y-%m-%d %H:%M %Z')}",
        "",
        "1) Overview",
        line("Users", "totalUsers"),
        line("Sessions", "sessions"),
        line("Pageviews", "screenPageViews"),
        line("Engaged sessions", "engagedSessions"),
        line("Engagement rate", "engagementRate", fmt="pct"),
        line("Avg session duration", "averageSessionDuration", fmt="sec"),
        "",
        "2) Acquisition (top sources by sessions)",
    ]

    for r in acquisition.get("rows", []):
        lines.append(
            f"- {r['source']}: {_fmt_int(r['sessions'])} sessions (DoD {_fmt_pct(r['sessions_dod_pct'], 1)}), {_fmt_int(r['users'])} users"
        )

    lines += [
        "",
        "3) Conversions (yesterday)",
        f"- CTA clicks: {_fmt_int(funnel.get('donation_cta_click'))}",
        f"- PayPal opened: {_fmt_int(funnel.get('paypal_opened'))}",
        f"- Donation success: {_fmt_int(funnel.get('donation_success'))}",
        f"- Donation abandon: {_fmt_int(funnel.get('donation_abandon'))}",
        f"- Donation value (sum): {_fmt_float(funnel.get('donation_value'), 2)}",
        f"- CTA→PayPal: {_fmt_pct((funnel.get('cta_to_paypal_rate') or 0.0) * 100.0, 1) if funnel.get('cta_to_paypal_rate') is not None else '—'}",
        f"- PayPal→Success: {_fmt_pct((funnel.get('paypal_to_success_rate') or 0.0) * 100.0, 1) if funnel.get('paypal_to_success_rate') is not None else '—'}",
        "",
        "4) Top pages (by views)",
    ]

    for r in top_pages.get("rows", []):
        lines.append(f"- {r['path']}: {_fmt_int(r['views'])} views, {_fmt_int(r['users'])} users")

    if warnings:
        lines += ["", "Notes"] + [f"- {w}" for w in warnings]

    return "\n".join(lines) + "\n"


def _send_resend(*, api_key: str, sender: str, recipient: str, subject: str, html: str, text: str) -> Any:
    import resend

    resend.api_key = api_key
    return resend.Emails.send(
        {
            "from": sender,
            "to": [recipient],
            "subject": subject,
            "html": html,
            "text": text,
        }
    )


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Send daily GA4 analytics email via Resend.")
    parser.add_argument("--to", dest="to", default=None, help="Override recipient email.")
    parser.add_argument("--from", dest="from_addr", default=None, help="Override sender (must be verified in Resend).")
    parser.add_argument("--dry-run", action="store_true", help="Render output but do not send.")
    parser.add_argument(
        "--allow-missing-ga",
        action="store_true",
        help="Allow sending even if GA_PROPERTY_ID is missing (email will include warnings and empty metrics).",
    )
    args = parser.parse_args(argv)

    cfg = ReportConfig.from_env(strict=not args.dry_run)
    if args.to:
        cfg = ReportConfig(
            ga_property_id=cfg.ga_property_id,
            google_credentials_path=cfg.google_credentials_path,
            resend_api_key=cfg.resend_api_key,
            sender=cfg.sender,
            recipient=args.to,
            timezone=cfg.timezone,
            site_name=cfg.site_name,
        )
    if args.from_addr:
        cfg = ReportConfig(
            ga_property_id=cfg.ga_property_id,
            google_credentials_path=cfg.google_credentials_path,
            resend_api_key=cfg.resend_api_key,
            sender=args.from_addr,
            recipient=cfg.recipient,
            timezone=cfg.timezone,
            site_name=cfg.site_name,
        )

    tz = ZoneInfo(cfg.timezone)
    now = datetime.now(tz=tz)
    report_date = (now - timedelta(days=1)).date()

    warnings: List[str] = []
    if not args.dry_run and not args.allow_missing_ga and not cfg.ga_property_id:
        raise ConfigError("Missing GA_PROPERTY_ID (numeric GA4 property id).")

    client = None
    if not cfg.ga_property_id:
        warnings.append("GA_PROPERTY_ID not set; GA4 queries skipped.")
    else:
        try:
            client = _get_ga4_client(cfg.google_credentials_path)
        except Exception as exc:
            warnings.append(
                "Failed to initialize GA4 Data API client; ensure google-analytics-data is installed and "
                "GOOGLE_APPLICATION_CREDENTIALS points to a valid service account JSON (or ADC is configured)."
            )
            warnings.append(str(exc))

    overview: Dict[str, Any] = {}
    acquisition: Dict[str, Any] = {}
    events: Dict[str, Any] = {}
    top_pages: Dict[str, Any] = {}

    if client is not None:
        try:
            overview = _report_overview(client, cfg, report_date)
        except Exception as exc:
            warnings.append(f"Overview query failed: {exc}")
        try:
            acquisition = _report_acquisition(client, cfg, report_date)
        except Exception as exc:
            warnings.append(f"Acquisition query failed: {exc}")
        try:
            events = _report_events(client, cfg, report_date)
        except Exception as exc:
            warnings.append(f"Events/funnel query failed: {exc}")
        try:
            top_pages = _report_top_pages(client, cfg, report_date)
        except Exception as exc:
            warnings.append(f"Top pages query failed: {exc}")

    generated_at = now
    subject = f"Daily Analytics — {cfg.site_name} — {_to_date_strings(report_date)}"
    html = _render_html(
        cfg=cfg,
        report_date=report_date,
        generated_at=generated_at,
        overview=overview,
        acquisition=acquisition,
        events=events,
        top_pages=top_pages,
        warnings=warnings,
    )
    text = _render_text(
        cfg=cfg,
        report_date=report_date,
        generated_at=generated_at,
        overview=overview,
        acquisition=acquisition,
        events=events,
        top_pages=top_pages,
        warnings=warnings,
    )

    if args.dry_run:
        print(text)
        return 0

    if not cfg.resend_api_key:
        raise ConfigError("Missing RESEND_API_KEY.")

    result = _send_resend(
        api_key=cfg.resend_api_key,
        sender=cfg.sender,
        recipient=cfg.recipient,
        subject=subject,
        html=html,
        text=text,
    )
    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
