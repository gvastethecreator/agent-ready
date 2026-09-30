#!/usr/bin/env python3
"""Read-only HTTP probe for agent-ready-site.

Fetches a bounded set of URLs with GET and records what agents that do not run
JavaScript receive: access, robots rules, markdown variants, well-known
discovery files, and static page structure. Writes one JSON evidence file and
prints a short summary. Standard library only.
"""

from __future__ import annotations

import argparse
import html as htmllib
import json
import re
import secrets
import sys
import time
import zlib
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlsplit
from urllib.request import Request, urlopen

VERSION = "0.1.0"
REGISTRY_PATH = Path(__file__).resolve().parent.parent / "references" / "standards.json"
TOOL_UA = f"agent-ready-site-probe/{VERSION} (read-only readiness audit)"
BROWSER_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
)
HTML_ACCEPT = "text/html,application/xhtml+xml;q=0.9,*/*;q=0.8"
MAX_BODY = 2_000_000
KEPT_HEADERS = (
    "content-type", "content-length", "vary", "link", "x-robots-tag", "server",
    "cf-mitigated", "retry-after", "ratelimit", "ratelimit-policy",
    "x-ratelimit-limit", "x-ratelimit-remaining", "x-markdown-tokens",
    "content-signal", "location",
)
# Markup served by bot-management challenges instead of content.
CHALLENGE_MARKERS = (
    "challenge-platform", "cf-chl-", "just a moment...", "px-captcha",
    "captcha-delivery.com", "_incapsula_resource", "verify you are human",
)
SKIP_TEXT_TAGS = {"script", "style", "noscript", "template", "svg", "title"}
FIELD_SKIP_TYPES = {"hidden", "submit", "button", "reset", "image"}
EXAMPLES = 5


class BudgetExhausted(Exception):
    pass


class Fetcher:
    def __init__(self, ua: str, limit: int, delay: float, timeout: float):
        self.ua, self.limit, self.delay, self.timeout = ua, limit, delay, timeout
        self.used = 0

    def get(self, url: str, accept: str = HTML_ACCEPT, ua: str | None = None) -> dict:
        if self.used >= self.limit:
            raise BudgetExhausted(url)
        if self.used:
            time.sleep(self.delay)
        self.used += 1
        headers = {"User-Agent": ua or self.ua, "Accept": accept, "Accept-Language": "en;q=0.9,*;q=0.5"}
        started = time.monotonic()
        try:
            with urlopen(Request(url, headers=headers), timeout=self.timeout) as resp:
                return _result(url, resp.status, resp.geturl(), resp.headers, resp.read(MAX_BODY + 1), started)
        except HTTPError as err:
            try:
                body = err.read(MAX_BODY + 1)
            except Exception:
                body = b""
            return _result(url, err.code, err.geturl() or url, err.headers, body, started)
        except (URLError, TimeoutError, OSError, ValueError) as err:
            reason = getattr(err, "reason", err)
            return {"url": url, "status": None, "error": f"{type(err).__name__}: {reason}", "headers": {},
                    "content_type": "", "bytes": 0, "_body": ""}


def _result(url, status, final_url, headers, raw: bytes, started: float) -> dict:
    truncated = len(raw) > MAX_BODY
    raw = raw[:MAX_BODY]
    encoding = (headers.get("Content-Encoding") or "").lower()
    note = None
    try:
        if raw[:2] == b"\x1f\x8b" or encoding == "gzip":
            raw = zlib.decompress(raw, 16 + zlib.MAX_WBITS)
        elif encoding == "deflate":
            raw = zlib.decompress(raw, -zlib.MAX_WBITS)
    except zlib.error:
        note = f"could not decode {encoding or 'gzip'} body"
    if encoding == "br":
        note = "brotli body not decodable with the standard library"
    ctype = (headers.get("Content-Type") or "").lower()
    charset = re.search(r"charset=([\w-]+)", ctype)
    try:
        text = raw.decode(charset.group(1) if charset else "utf-8", errors="replace")
    except LookupError:
        text = raw.decode("utf-8", errors="replace")
    kept = {}
    for name in KEPT_HEADERS:
        values = headers.get_all(name) if hasattr(headers, "get_all") else None
        if values:
            kept[name] = ", ".join(values)
    out = {
        "url": url,
        "final_url": final_url,
        "status": status,
        "content_type": ctype.split(";")[0].strip(),
        "bytes": len(raw),
        "elapsed_ms": int((time.monotonic() - started) * 1000),
        "headers": kept,
        "_body": text,
    }
    if truncated:
        out["truncated"] = True
    if note:
        out["note"] = note
    return out


def public(res: dict | None) -> dict | None:
    """Strip the private body before writing evidence."""
    if res is None:
        return None
    return {k: v for k, v in res.items() if not k.startswith("_")}


def challenge_marker(res: dict) -> str | None:
    if res["headers"].get("cf-mitigated", "").lower() == "challenge":
        return "cf-mitigated: challenge"
    body = res.get("_body", "")[:300_000].lower()
    for marker in CHALLENGE_MARKERS:
        if marker in body:
            return marker
    return None


def looks_like_html(text: str) -> bool:
    head = text.lstrip()[:300].lower()
    return head.startswith("<!doctype html") or head.startswith("<html") or "<head" in head


def norm(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()


def approx_tokens(chars: int) -> int:
    return round(chars / 4)


# ---------------------------------------------------------------- robots.txt

def parse_robots(text: str) -> tuple[list[dict], list[str]]:
    groups: list[dict] = []
    sitemaps: list[str] = []
    current = None
    in_agent_lines = False
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].strip()
        if ":" not in line:
            continue
        key, value = (part.strip() for part in line.split(":", 1))
        key = key.lower()
        if key == "user-agent":
            if current is None or not in_agent_lines:
                current = {"agents": [], "rules": [], "content_signal": []}
                groups.append(current)
            current["agents"].append(value.lower())
            in_agent_lines = True
            continue
        if key == "sitemap":
            sitemaps.append(value)
            continue
        in_agent_lines = False
        if current is None:
            continue
        if key in ("allow", "disallow") and value:
            current["rules"].append((key == "allow", value))
        elif key == "content-signal":
            current["content_signal"].append(value)
    return groups, sitemaps


def _rule_regex(pattern: str) -> re.Pattern:
    anchored = pattern.endswith("$")
    body = re.escape(pattern[:-1] if anchored else pattern).replace(r"\*", ".*")
    return re.compile(body + ("$" if anchored else ""))


def robots_verdict(groups: list[dict], token: str, path: str) -> dict:
    """RFC 9309: product-token group else '*'; longest match wins; allow wins ties."""
    matched = [g for g in groups if any(a.split("/")[0] == token for a in g["agents"])]
    source = token
    if not matched:
        matched = [g for g in groups if "*" in g["agents"]]
        source = "*" if matched else None
    best = None
    for allow, pattern in (rule for g in matched for rule in g["rules"]):
        if _rule_regex(pattern).match(path):
            key = (len(pattern), allow)
            if best is None or key > best[0]:
                best = (key, allow, pattern)
    return {
        "allowed": True if best is None else best[1],
        "group": source,
        "rule": None if best is None else f"{'Allow' if best[1] else 'Disallow'}: {best[2]}",
    }


def probe_robots(fetch: Fetcher, origin: str, agents: list[dict], paths: list[str]) -> tuple[dict, list[str]]:
    res = fetch.get(urljoin(origin, "/robots.txt"), accept="text/plain,*/*;q=0.5")
    out = public(res)
    status, body = res["status"], res["_body"]
    if status is None or status >= 500:
        out["rfc9309_effect"] = "unreachable: compliant crawlers assume complete disallow"
        return out, []
    if status >= 400:
        out["rfc9309_effect"] = "unavailable: compliant crawlers may access everything"
        return out, []
    if looks_like_html(body):
        out["rfc9309_effect"] = "HTML served at /robots.txt; no parseable rules"
        return out, []
    groups, sitemaps = parse_robots(body)
    out["groups"] = [{"agents": g["agents"], "rules": len(g["rules"]), "content_signal": g["content_signal"]}
                     for g in groups]
    out["sitemaps"] = sitemaps
    out["content_signal_present"] = any(g["content_signal"] for g in groups)
    verdicts = {}
    for agent in [{"token": "*", "name": "*"}] + agents:
        verdicts[agent["name"]] = {p: robots_verdict(groups, agent["token"], p) for p in paths}
    out["verdicts"] = verdicts
    return out, sitemaps


# ------------------------------------------------------------------- sitemap

def _locs(body: str) -> list[str]:
    return [htmllib.unescape(u) for u in re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", body, re.I)]


def probe_sitemap(fetch: Fetcher, origin: str, declared: list[str]) -> tuple[dict, list[str]]:
    url = declared[0] if declared else urljoin(origin, "/sitemap.xml")
    res = fetch.get(url, accept="application/xml,text/xml;q=0.9,*/*;q=0.5")
    out = public(res)
    out["declared_in_robots"] = bool(declared)
    body = res["_body"]
    if res["status"] != 200 or "<loc>" not in body.lower():
        out["valid"] = False
        return out, []
    locs = _locs(body)
    if re.search(r"<sitemapindex", body, re.I):
        out["index_children"] = len(locs)
        if not locs:
            return out, []
        child = fetch.get(locs[0], accept="application/xml,text/xml;q=0.9,*/*;q=0.5")
        out["sampled_child"] = {"url": locs[0], "status": child["status"]}
        body = child["_body"]
        locs = _locs(body)
    out["valid"] = bool(locs)
    out["url_count"] = len(locs)
    out["has_lastmod"] = "<lastmod>" in body.lower()
    out["sample"] = locs[:10]
    return out, locs


# ------------------------------------------------------------------ llms.txt

def probe_llms(fetch: Fetcher, origin: str, link_checks: int = 3) -> dict:
    res = fetch.get(urljoin(origin, "/llms.txt"), accept="text/markdown,text/plain;q=0.9,*/*;q=0.5")
    out = public(res)
    body = res["_body"]
    if res["status"] != 200 or looks_like_html(body):
        out["present"] = False
        return out
    lines = [line.strip() for line in body.splitlines() if line.strip()]
    links = re.findall(r"\[[^\]]*\]\(([^)\s]+)\)", body)
    out.update({
        "present": True,
        "has_h1": bool(lines) and lines[0].startswith("# "),
        "has_summary": any(line.startswith("> ") for line in lines[:6]),
        "sections": [line[3:] for line in lines if line.startswith("## ")][:20],
        "links": len(links),
        "markdown_links": sum(1 for u in links if urlsplit(u).path.endswith(".md")),
        "approx_tokens": approx_tokens(len(body)),
    })
    checked = []
    for link in links[:link_checks]:
        target = urljoin(res["final_url"], link)
        if urlsplit(target).scheme not in ("http", "https"):
            continue
        linked = fetch.get(target, accept="text/markdown,text/plain;q=0.9,*/*;q=0.5")
        checked.append({"url": target, "status": linked["status"], "content_type": linked["content_type"]})
    out["link_checks"] = checked
    return out


# -------------------------------------------------------------- well-known

def probe_well_known(fetch: Fetcher, origin: str, capabilities: list[dict]) -> list[dict]:
    results = []
    for cap in capabilities:
        for path in cap.get("probe_paths", []):
            expect = cap.get("expect", "json")
            accept = {"linkset": "application/linkset+json,application/json;q=0.9,*/*;q=0.5",
                      "text": "text/plain,text/markdown;q=0.9,*/*;q=0.5"}.get(expect, "application/json,*/*;q=0.5")
            res = fetch.get(urljoin(origin, path), accept=accept)
            entry = {"id": cap["id"], "path": path, "status": res["status"], "content_type": res["content_type"],
                     "bytes": res["bytes"]}
            body = res["_body"]
            valid = False
            if res["status"] == 200 and not looks_like_html(body):
                if expect == "text":
                    valid = bool(body.strip())
                else:
                    try:
                        data = json.loads(body)
                        valid = "linkset" in data if expect == "linkset" else True
                    except (json.JSONDecodeError, TypeError):
                        valid = False
                    if expect == "linkset" and res["content_type"] != "application/linkset+json":
                        entry["note"] = "RFC 9727 expects application/linkset+json"
            elif res["status"] == 200:
                entry["note"] = "HTML served; likely an app fallback, not the resource"
            entry["present"] = valid
            results.append(entry)
    return results


# --------------------------------------------------------------- page parse

class PageParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.skip = 0
        self.in_title = False
        self.in_jsonld = False
        self.title = []
        self.text = []
        self.jsonld_blocks = []
        self.lang = None
        self.meta_description = None
        self.meta_robots = None
        self.canonical = None
        self.md_alternates = []
        self.og_tags = 0
        self.h1 = 0
        self.headings = []
        self.heading = None
        self.landmarks = {"main": 0, "nav": 0}
        self.images = 0
        self.images_no_alt = 0
        self.frames = []
        self.unnamed_controls = []
        self.controls = 0
        self.fields = []
        self.label_for = set()
        self.label_depth = 0
        self.clickable_non_semantic = []
        self.counts = {"forms": 0, "tool_forms": 0, "scripts": 0, "iframes": 0, "canvas": 0, "tables": 0}

    def handle_starttag(self, tag, attrs):
        a = {k: (v or "") for k, v in attrs}
        role = a.get("role", "").lower()
        if tag == "html":
            self.lang = a.get("lang") or None
        elif tag == "meta":
            name = a.get("name", "").lower()
            if name == "description":
                self.meta_description = a.get("content", "")
            elif name == "robots":
                self.meta_robots = a.get("content", "")
            if a.get("property", "").lower().startswith("og:"):
                self.og_tags += 1
        elif tag == "link":
            rels = a.get("rel", "").lower().split()
            if "canonical" in rels:
                self.canonical = a.get("href")
            if "alternate" in rels and a.get("type", "").lower() == "text/markdown" and a.get("href"):
                self.md_alternates.append(a["href"])
        elif tag == "script":
            if a.get("type", "").lower() == "application/ld+json":
                self.in_jsonld = True
                self.jsonld_blocks.append([])
            else:
                self.counts["scripts"] += 1
        elif tag == "title":
            self.in_title = self.skip == 0  # ignore <svg><title>
        elif tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self.h1 += tag == "h1"
            self.heading = (int(tag[1]), [])
        elif tag == "img":
            self.images += 1
            if "alt" not in a:
                self.images_no_alt += 1
            elif a["alt"].strip():
                for frame in self.frames:
                    frame["text"].append(a["alt"])
        elif tag == "form":
            self.counts["forms"] += 1
            if a.get("toolname"):
                self.counts["tool_forms"] += 1
        elif tag == "iframe":
            self.counts["iframes"] += 1
        elif tag == "canvas":
            self.counts["canvas"] += 1
        elif tag == "table":
            self.counts["tables"] += 1
        elif tag == "label":
            self.label_depth += 1
            if a.get("for"):
                self.label_for.add(a["for"])

        if tag == "main" or role == "main":
            self.landmarks["main"] += 1
        if tag == "nav" or role == "navigation":
            self.landmarks["nav"] += 1
        if tag in ("a", "button") and (tag == "button" or "href" in a):
            self.controls += 1
            named = any(a.get(k, "").strip() for k in ("aria-label", "aria-labelledby", "title"))
            self.frames.append({"tag": tag, "named": named, "text": [], "snippet": self.get_starttag_text()[:140]})
        if tag in ("input", "select", "textarea"):
            if not (tag == "input" and a.get("type", "text").lower() in FIELD_SKIP_TYPES):
                self.fields.append({
                    "id": a.get("id"),
                    "named": any(a.get(k, "").strip() for k in ("aria-label", "aria-labelledby", "title")),
                    "in_label": self.label_depth > 0,
                    "placeholder": bool(a.get("placeholder", "").strip()),
                    "snippet": self.get_starttag_text()[:140],
                })
        if tag in ("div", "span", "li", "td", "img", "p") and "onclick" in a and not role:
            self.clickable_non_semantic.append(self.get_starttag_text()[:140])
        if tag in SKIP_TEXT_TAGS:
            self.skip += 1

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag in SKIP_TEXT_TAGS:
            self.skip = max(0, self.skip - 1)

    def handle_endtag(self, tag):
        if tag in SKIP_TEXT_TAGS:
            self.skip = max(0, self.skip - 1)
        if tag == "script":
            self.in_jsonld = False
        elif tag == "title":
            self.in_title = False
        elif tag == "label":
            self.label_depth = max(0, self.label_depth - 1)
        elif tag in ("h1", "h2", "h3", "h4", "h5", "h6") and self.heading:
            if len(self.headings) < 25:
                self.headings.append({"level": self.heading[0], "text": norm(" ".join(self.heading[1]))[:90]})
            self.heading = None
        elif tag in ("a", "button"):
            for i in range(len(self.frames) - 1, -1, -1):
                if self.frames[i]["tag"] == tag:
                    self._close_frame(self.frames.pop(i))
                    break

    def _close_frame(self, frame):
        if not frame["named"] and not norm(" ".join(frame["text"])):
            self.unnamed_controls.append(frame["snippet"])

    def handle_data(self, data):
        if self.in_jsonld:
            self.jsonld_blocks[-1].append(data)
            return
        if self.in_title:
            self.title.append(data)
            return
        if self.skip:
            return
        self.text.append(data)
        if self.heading:
            self.heading[1].append(data)
        for frame in self.frames:
            frame["text"].append(data)

    def summary(self) -> dict:
        for frame in self.frames:
            self._close_frame(frame)
        self.frames = []
        unlabeled = [f for f in self.fields
                     if not (f["named"] or f["in_label"] or (f["id"] and f["id"] in self.label_for))]
        types, jsonld_errors = [], 0
        for block in self.jsonld_blocks:
            try:
                _collect_types(json.loads("".join(block)), types)
            except json.JSONDecodeError:
                jsonld_errors += 1
        return {
            "title": norm(" ".join(self.title)),
            "lang": self.lang,
            "meta_description": bool(self.meta_description and self.meta_description.strip()),
            "meta_robots": self.meta_robots,
            "canonical": self.canonical,
            "md_alternates": self.md_alternates,
            "og_tags": self.og_tags,
            "h1_count": self.h1,
            "headings": self.headings,
            "landmarks": self.landmarks,
            "jsonld_types": sorted(set(types)),
            "jsonld_errors": jsonld_errors,
            "images": self.images,
            "images_missing_alt": self.images_no_alt,
            "controls": self.controls,
            "unnamed_controls": len(self.unnamed_controls),
            "unnamed_control_examples": self.unnamed_controls[:EXAMPLES],
            "fields": len(self.fields),
            "unlabeled_fields": len(unlabeled),
            "placeholder_only_fields": sum(1 for f in unlabeled if f["placeholder"]),
            "unlabeled_field_examples": [f["snippet"] for f in unlabeled[:EXAMPLES]],
            "clickable_non_semantic": len(self.clickable_non_semantic),
            "clickable_non_semantic_examples": self.clickable_non_semantic[:EXAMPLES],
            **self.counts,
        }


def _collect_types(node, out: list):
    if isinstance(node, list):
        for item in node:
            _collect_types(item, out)
    elif isinstance(node, dict):
        kind = node.get("@type")
        if isinstance(kind, str):
            out.append(kind)
        elif isinstance(kind, list):
            out.extend(k for k in kind if isinstance(k, str))
        for value in node.values():
            if isinstance(value, (dict, list)):
                _collect_types(value, out)


def parse_link_header(value: str) -> list[dict]:
    links = []
    for target, params in re.findall(r"<([^>]*)>\s*((?:;\s*[^;,]+)*)", value or ""):
        attrs = {}
        for key, val in re.findall(r";\s*([\w*-]+)\s*=\s*\"?([^\";,]*)\"?", params):
            attrs[key.lower()] = val.strip()
        links.append({"href": target, "rel": attrs.get("rel", "").lower(), "type": attrs.get("type", "").lower()})
    return links


# ---------------------------------------------------------------------- page

def probe_page(fetch: Fetcher, url: str, facts: list[str]) -> dict:
    res = fetch.get(url)
    page = public(res)
    page.pop("url", None)
    page = {"url": url, **page}
    body = res["_body"]
    marker = challenge_marker(res) if res["status"] is not None else None
    if marker:
        page["challenge_suspected"] = marker
    raw_text = ""
    parsed = None
    if res["status"] == 200 and ("html" in res["content_type"] or looks_like_html(body)):
        parser = PageParser()
        try:
            parser.feed(body)
            parser.close()
        except Exception as err:  # malformed markup should not end the audit
            page["parse_error"] = str(err)[:200]
        parsed = parser.summary()
        raw_text = norm(" ".join(parser.text))
        parsed["text_chars"] = len(raw_text)
        parsed["approx_tokens_html"] = approx_tokens(len(body))
        parsed["approx_tokens_text"] = approx_tokens(len(raw_text))
        parsed["js_shell_suspected"] = len(raw_text) < 300 and parsed["scripts"] > 0
        page["html"] = parsed

    header_links = parse_link_header(res["headers"].get("link", ""))
    page["link_header_rels"] = sorted({l["rel"] for l in header_links if l["rel"]})

    md = fetch.get(url, accept="text/markdown")
    md_ok = md["status"] == 200 and md["content_type"] == "text/markdown" and not looks_like_html(md["_body"])
    page["markdown_negotiation"] = {
        "status": md["status"],
        "content_type": md["content_type"],
        "vary_accept": "accept" in md["headers"].get("vary", "").lower(),
        "x_markdown_tokens": md["headers"].get("x-markdown-tokens"),
        "ok": md_ok,
        "approx_tokens": approx_tokens(len(md["_body"])) if md_ok else None,
    }
    md_text = md["_body"] if md_ok else ""

    declared = [l["href"] for l in header_links if "alternate" in l["rel"].split() and l["type"] == "text/markdown"]
    declared += parsed["md_alternates"] if parsed else []
    alt_url = urljoin(res.get("final_url") or url, declared[0]) if declared else None
    guessed = False
    if not alt_url and not md_ok and res["status"] == 200:
        path = urlsplit(res.get("final_url") or url).path or "/"
        alt_url = urljoin(url, path + "index.md" if path.endswith("/") else path + ".md")
        guessed = True
    if alt_url:
        alt = fetch.get(alt_url, accept="text/markdown,text/plain;q=0.9,*/*;q=0.1")
        alt_ok = alt["status"] == 200 and not looks_like_html(alt["_body"]) and bool(alt["_body"].strip())
        page["markdown_alternate"] = {"url": alt_url, "declared": not guessed, "status": alt["status"],
                                      "content_type": alt["content_type"], "ok": alt_ok,
                                      "approx_tokens": approx_tokens(len(alt["_body"])) if alt_ok else None}
        if alt_ok and not md_text:
            md_text = alt["_body"]

    if facts:
        source = norm(body)
        md_norm = norm(md_text)
        page["facts"] = [{
            "fact": fact,
            "visible_text": norm(fact) in raw_text,
            "html_source": norm(fact) in source,
            "markdown": (norm(fact) in md_norm) if md_text else None,
        } for fact in facts]
    return page


# ----------------------------------------------------------------- ua matrix

def probe_ua_matrix(fetch: Fetcher, url: str, agents: list[dict]) -> list[dict]:
    rows = []
    candidates = [("browser", BROWSER_UA), ("tool", TOOL_UA)] + [
        (a["name"], f"Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; {a['name']}/1.0; "
                    f"+agent-ready-site probe)")
        for a in agents if a.get("ua_probe")
    ]
    baseline = None
    for name, ua in candidates:
        res = fetch.get(url, ua=ua)
        row = {"agent": name, "status": res["status"], "bytes": res["bytes"], "error": res.get("error")}
        marker = challenge_marker(res) if res["status"] is not None else None
        if marker:
            row["challenge_suspected"] = marker
        if baseline is None:
            baseline = row
        else:
            ratio = res["bytes"] / baseline["bytes"] if baseline["bytes"] else 1.0
            row["differs_from_browser"] = (row["status"] != baseline["status"] or not 0.5 <= ratio <= 2.0
                                           or bool(marker))
        rows.append(row)
    return rows


# ---------------------------------------------------------------- selection

def _host(url: str) -> str:
    return urlsplit(url).netloc.lower().removeprefix("www.")


def _segment(url: str) -> str:
    parts = [p for p in urlsplit(url).path.split("/") if p]
    return parts[0] if parts else ""


def select_pages(base: str, explicit: list[str], locs: list[str], max_pages: int) -> list[str]:
    pages = []
    for url in [base] + [urljoin(base, p) for p in explicit]:
        if url not in pages:
            pages.append(url)
    seen = {_segment(p) for p in pages}
    for loc in locs:
        if len(pages) >= max_pages:
            break
        if _host(loc) != _host(base) or loc in pages or _segment(loc) in seen:
            continue
        seen.add(_segment(loc))
        pages.append(loc)
    return pages


def parse_expect(values: list[str], base: str) -> list[tuple[str, str]]:
    out = []
    for value in values:
        if "::" not in value:
            raise SystemExit(f"--expect needs PATH::TEXT, got {value!r}")
        path, fact = value.split("::", 1)
        out.append(("*" if path.strip() == "*" else urljoin(base, path.strip()), fact.strip()))
    return out


def facts_for(url: str, expects: list[tuple[str, str]]) -> list[str]:
    key = url.rstrip("/")
    return [fact for target, fact in expects if target == "*" or target.rstrip("/") == key]


# --------------------------------------------------------------------- main

def summarize(report: dict) -> str:
    lines = [f"agent-ready-site probe {VERSION}: {report['base_url']} "
             f"(ua={report['ua_mode']}, requests {report['requests']['used']}/{report['requests']['limit']})"]
    robots = report.get("robots") or {}
    blocked = sorted({name for name, verdicts in (robots.get("verdicts") or {}).items()
                      if name != "*" and not all(v["allowed"] for v in verdicts.values())})
    lines.append(f"robots.txt {robots.get('status')} | groups {len(robots.get('groups') or [])} | "
                 f"content-signal {'yes' if robots.get('content_signal_present') else 'no'} | "
                 f"blocked on sampled paths: {', '.join(blocked) or 'none'}"
                 + (f" | {robots['rfc9309_effect']}" if robots.get("rfc9309_effect") else ""))
    sm = report.get("sitemap") or {}
    lines.append(f"sitemap {sm.get('status')} | urls {sm.get('url_count', 0)} | lastmod {sm.get('has_lastmod', False)}")
    llms = report.get("llms_txt") or {}
    lines.append(f"llms.txt {llms.get('status')} | present {llms.get('present')} | links {llms.get('links', 0)}")
    soft = report.get("soft_404") or {}
    lines.append(f"unknown path -> {soft.get('status')} ({'soft 404: presence needs content checks' if soft.get('suspected') else 'ok'})")
    found = [w["path"] for w in report.get("well_known", []) if w["present"]]
    lines.append(f"well-known present: {', '.join(found) or 'none'}")
    for page in report.get("pages", []):
        html = page.get("html") or {}
        mdn = page.get("markdown_negotiation") or {}
        alt = page.get("markdown_alternate") or {}
        bits = [f"{page.get('status')}", f"text {html.get('text_chars', 0)}c",
                f"md-neg {'ok' if mdn.get('ok') else mdn.get('content_type') or mdn.get('status')}",
                f"md-alt {'ok' if alt.get('ok') else 'no'}",
                f"h1 {html.get('h1_count', 0)}", f"main {html.get('landmarks', {}).get('main', 0)}",
                f"unnamed {html.get('unnamed_controls', 0)}", f"unlabeled {html.get('unlabeled_fields', 0)}",
                f"jsonld {','.join(html.get('jsonld_types', [])[:4]) or '-'}"]
        if page.get("error"):
            bits.append(f"ERROR {page['error']}")
        if page.get("challenge_suspected"):
            bits.append(f"CHALLENGE {page['challenge_suspected']}")
        if html.get("js_shell_suspected"):
            bits.append("JS-SHELL")
        lines.append(f"page {page['url']}: " + " | ".join(bits))
        for fact in page.get("facts", []):
            lines.append(f"  fact {fact['fact']!r}: visible={fact['visible_text']} "
                         f"source={fact['html_source']} markdown={fact['markdown']}")
    for row in report.get("ua_matrix") or []:
        if row.get("differs_from_browser"):
            lines.append(f"ua {row['agent']}: status {row['status']} bytes {row['bytes']} differs from browser"
                         + (f" ({row['challenge_suspected']})" if row.get("challenge_suspected") else ""))
    for limit in report["limits"]:
        lines.append(f"limit: {limit}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("url", help="Base URL, for example https://example.com/")
    parser.add_argument("--out", required=True, help="New JSON evidence file; must not exist")
    parser.add_argument("--page", action="append", default=[], help="Job start path or URL (repeatable)")
    parser.add_argument("--expect", action="append", default=[],
                        help="Fact a read job needs, as PATH::TEXT or *::TEXT (repeatable)")
    parser.add_argument("--max-pages", type=int, default=6, help="Page cap including sitemap samples (default 6)")
    parser.add_argument("--ua", choices=("tool", "browser"), default="tool",
                        help="User agent for content checks: honest tool UA (default) or a browser UA")
    parser.add_argument("--ua-matrix", action="store_true",
                        help="Compare the base URL across browser, tool, and registry agent user agents")
    parser.add_argument("--max-requests", type=int, default=90, help="Hard request budget (default 90)")
    parser.add_argument("--delay", type=float, default=0.3, help="Seconds between requests (default 0.3)")
    parser.add_argument("--timeout", type=float, default=15, help="Per-request timeout seconds (default 15)")
    args = parser.parse_args(argv)

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    base = args.url if urlsplit(args.url).path else args.url.rstrip("/") + "/"
    if urlsplit(base).scheme not in ("http", "https"):
        parser.error("url must be http or https")
    out_path = Path(args.out)
    if out_path.exists():
        parser.error(f"{out_path} exists; choose a new file to preserve earlier evidence")

    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    agents = registry["agents"]
    origin = f"{urlsplit(base).scheme}://{urlsplit(base).netloc}"
    fetch = Fetcher(BROWSER_UA if args.ua == "browser" else TOOL_UA, args.max_requests, args.delay, args.timeout)
    expects = parse_expect(args.expect, base)
    report = {
        "tool": "agent-ready-site/scripts/probe_site.py",
        "version": VERSION,
        "started_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "base_url": base,
        "ua_mode": args.ua,
        "registry_last_verified": registry["last_verified"],
        "limits": [
            "Static parse of server HTML: rendered DOM, CSS visibility, and framework event handlers need the browser operate test.",
            "Token counts are approximate (characters / 4).",
        ],
    }
    exit_code = 0
    try:
        explicit_paths = [urlsplit(urljoin(base, p)).path or "/" for p in args.page]
        sample_paths = sorted({urlsplit(base).path or "/", *explicit_paths})
        report["robots"], declared = probe_robots(fetch, origin, agents, sample_paths)
        report["sitemap"], locs = probe_sitemap(fetch, origin, declared)
        soft = fetch.get(urljoin(origin, f"/agent-ready-site-{secrets.token_hex(6)}"))
        report["soft_404"] = {"status": soft["status"], "content_type": soft["content_type"],
                              "suspected": soft["status"] == 200}
        report["llms_txt"] = probe_llms(fetch, origin)
        report["well_known"] = probe_well_known(fetch, origin, registry["capabilities"])
        pages = select_pages(base, args.page, locs, args.max_pages)
        report["pages"] = []
        for url in pages:
            report["pages"].append(probe_page(fetch, url, facts_for(url, expects)))
        if report["pages"] and report["pages"][0]["status"] is None:
            exit_code = 1
        if args.ua_matrix:
            report["ua_matrix"] = probe_ua_matrix(fetch, base, agents)
            report["limits"].append("Spoofed user agents reveal user-agent rules only; IP- or signature-verified "
                                    "bot rules need CDN or server evidence.")
    except BudgetExhausted as stop:
        report["limits"].append(f"Request budget {args.max_requests} exhausted before {stop}; results are partial.")
    blocked = [p for p in report.get("pages", [])
               if p.get("challenge_suspected") or (p.get("html") or {}).get("js_shell_suspected")]
    if blocked and args.ua == "tool":
        report["limits"].append("Content checks hit a challenge or JS shell; rerun with --ua browser to separate "
                                "access from read.")
    report["requests"] = {"used": fetch.used, "limit": args.max_requests}

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(summarize(report))
    print(f"evidence: {out_path}")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
