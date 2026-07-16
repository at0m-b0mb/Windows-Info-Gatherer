"""Export collected categories to JSON, plain text or a standalone HTML report."""

from __future__ import annotations

import datetime as _dt
import html
import json
import platform
from typing import List

from . import __app_name__, __version__
from .model import Category, Severity


def _now() -> str:
    return _dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _meta(demo: bool) -> dict:
    return {
        "tool": __app_name__,
        "version": __version__,
        "generated": _now(),
        "host": platform.node(),
        "platform": platform.platform(),
        "mode": "DEMO" if demo else "LIVE",
    }


# --------------------------------------------------------------------- JSON
def to_dict(categories: List[Category], demo: bool) -> dict:
    cats = []
    for c in categories:
        sections = []
        for s in c.sections:
            entry = {"title": s.title, "kind": s.kind, "note": s.note}
            if s.kind == "keyvalue":
                entry["data"] = {k: v for k, v in s.rows}
            elif s.kind == "table":
                entry["headers"] = s.headers
                entry["rows"] = s.table_rows
            elif s.kind == "findings":
                entry["findings"] = [
                    {"title": f.title, "severity": f.severity.value,
                     "detail": f.detail, "recommendation": f.recommendation}
                    for f in s.findings
                ]
            sections.append(entry)
        cats.append({"key": c.key, "name": c.name,
                     "subtitle": c.subtitle, "sections": sections})
    return {"meta": _meta(demo), "categories": cats}


def to_json(categories: List[Category], demo: bool) -> str:
    return json.dumps(to_dict(categories, demo), indent=2)


# --------------------------------------------------------------------- TXT
def to_text(categories: List[Category], demo: bool) -> str:
    m = _meta(demo)
    out = []
    bar = "=" * 68
    out.append(bar)
    out.append(f"  {m['tool']} v{m['version']}  --  {m['mode']} report")
    out.append(f"  Host: {m['host']}   Generated: {m['generated']}")
    out.append(bar)
    for c in categories:
        out.append("")
        out.append(f"### {c.name.upper()} -- {c.subtitle}")
        for s in c.sections:
            out.append("")
            out.append(f"  [{s.title}]")
            if s.kind == "keyvalue":
                width = max((len(k) for k, _ in s.rows), default=0)
                for k, v in s.rows:
                    out.append(f"    {k.ljust(width)} : {v}")
            elif s.kind == "table":
                out.append("    " + " | ".join(s.headers))
                for row in s.table_rows:
                    out.append("    " + " | ".join(row))
            elif s.kind == "findings":
                for f in s.findings:
                    out.append(f"    [{f.severity.value.upper()}] {f.title}")
                    out.append(f"        {f.detail}")
                    if f.recommendation:
                        out.append(f"        -> {f.recommendation}")
            if s.note:
                out.append(f"    ({s.note})")
    out.append("")
    return "\n".join(out)


# --------------------------------------------------------------------- HTML
_SEV_COLOR = {
    Severity.CRITICAL: "#ff4d5e",
    Severity.HIGH: "#ff8a3d",
    Severity.MEDIUM: "#ffd23d",
    Severity.LOW: "#4dc3ff",
    Severity.INFO: "#8b98a9",
    Severity.GOOD: "#28e0c8",
}
_GOOD = "#39d98a"
_ACCENT = "#28e0c8"
_HIGH = "#ff8a3d"
_MED = "#ffd23d"
_RISKY_PORTS = {"21", "23", "135", "137", "138", "139", "445",
                "1433", "3306", "3389", "5432", "5985", "5986"}


def _cell_color(section_title: str, header: str, value: str):
    """Highlight colour for a security-meaningful cell (mirrors the GUI)."""
    t, h, vl = (section_title or "").lower(), (header or "").lower(), \
        (value or "").strip().lower()
    if not vl:
        return None
    if "posture" in t:
        if "tamper" in h:
            return _GOOD if vl in ("on", "true", "enabled") else _MED
        if "firewall" in h:
            return _MED if "off" in vl else _GOOD
        if "bitlocker" in h:
            return _GOOD if vl in ("on", "enabled") else _HIGH
        if h == "rdp":
            return _MED if "enabled" in vl else _GOOD
        if h == "smbv1":
            return _HIGH if "enabled" in vl else _GOOD
        if vl in ("on", "enabled", "running", "true"):
            return _GOOD
        if vl in ("off", "disabled", "stopped", "not encrypted", "false"):
            return _MED
        return None
    if "local accounts" in t and h == "admin" and vl == "yes":
        return _HIGH
    if "listening ports" in t:
        if h == "state" and vl == "listening":
            return _ACCENT
        if h == "local address" and value.rsplit(":", 1)[-1] in _RISKY_PORTS:
            return _HIGH
    if t == "services" and h == "state" and vl == "running":
        return _GOOD
    if "wi-fi" in t and "key" in h and vl not in ("(open)",
                                                  "(not stored / no admin)"):
        return _ACCENT
    return None


def to_html(categories: List[Category], demo: bool) -> str:
    m = _meta(demo)
    e = html.escape

    def sev_badge(sev: Severity) -> str:
        return (f'<span class="sev" style="background:{_SEV_COLOR[sev]}22;'
                f'color:{_SEV_COLOR[sev]};border:1px solid {_SEV_COLOR[sev]}55">'
                f'{sev.value}</span>')

    body = []
    nav = []
    for c in categories:
        nav.append(f'<a href="#{c.key}">{e(c.name)}</a>')
        body.append(f'<section id="{c.key}"><h2>{e(c.name)}'
                    f'<small>{e(c.subtitle)}</small></h2>')
        for s in c.sections:
            body.append(f'<div class="card"><h3>{e(s.title)}</h3>')
            if s.kind == "keyvalue":
                body.append('<table class="kv">')
                for k, v in s.rows:
                    col = _cell_color(s.title, k, v)
                    style = f' style="color:{col};font-weight:600"' if col else ''
                    body.append(f'<tr><th>{e(k)}</th>'
                                f'<td{style}>{e(v)}</td></tr>')
                body.append('</table>')
            elif s.kind == "table":
                body.append('<div class="scroll"><table class="grid"><thead><tr>')
                for h in s.headers:
                    body.append(f'<th>{e(h)}</th>')
                body.append('</tr></thead><tbody>')
                for row in s.table_rows:
                    cells = []
                    for i, c in enumerate(row):
                        hd = s.headers[i] if i < len(s.headers) else ""
                        col = _cell_color(s.title, hd, c)
                        style = f' style="color:{col}"' if col else ''
                        cells.append(f'<td{style}>{e(c)}</td>')
                    body.append('<tr>' + ''.join(cells) + '</tr>')
                body.append('</tbody></table></div>')
            elif s.kind == "findings":
                for f in s.findings:
                    body.append(
                        f'<div class="finding" style="border-left-color:'
                        f'{_SEV_COLOR[f.severity]}">'
                        f'<div class="fhead">{sev_badge(f.severity)}'
                        f'<strong>{e(f.title)}</strong></div>'
                        f'<p>{e(f.detail)}</p>'
                        + (f'<p class="rec">&#9656; {e(f.recommendation)}</p>'
                           if f.recommendation else '')
                        + '</div>')
            if s.note:
                body.append(f'<p class="note">{e(s.note)}</p>')
            body.append('</div>')
        body.append('</section>')

    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(m['tool'])} Report &mdash; {e(m['host'])}</title>
<style>
:root{{--bg:#0a0e14;--panel:#111721;--card:#161b22;--border:#232b36;
--text:#e6edf3;--muted:#8b98a9;--accent:#28e0c8;--accent2:#3d8bfd;}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--text);
font:14px/1.55 -apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif}}
header{{padding:26px 32px;background:linear-gradient(120deg,#0d1420,#0a0e14);
border-bottom:1px solid var(--border)}}
header h1{{margin:0;font-size:22px;letter-spacing:.5px}}
header h1 b{{color:var(--accent)}}
.badge{{display:inline-block;margin-left:10px;padding:2px 10px;border-radius:20px;
font-size:11px;font-weight:700;background:{('#28e0c822' if demo else '#39d98a22')};
color:{('#28e0c8' if demo else '#39d98a')};
border:1px solid {('#28e0c855' if demo else '#39d98a55')}}}
.meta{{color:var(--muted);font-size:12px;margin-top:8px}}
nav{{position:sticky;top:0;background:var(--panel);padding:12px 32px;
border-bottom:1px solid var(--border);display:flex;gap:6px;flex-wrap:wrap;z-index:5}}
nav a{{color:var(--muted);text-decoration:none;font-size:12px;padding:5px 12px;
border-radius:16px;border:1px solid transparent}}
nav a:hover{{color:var(--accent);border-color:var(--border);background:var(--card)}}
main{{max-width:1000px;margin:0 auto;padding:24px 32px 80px}}
h2{{font-size:18px;margin:34px 0 14px;padding-bottom:8px;
border-bottom:1px solid var(--border)}}
h2 small{{display:block;font-size:12px;color:var(--muted);font-weight:400;margin-top:4px}}
h3{{font-size:13px;text-transform:uppercase;letter-spacing:.6px;
color:var(--accent2);margin:0 0 12px}}
.card{{background:var(--card);border:1px solid var(--border);border-radius:12px;
padding:18px 20px;margin-bottom:16px}}
table{{width:100%;border-collapse:collapse;font-size:13px}}
.scroll{{overflow-x:auto}}
.kv th{{text-align:left;color:var(--muted);font-weight:500;width:38%;
padding:5px 10px 5px 0;vertical-align:top;white-space:nowrap}}
.kv td{{padding:5px 0;font-family:ui-monospace,Menlo,Consolas,monospace}}
.grid th{{text-align:left;color:var(--accent);border-bottom:1px solid var(--border);
padding:8px 12px 8px 0;font-size:11px;text-transform:uppercase}}
.grid td{{padding:7px 12px 7px 0;border-bottom:1px solid #1c2430;
font-family:ui-monospace,Menlo,Consolas,monospace;font-size:12px}}
.finding{{background:#12181f;border:1px solid var(--border);border-left:3px solid;
border-radius:8px;padding:12px 16px;margin-bottom:10px}}
.fhead{{display:flex;align-items:center;gap:10px;margin-bottom:6px}}
.sev{{font-size:10px;font-weight:700;padding:2px 8px;border-radius:12px;
text-transform:uppercase;letter-spacing:.5px}}
.finding p{{margin:4px 0;color:var(--muted)}}
.rec{{color:var(--accent)!important}}
.note{{color:var(--muted);font-size:12px;font-style:italic;margin:6px 2px 0}}
footer{{text-align:center;color:var(--muted);font-size:11px;padding:24px}}
</style></head><body>
<header>
<h1><b>Win</b>Recon Report <span class="badge">{m['mode']}</span></h1>
<div class="meta">Host <b>{e(m['host'])}</b> &nbsp;|&nbsp; {e(m['platform'])}
&nbsp;|&nbsp; Generated {m['generated']} &nbsp;|&nbsp; v{m['version']}</div>
</header>
<nav>{''.join(nav)}</nav>
<main>{''.join(body)}</main>
<footer>Generated by {e(m['tool'])} v{m['version']} &middot; for authorised
security assessment and educational use only.</footer>
</body></html>"""
