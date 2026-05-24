#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "pygments>=2.17",
# ]
# ///
"""Small local renderer/index for this crackme practice repository."""

from __future__ import annotations

import argparse
import html
import http.server
import json
import mimetypes
import os
import posixpath
import re
import socketserver
import subprocess
import sys
import textwrap
import urllib.parse
import webbrowser
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

SKIP_DIRS = {
    ".git",
    ".wine-prefix",
    ".wine",
    "__pycache__",
    ".pytest_cache",
    "crack-me-all.rep",
    "crackme-gh.rep",
}

MARKDOWN_EXTS = {".md", ".markdown"}
HTML_EXTS = {".html", ".htm"}
TEXT_EXTS = {".txt", ".log", ".cfg", ".ini", ".json", ".yml", ".yaml", ".toml", ".csv"}
SOURCE_EXTS = {
    ".asm",
    ".c",
    ".cc",
    ".cpp",
    ".cs",
    ".go",
    ".h",
    ".hpp",
    ".java",
    ".js",
    ".ld",
    ".py",
    ".rs",
    ".s",
    ".sh",
    ".S",
}
IMAGE_EXTS = {".gif", ".jpeg", ".jpg", ".png", ".webp"}
PDF_EXTS = {".pdf"}
ARCHIVE_EXTS = {".7z", ".gz", ".rar", ".tar", ".tgz", ".zip"}
BINARY_EXTS = {".bin", ".dll", ".dylib", ".exe", ".flp", ".scr", ".so"}

READABLE_NAMES = {"readme", "license", "makefile"}


@dataclass(frozen=True)
class Entry:
    path: str
    name: str
    kind: str
    category: str
    title: str
    size: int
    size_human: str
    tags: list[str]


def human_size(size: int) -> str:
    units = ["B", "KB", "MB", "GB"]
    value = float(size)
    for unit in units:
        if value < 1024 or unit == units[-1]:
            if unit == "B":
                return f"{int(value)} {unit}"
            return f"{value:.1f} {unit}"
        value /= 1024
    return f"{size} B"


def rel_path(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def safe_resolve(raw_path: str) -> Path:
    raw_path = urllib.parse.unquote(raw_path).replace("\\", "/")
    raw_path = raw_path.lstrip("/")
    normalized = posixpath.normpath(raw_path)
    if normalized in {"", "."} or normalized.startswith("../"):
        raise ValueError("invalid path")
    candidate = (ROOT / normalized).resolve()
    candidate.relative_to(ROOT.resolve())
    if not candidate.is_file():
        raise FileNotFoundError(normalized)
    return candidate


def walk_files() -> list[Path]:
    files: list[Path] = []
    for current, dirs, names in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        current_path = Path(current)
        for name in names:
            path = current_path / name
            if path.name.endswith((".pyc", ".tmp", ".lock", ".lock~")):
                continue
            if path.name in {"crack-me-all.gpr", "crackme-gh.gpr"}:
                continue
            files.append(path)
    return sorted(files, key=lambda p: rel_path(p).lower())


def kind_for(path: Path) -> str:
    ext = path.suffix.lower()
    stem = path.name.lower()
    if ext in MARKDOWN_EXTS or stem in READABLE_NAMES:
        return "markdown"
    if ext in HTML_EXTS:
        return "html"
    if ext in IMAGE_EXTS:
        return "image"
    if ext in PDF_EXTS:
        return "pdf"
    if ext in ARCHIVE_EXTS:
        return "archive"
    if ext in BINARY_EXTS:
        return "binary"
    if ext in SOURCE_EXTS:
        return "source"
    if ext in TEXT_EXTS:
        return "text"
    try:
        data = path.read_bytes()[:2048]
    except OSError:
        return "other"
    if b"\x00" in data:
        return "binary"
    return "text"


def category_for(path: str, kind: str) -> str:
    if path.startswith("solutions/"):
        return "Solutions"
    if path.startswith("docs/") or path in {"README.md", "Import_and_create_project_tutorial.md"}:
        return "Repo Docs"
    if path.startswith("crackmes/"):
        return "Original Crackmes"
    if path.startswith("practice/crackmes-one/"):
        return "crackmes.one"
    if path.startswith("practice/crackmes-one-ctf-2026/"):
        return "crackmes.one CTF 2026"
    if path.startswith("practice/nightmare/"):
        return "Nightmare"
    if path.startswith("practice/pwncollege"):
        return "pwn.college"
    if path.startswith("practice/"):
        return "Practice"
    if kind == "image":
        return "Images"
    if kind == "archive":
        return "Archives"
    return "Other"


def read_text(path: Path, max_bytes: int = 2_000_000) -> str:
    data = path.read_bytes()
    truncated = len(data) > max_bytes
    if truncated:
        data = data[:max_bytes]
    text = data.decode("utf-8", errors="replace")
    if truncated:
        text += "\n\n[viewer truncated this large text file]\n"
    return text


def extract_title(path: Path, kind: str) -> str:
    name = path.name
    try:
        text = read_text(path, 120_000)
    except OSError:
        return name
    if kind == "html":
        match = re.search(r"<title[^>]*>(.*?)</title>", text, re.I | re.S)
        if match:
            return html.unescape(re.sub(r"\s+", " ", match.group(1)).strip()) or name
    for line in text.splitlines()[:80]:
        stripped = line.strip()
        if stripped.startswith("#"):
            return stripped.lstrip("#").strip() or name
    for line in text.splitlines()[:30]:
        stripped = line.strip()
        if stripped:
            return stripped[:120]
    return name


def tags_for(path: str, kind: str) -> list[str]:
    lowered = path.lower()
    tags: list[str] = [kind]
    if "solution" in lowered or "writeup" in lowered or "/flag" in lowered or lowered.endswith("flag.txt"):
        tags.append("spoiler")
    if "handout" in lowered:
        tags.append("handout")
    if "reverse-engineering" in lowered or "beginner_re" in lowered:
        tags.append("re")
    if any(word in lowered for word in ("heap", "rop", "shellcode", "bof", "format")):
        tags.append("exploit-adjacent")
    if any(word in lowered for word in ("ghidra", "x64dbg", "gdb", "tool")):
        tags.append("tools")
    return tags


def build_index() -> list[Entry]:
    entries: list[Entry] = []
    for path in walk_files():
        rp = rel_path(path)
        kind = kind_for(path)
        stat = path.stat()
        entries.append(
            Entry(
                path=rp,
                name=path.name,
                kind=kind,
                category=category_for(rp, kind),
                title=extract_title(path, kind) if kind in {"markdown", "html", "text", "source"} else path.name,
                size=stat.st_size,
                size_human=human_size(stat.st_size),
                tags=tags_for(rp, kind),
            )
        )
    return entries


def raw_url(path: str) -> str:
    return "/raw/" + urllib.parse.quote(path, safe="/")


def view_hash(path: str) -> str:
    return "#path=" + urllib.parse.quote(path, safe="/")


def resolve_link(base_path: str, target: str, image: bool = False) -> str:
    parsed = urllib.parse.urlparse(target)
    if parsed.scheme or target.startswith("#") or target.startswith("mailto:"):
        return target
    base_dir = posixpath.dirname(base_path)
    normalized = posixpath.normpath(posixpath.join(base_dir, target))
    if normalized.startswith("../"):
        return target
    candidate = ROOT / normalized
    if image:
        return raw_url(normalized)
    if candidate.is_file():
        kind = kind_for(candidate)
        if kind in {"markdown", "html", "text", "source", "image", "pdf"}:
            return view_hash(normalized)
        return raw_url(normalized)
    return target


def inline_markdown(text: str, base_path: str) -> str:
    placeholders: list[str] = []

    def stash(value: str) -> str:
        placeholders.append(value)
        return f"\x00{len(placeholders) - 1}\x00"

    text = html.escape(text)

    def image_repl(match: re.Match[str]) -> str:
        alt = match.group(1)
        src = html.unescape(match.group(2).strip())
        href = resolve_link(base_path, src, image=True)
        return stash(f'<img src="{html.escape(href)}" alt="{alt}">')

    def link_repl(match: re.Match[str]) -> str:
        label = match.group(1)
        href_raw = html.unescape(match.group(2).strip())
        href = resolve_link(base_path, href_raw)
        target = ' target="_blank" rel="noreferrer"' if urllib.parse.urlparse(href).scheme else ""
        return stash(f'<a href="{html.escape(href)}"{target}>{label}</a>')

    text = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", image_repl, text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", link_repl, text)
    text = re.sub(r"`([^`]+)`", lambda m: stash(f"<code>{m.group(1)}</code>"), text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"__([^_]+)__", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"<em>\1</em>", text)
    text = re.sub(r"(?<!_)_([^_\n]+)_(?!_)", r"<em>\1</em>", text)
    for i, value in enumerate(placeholders):
        text = text.replace(f"\x00{i}\x00", value)
    return text


def render_code(code: str, lang: str = "") -> str:
    try:
        from pygments import highlight
        from pygments.formatters import HtmlFormatter
        from pygments.lexers import TextLexer, get_lexer_by_name
    except Exception:
        return f"<pre><code>{html.escape(code)}</code></pre>"
    try:
        lexer = get_lexer_by_name(lang or "text")
    except Exception:
        lexer = TextLexer()
    formatter = HtmlFormatter(nowrap=False, noclasses=True)
    return highlight(code, lexer, formatter)


def is_table(lines: list[str], index: int) -> bool:
    if index + 1 >= len(lines):
        return False
    return "|" in lines[index] and re.match(r"^\s*\|?[\s:|-]+\|[\s:|-]*$", lines[index + 1]) is not None


def split_table_row(line: str) -> list[str]:
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|"):
        line = line[:-1]
    return [cell.strip() for cell in line.split("|")]


def render_markdown(text: str, base_path: str) -> str:
    lines = text.splitlines()
    out: list[str] = []
    i = 0
    in_code = False
    code_lang = ""
    code_lines: list[str] = []
    paragraph: list[str] = []
    list_stack: list[str] = []

    def flush_paragraph() -> None:
        nonlocal paragraph
        if paragraph:
            content = inline_markdown(" ".join(part.strip() for part in paragraph), base_path)
            out.append(f"<p>{content}</p>")
            paragraph = []

    def close_lists() -> None:
        nonlocal list_stack
        while list_stack:
            out.append(f"</{list_stack.pop()}>")

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if in_code:
            if stripped.startswith("```"):
                out.append(render_code("\n".join(code_lines), code_lang))
                in_code = False
                code_lang = ""
                code_lines = []
            else:
                code_lines.append(line)
            i += 1
            continue

        if stripped.startswith("```"):
            flush_paragraph()
            close_lists()
            in_code = True
            code_lang = stripped[3:].strip()
            i += 1
            continue

        if not stripped:
            flush_paragraph()
            close_lists()
            i += 1
            continue

        heading = re.match(r"^(#{1,6})\s+(.+)$", stripped)
        if heading:
            flush_paragraph()
            close_lists()
            level = len(heading.group(1))
            text_html = inline_markdown(heading.group(2), base_path)
            slug = re.sub(r"[^a-z0-9]+", "-", heading.group(2).lower()).strip("-")
            out.append(f'<h{level} id="{html.escape(slug)}">{text_html}</h{level}>')
            i += 1
            continue

        if stripped in {"---", "***", "___"}:
            flush_paragraph()
            close_lists()
            out.append("<hr>")
            i += 1
            continue

        if is_table(lines, i):
            flush_paragraph()
            close_lists()
            headers = split_table_row(lines[i])
            i += 2
            rows: list[list[str]] = []
            while i < len(lines) and "|" in lines[i].strip():
                rows.append(split_table_row(lines[i]))
                i += 1
            out.append("<table><thead><tr>")
            out.extend(f"<th>{inline_markdown(cell, base_path)}</th>" for cell in headers)
            out.append("</tr></thead><tbody>")
            for row in rows:
                out.append("<tr>")
                out.extend(f"<td>{inline_markdown(cell, base_path)}</td>" for cell in row)
                out.append("</tr>")
            out.append("</tbody></table>")
            continue

        quote = re.match(r"^>\s?(.*)$", line)
        if quote:
            flush_paragraph()
            close_lists()
            out.append(f"<blockquote>{inline_markdown(quote.group(1), base_path)}</blockquote>")
            i += 1
            continue

        item = re.match(r"^\s*([-*+])\s+(.+)$", line)
        ordered = re.match(r"^\s*\d+[.)]\s+(.+)$", line)
        if item or ordered:
            flush_paragraph()
            list_type = "ol" if ordered else "ul"
            if not list_stack or list_stack[-1] != list_type:
                close_lists()
                out.append(f"<{list_type}>")
                list_stack.append(list_type)
            value = ordered.group(1) if ordered else item.group(2)
            out.append(f"<li>{inline_markdown(value, base_path)}</li>")
            i += 1
            continue

        close_lists()
        paragraph.append(line)
        i += 1

    if in_code:
        out.append(render_code("\n".join(code_lines), code_lang))
    flush_paragraph()
    close_lists()
    return "\n".join(out)


def file_command(path: Path) -> str:
    try:
        result = subprocess.run(["file", "-b", str(path)], text=True, capture_output=True, timeout=3)
    except Exception:
        return ""
    return result.stdout.strip()


def render_file(path: Path) -> dict[str, object]:
    rp = rel_path(path)
    kind = kind_for(path)
    title = extract_title(path, kind) if kind in {"markdown", "html", "text", "source"} else path.name
    stat = path.stat()
    common = {
        "path": rp,
        "kind": kind,
        "title": title,
        "size": stat.st_size,
        "size_human": human_size(stat.st_size),
        "raw_url": raw_url(rp),
    }
    if kind == "markdown":
        return {**common, "mode": "html", "html": render_markdown(read_text(path), rp)}
    if kind in {"text", "source"}:
        text = read_text(path)
        lang = path.suffix.lstrip(".")
        return {**common, "mode": "html", "html": render_code(text, lang)}
    if kind == "html":
        return {**common, "mode": "iframe"}
    if kind == "image":
        return {**common, "mode": "image"}
    if kind == "pdf":
        return {**common, "mode": "pdf"}
    return {
        **common,
        "mode": "meta",
        "file_info": file_command(path),
        "tags": tags_for(rp, kind),
    }


APP_HTML = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Crackme Repo Viewer</title>
<style>
:root {
  color-scheme: light dark;
  --bg: #111;
  --panel: #181818;
  --panel2: #202020;
  --text: #e8e8e8;
  --muted: #9c9c9c;
  --line: #333;
  --accent: #9acc14;
  --warn: #f0b94a;
}
* { box-sizing: border-box; }
body { margin: 0; background: var(--bg); color: var(--text); font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, sans-serif; }
a { color: #b7dbff; }
#app { display: grid; grid-template-columns: 360px 1fr; min-height: 100vh; }
aside { border-right: 1px solid var(--line); background: var(--panel); min-width: 0; }
header { padding: 14px; border-bottom: 1px solid var(--line); }
h1 { font-size: 16px; margin: 0 0 10px; }
.controls { display: grid; gap: 8px; }
input, select, button { width: 100%; padding: 8px 10px; border: 1px solid var(--line); border-radius: 4px; background: #0f0f0f; color: var(--text); font: inherit; }
button { cursor: pointer; background: var(--panel2); }
button:hover, .item:hover { border-color: var(--accent); }
.meta { color: var(--muted); font-size: 12px; line-height: 1.4; }
#list { height: calc(100vh - 177px); overflow: auto; padding: 8px; }
.item { display: block; width: 100%; text-align: left; border: 1px solid transparent; border-radius: 4px; padding: 8px; margin: 0 0 6px; background: transparent; color: var(--text); }
.item.active { border-color: var(--accent); background: #172006; }
.item-title { display: block; font-weight: 650; overflow-wrap: anywhere; }
.item-path { display: block; color: var(--muted); font-size: 12px; overflow-wrap: anywhere; margin-top: 2px; }
.pill { display: inline-block; margin: 5px 4px 0 0; padding: 2px 5px; border: 1px solid var(--line); border-radius: 999px; color: var(--muted); font-size: 11px; }
.pill.spoiler { color: var(--warn); border-color: #7b5b12; }
main { min-width: 0; }
#topbar { min-height: 58px; display: grid; grid-template-columns: 1fr auto; gap: 12px; align-items: center; padding: 12px 16px; border-bottom: 1px solid var(--line); background: var(--panel); position: sticky; top: 0; z-index: 2; }
#title { font-weight: 700; overflow-wrap: anywhere; }
#path { color: var(--muted); font-size: 12px; overflow-wrap: anywhere; margin-top: 3px; }
.actions { display: flex; gap: 8px; }
.actions a, .actions button { width: auto; white-space: nowrap; color: var(--text); text-decoration: none; border: 1px solid var(--line); border-radius: 4px; padding: 7px 9px; background: var(--panel2); }
#content { max-width: 980px; margin: 0 auto; padding: 24px; line-height: 1.58; }
#content.wide { max-width: none; padding: 0; }
.doc h1, .doc h2, .doc h3 { line-height: 1.25; margin-top: 1.5em; }
.doc h1:first-child, .doc h2:first-child, .doc h3:first-child { margin-top: 0; }
.doc img { max-width: 100%; height: auto; border: 1px solid var(--line); border-radius: 3px; }
.doc pre { overflow: auto; padding: 12px; background: #090909; border: 1px solid var(--line); border-radius: 4px; }
.doc code { background: #090909; padding: 1px 4px; border-radius: 3px; }
.doc pre code { padding: 0; background: transparent; }
.doc table { border-collapse: collapse; width: 100%; margin: 1em 0; }
.doc th, .doc td { border: 1px solid var(--line); padding: 7px; vertical-align: top; }
.doc blockquote { margin-left: 0; border-left: 3px solid var(--line); padding-left: 12px; color: #ccc; }
iframe { width: 100%; height: calc(100vh - 58px); border: 0; background: white; }
.preview { max-width: 100%; max-height: calc(100vh - 130px); }
.card { border: 1px solid var(--line); border-radius: 4px; padding: 14px; background: var(--panel); }
.grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 10px; }
.empty { color: var(--muted); padding: 30px; }
@media (max-width: 900px) {
  #app { grid-template-columns: 1fr; }
  aside { border-right: 0; border-bottom: 1px solid var(--line); }
  #list { height: 42vh; }
  #topbar { position: static; grid-template-columns: 1fr; }
}
</style>
</head>
<body>
<div id="app">
  <aside>
    <header>
      <h1>Crackme Repo Viewer</h1>
      <div class="controls">
        <input id="q" placeholder="search paths, titles, tags" autofocus>
        <select id="category"></select>
        <select id="kind"></select>
      </div>
      <div class="meta" id="counts"></div>
    </header>
    <div id="list"></div>
  </aside>
  <main>
    <div id="topbar">
      <div>
        <div id="title">Select a file</div>
        <div id="path"></div>
      </div>
      <div class="actions">
        <a id="raw" href="#" target="_blank" rel="noreferrer">raw</a>
        <button id="copy">copy path</button>
      </div>
    </div>
    <div id="content"><div class="empty">Use the sidebar to open Markdown, HTML, PDFs, images, source files, and binary metadata.</div></div>
  </main>
</div>
<script>
let entries = [];
let filtered = [];
let selectedPath = "";

const el = id => document.getElementById(id);

function optionList(values, label) {
  return `<option value="">${label}</option>` + values.map(v => `<option value="${escapeHtml(v)}">${escapeHtml(v)}</option>`).join("");
}

function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
}

function initFilters() {
  const categories = [...new Set(entries.map(e => e.category))].sort();
  const kinds = [...new Set(entries.map(e => e.kind))].sort();
  el("category").innerHTML = optionList(categories, "all categories");
  el("kind").innerHTML = optionList(kinds, "all kinds");
}

function applyFilters() {
  const q = el("q").value.trim().toLowerCase();
  const cat = el("category").value;
  const kind = el("kind").value;
  filtered = entries.filter(e => {
    if (cat && e.category !== cat) return false;
    if (kind && e.kind !== kind) return false;
    if (!q) return true;
    const hay = [e.path, e.title, e.kind, e.category, ...(e.tags || [])].join(" ").toLowerCase();
    return hay.includes(q);
  });
  renderList();
}

function renderList() {
  el("counts").textContent = `${filtered.length} shown / ${entries.length} total`;
  el("list").innerHTML = filtered.slice(0, 900).map(e => `
    <button class="item ${e.path === selectedPath ? "active" : ""}" data-path="${escapeHtml(e.path)}">
      <span class="item-title">${escapeHtml(e.title || e.name)}</span>
      <span class="item-path">${escapeHtml(e.path)}</span>
      <span class="pill">${escapeHtml(e.category)}</span><span class="pill">${escapeHtml(e.kind)}</span><span class="pill">${escapeHtml(e.size_human)}</span>
      ${(e.tags || []).filter(t => t !== e.kind).map(t => `<span class="pill ${t === "spoiler" ? "spoiler" : ""}">${escapeHtml(t)}</span>`).join("")}
    </button>
  `).join("") || `<div class="empty">No matches.</div>`;
}

async function openPath(path, push = true) {
  selectedPath = path;
  renderList();
  const res = await fetch(`/api/file?path=${encodeURIComponent(path)}`);
  if (!res.ok) {
    el("content").innerHTML = `<div class="empty">Could not load ${escapeHtml(path)}</div>`;
    return;
  }
  const data = await res.json();
  el("title").textContent = data.title || data.path;
  el("path").textContent = `${data.path} · ${data.kind} · ${data.size_human}`;
  el("raw").href = data.raw_url;
  let content = "";
  el("content").className = "";
  if (data.mode === "html") {
    content = `<article class="doc">${data.html}</article>`;
  } else if (data.mode === "iframe") {
    el("content").className = "wide";
    content = `<iframe sandbox src="${data.raw_url}"></iframe>`;
  } else if (data.mode === "image") {
    content = `<img class="preview" src="${data.raw_url}" alt="${escapeHtml(data.path)}">`;
  } else if (data.mode === "pdf") {
    el("content").className = "wide";
    content = `<iframe src="${data.raw_url}"></iframe>`;
  } else {
    content = `<div class="card"><h2>${escapeHtml(data.title)}</h2><div class="grid">
      <div><strong>Path</strong><br>${escapeHtml(data.path)}</div>
      <div><strong>Kind</strong><br>${escapeHtml(data.kind)}</div>
      <div><strong>Size</strong><br>${escapeHtml(data.size_human)}</div>
      <div><strong>file(1)</strong><br>${escapeHtml(data.file_info || "n/a")}</div>
    </div><p><a href="${data.raw_url}">Open raw/download</a></p></div>`;
  }
  el("content").innerHTML = content;
  if (push) history.replaceState(null, "", `#path=${encodeURIComponent(path)}`);
}

document.addEventListener("click", ev => {
  const button = ev.target.closest(".item");
  if (button) openPath(button.dataset.path);
});

["q", "category", "kind"].forEach(id => el(id).addEventListener("input", applyFilters));
el("copy").addEventListener("click", async () => {
  if (!selectedPath) return;
  await navigator.clipboard.writeText(selectedPath).catch(() => {});
});

fetch("/api/index").then(r => r.json()).then(data => {
  entries = data.entries;
  initFilters();
  applyFilters();
  const params = new URLSearchParams(location.hash.replace(/^#/, ""));
  const initial = params.get("path") || "practice/INDEX.md";
  if (entries.some(e => e.path === initial)) openPath(initial, false);
});
</script>
</body>
</html>
"""


class ViewerHandler(http.server.BaseHTTPRequestHandler):
    server_version = "RepoViewer/1.0"

    def _send(self, body: bytes, content_type: str, status: int = 200) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, payload: object, status: int = 200) -> None:
        self._send(json.dumps(payload, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8", status)

    def do_GET(self) -> None:  # noqa: N802
        parsed = urllib.parse.urlparse(self.path)
        try:
            if parsed.path == "/":
                self._send(APP_HTML.encode("utf-8"), "text/html; charset=utf-8")
                return
            if parsed.path == "/api/index":
                entries = [entry.__dict__ for entry in build_index()]
                self._json({"root": str(ROOT), "entries": entries})
                return
            if parsed.path == "/api/file":
                query = urllib.parse.parse_qs(parsed.query)
                path = safe_resolve(query.get("path", [""])[0])
                self._json(render_file(path))
                return
            if parsed.path.startswith("/raw/"):
                path = safe_resolve(parsed.path[len("/raw/") :])
                content_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
                self.send_response(200)
                self.send_header("Content-Type", content_type)
                self.send_header("Content-Length", str(path.stat().st_size))
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                with path.open("rb") as fh:
                    while chunk := fh.read(1024 * 1024):
                        self.wfile.write(chunk)
                return
        except Exception as exc:
            self._json({"error": str(exc)}, status=404)
            return
        self._json({"error": "not found"}, status=404)

    def do_HEAD(self) -> None:  # noqa: N802
        parsed = urllib.parse.urlparse(self.path)
        try:
            if parsed.path.startswith("/raw/"):
                path = safe_resolve(parsed.path[len("/raw/") :])
                content_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
                self.send_response(200)
                self.send_header("Content-Type", content_type)
                self.send_header("Content-Length", str(path.stat().st_size))
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                return
        except Exception:
            pass
        self.send_response(404)
        self.end_headers()

    def log_message(self, fmt: str, *args: object) -> None:
        sys.stderr.write("[viewer] " + fmt % args + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Serve a dead-simple local viewer for Markdown, HTML, binaries, images, and PDFs.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent(
            """\
            Examples:
              tools/repo_viewer.py
              tools/repo_viewer.py --port 8787 --no-browser
            """
        ),
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args()

    class ThreadingServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
        daemon_threads = True
        allow_reuse_address = True

    server = ThreadingServer((args.host, args.port), ViewerHandler)
    url = f"http://{args.host}:{args.port}/"
    print(f"Serving {ROOT} at {url}")
    if not args.no_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping viewer")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
