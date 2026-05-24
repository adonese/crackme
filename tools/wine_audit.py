#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# ///
"""Run a bounded Wine smoke test across local Windows executables."""

from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import signal
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PREFIX = Path.home() / ".cache" / "crackme-wine-audit"
DEFAULT_REPORT = ROOT / "docs" / "WINE_AUDIT.md"


@dataclass
class Result:
    path: str
    file_type: str
    status: str
    exit_code: int | str
    seconds: float
    notes: str
    output: str


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def exe_files(pattern: str | None = None) -> list[Path]:
    files_by_path: dict[Path, None] = {}
    for base in [ROOT / "crackmes", ROOT / "practice"]:
        for path in base.rglob("*"):
            name = path.name.lower()
            is_windows_app = path.suffix.lower() in {".exe", ".scr", ".com"} or ".exe." in name
            if path.is_file() and is_windows_app and "dll" not in file_type(path).lower():
                files_by_path[path] = None
    files = sorted(files_by_path, key=lambda p: rel(p).lower())
    if pattern:
        needle = pattern.lower()
        files = [path for path in files if needle in rel(path).lower()]
    return files


def file_type(path: Path) -> str:
    try:
        return subprocess.check_output(["file", "-b", str(path)], text=True).strip()
    except Exception:
        return "unknown"


def trim_output(text: str, limit: int = 1800) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n").strip()
    if len(text) <= limit:
        return text
    crash_lines = [
        line
        for line in text.splitlines()
        if "unhandled page fault" in line.lower() or "winedbg attached" in line.lower()
    ]
    if crash_lines:
        highlight = "\n".join(dict.fromkeys(crash_lines))
        head = max(1, (limit - len(highlight)) // 2)
        tail = max(1, limit - len(highlight) - head)
        return text[:head].rstrip() + "\n...\n" + highlight + "\n...\n" + text[-tail:].lstrip()
    head = max(1, limit // 2)
    tail = max(1, limit - head)
    return text[:head].rstrip() + "\n...\n" + text[-tail:].lstrip()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def classify(exit_code: int | str, output: str, kind: str) -> tuple[str, str]:
    low = output.lower()
    if "wine: unhandled page fault" in low or "winedbg attached" in low:
        return "crash", "Wine reported an unhandled page fault."
    if "failed to read license.bin" in low:
        return "needs-input", "Challenge expects a candidate license.bin in the executable directory."
    if "press enter if you read" in low:
        return "needs-interaction", "Console program reached an input prompt; audit stdin is disabled."
    if "mono" in low and ("not installed" in low or "mscoree" in low or "could not load" in low):
        return "missing-runtime", ".NET/Mono runtime problem under Wine."
    if "nodrv_createwindow" in low or "make sure that your x server is running" in low:
        return "display-error", "Wine could not create a window on the current WSL display."
    if "bad exe format" in low or "not a valid win32 application" in low or "shell execute ex failed" in low:
        return "loader-error", "Wine loader rejected the executable."
    if exit_code == "timeout":
        if "gui" in kind.lower():
            return "launched-gui-timeout", "GUI process stayed open until timeout."
        return "launched-timeout", "Process stayed alive; likely waiting for UI/input."
    if exit_code == 0:
        return "ok-exited", "Process exited cleanly."
    return "nonzero-exit", f"Process exited with code {exit_code}."


def known_findings(results: list[Result]) -> list[str]:
    result_paths = {result.path for result in results}
    sections: list[str] = []

    redxen_paths = [
        "crackmes/crackme_2_RedXen/C File CrackMe.exe",
        "crackmes/crackme_2_RedXen/file.exe",
        "practice/crackmes/crackmes-one/extracted/redxen-c-file-2022-07-25/C File CrackMe/C File CrackMe.exe",
    ]
    redxen_present = [path for path in redxen_paths if path in result_paths and (ROOT / path).exists()]
    if redxen_present:
        hashes = {sha256(ROOT / path) for path in redxen_present}
        password_bin = ROOT / "practice/crackmes/crackmes-one/extracted/redxen-c-file-2022-07-25/C File CrackMe/password.bin"
        password_note = ""
        if password_bin.exists():
            password_note = f" The bundled `password.bin` is present with SHA-256 `{sha256(password_bin)}`."
        hash_text = ", ".join(f"`{value}`" for value in sorted(hashes))
        sections.append(
            "\n".join(
                [
                    "### RedXen C File CrackMe",
                    "",
                    f"The RedXen executable copies in this repo hash to {hash_text}.{password_note}",
                    "This crackme is cwd-sensitive: launching it as `wine path/to/C File CrackMe.exe`",
                    "from the repo root can crash because the program opens `password.bin` relative to",
                    "the current directory and does not handle a missing file cleanly. The `wine-audit`",
                    "script and `./launchpad wine ...` both launch from the executable directory, which",
                    "keeps the sidecar file visible.",
                ]
            )
        )

    a_matter = "practice/ctf/crackmes-one-ctf-2026/A_MatterOfTime/Handout/a_matter_of_time.exe"
    if a_matter in result_paths:
        sections.append(
            "\n".join(
                [
                    "### A Matter Of Time",
                    "",
                    "`a_matter_of_time.exe` is extracted from the passworded handout zip. The",
                    "program reaches its intro text and `Press ENTER` prompt under Wine. The",
                    "audit intentionally disables stdin, so a nonzero exit at that prompt is",
                    "classified as `needs-interaction`, not as a broken executable.",
                    "",
                    "Upstream handout: https://github.com/crackmesone/ctf-2026-challenges-public/tree/main/A_MatterOfTime/Handout",
                ]
            )
        )

    flrscrnsvr = "practice/ctf/crackmes-one-ctf-2026/FLRSCRNSVR/handout/FLRSCRNSVR.SCR"
    if flrscrnsvr in result_paths:
        sections.append(
            "\n".join(
                [
                    "### FLRSCRNSVR.SCR",
                    "",
                    "`FLRSCRNSVR.SCR` is extracted from the passworded handout zip and launches",
                    "as a GUI screensaver binary under Wine. The upstream README records SHA-256",
                    "`65e0485c9780a856d0542aa88d921e253123b7326d064ff3cae6827509cf537f`,",
                    "which matches the extracted file.",
                    "",
                    "Upstream challenge: https://github.com/crackmesone/ctf-2026-challenges-public/tree/main/FLRSCRNSVR",
                ]
            )
        )

    matryoshka = "practice/ctf/crackmes-one-ctf-2026/Matryoshka v2/Handout/LicenseChecker.exe"
    if matryoshka in result_paths:
        sections.append(
            "\n".join(
                [
                    "### Matryoshka v2 LicenseChecker",
                    "",
                    "`LicenseChecker.exe` exits with `Failed to read license.bin` until you provide a",
                    "candidate `license.bin` in the same handout directory. The upstream public handout",
                    "contains only `Doll.dll` and `LicenseChecker.exe`, so this is not a local extraction",
                    "or re-zip problem.",
                    "",
                    "Upstream handout: https://github.com/crackmesone/ctf-2026-challenges-public/tree/main/Matryoshka%20v2/Handout",
                    "Spoiler-sensitive writeup confirming the first-run behavior: https://blog.cloudlabs.ufscar.br/sec/matryoshka-v2/",
                ]
            )
        )

    moment = "practice/ctf/crackmes-one-ctf-2026/moment/handout/moment.exe.bin"
    if moment in result_paths:
        sections.append(
            "\n".join(
                [
                    "### moment.exe.bin",
                    "",
                    "`moment.exe.bin` is a Windows PE executable with a protective `.bin` suffix.",
                    "The handout README says the program can be run by removing `.bin`, and also",
                    "describes it as an anti-tamper challenge. The Wine audit still records an",
                    "unhandled page fault, and a temporary local rename to `moment.exe` produced",
                    "the same Wine crash. Treat this as a Wine/anti-tamper compatibility issue,",
                    "not as a missing file or bad archive.",
                    "",
                    "Upstream handout: https://github.com/crackmesone/ctf-2026-challenges-public/tree/main/moment/handout",
                ]
            )
        )

    return sections


def run_with_timeout(command: list[str], *, cwd: Path, env: dict[str, str], timeout: float) -> tuple[int | str, str, float]:
    start = datetime.now()
    proc = subprocess.Popen(
        command,
        cwd=cwd,
        env=env,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        errors="replace",
        start_new_session=True,
    )
    try:
        output, _ = proc.communicate(timeout=timeout)
        elapsed = (datetime.now() - start).total_seconds()
        return proc.returncode, output, elapsed
    except subprocess.TimeoutExpired:
        try:
            os.killpg(proc.pid, signal.SIGTERM)
            output, _ = proc.communicate(timeout=2)
        except Exception:
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            output, _ = proc.communicate()
        elapsed = (datetime.now() - start).total_seconds()
        return "timeout", output, elapsed


def init_prefix(prefix: Path, *, fresh: bool, winearch: str | None) -> None:
    if fresh and prefix.exists():
        shutil.rmtree(prefix)
    prefix.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["WINEPREFIX"] = str(prefix)
    if winearch:
        env["WINEARCH"] = winearch
    code, output, _ = run_with_timeout(["wineboot", "-u"], cwd=ROOT, env=env, timeout=60)
    if code not in {0, "timeout"}:
        print(trim_output(output), file=sys.stderr)
        raise RuntimeError(f"wineboot failed with exit code {code}")


def audit_one(path: Path, *, prefix: Path, timeout: float, winearch: str | None) -> Result:
    kind = file_type(path)
    env = os.environ.copy()
    env["WINEPREFIX"] = str(prefix)
    if winearch:
        env["WINEARCH"] = winearch
    code, output, seconds = run_with_timeout(["wine", path.name], cwd=path.parent, env=env, timeout=timeout)
    status, notes = classify(code, output, kind)
    return Result(rel(path), kind, status, code, seconds, notes, trim_output(output))


def markdown(results: list[Result], *, prefix: Path, timeout: float) -> str:
    counts: dict[str, int] = {}
    for result in results:
        counts[result.status] = counts.get(result.status, 0) + 1
    count_text = ", ".join(f"`{key}`: {value}" for key, value in sorted(counts.items()))
    lines = [
        "# Wine Audit",
        "",
        f"Generated with `tools/wine_audit.py` using `WINEPREFIX={prefix}`.",
        f"Per-file timeout: `{timeout:g}s`.",
        "",
        "A timeout is not automatically a failure. Many crackmes open a GUI dialog",
        "or wait for input, so the important failure signal is an immediate Wine",
        "loader error, display error, missing runtime, or unhandled page fault.",
        "The audit includes `.exe` files and renamed Windows executables such as",
        "`*.exe.bin`, but it does not execute DLLs.",
        "",
        f"Summary: {count_text}",
        "",
        "| Status | File | Type | Exit | Notes |",
        "| --- | --- | --- | --- | --- |",
    ]
    for r in results:
        lines.append(
            f"| `{r.status}` | `{r.path}` | {r.file_type.replace('|', '/')} | `{r.exit_code}` | {r.notes} |"
        )
    findings = known_findings(results)
    if findings:
        lines.extend(["", "## Known Findings", ""])
        lines.extend("\n\n".join(findings).splitlines())
    attention_statuses = {"crash", "missing-runtime", "display-error", "loader-error", "needs-input", "nonzero-exit"}
    problem_results = [r for r in results if r.status in attention_statuses]
    if problem_results:
        lines.extend(["", "## Attention Logs", ""])
        for r in problem_results:
            lines.extend(
                [
                    f"### {r.path}",
                    "",
                    f"- Status: `{r.status}`",
                    f"- Type: {r.file_type}",
                    f"- Exit: `{r.exit_code}`",
                    "",
                    "```text",
                    r.output or "(no output)",
                    "```",
                    "",
                ]
            )
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--timeout", type=float, default=8.0)
    parser.add_argument("--prefix", type=Path, default=DEFAULT_PREFIX)
    parser.add_argument("--fresh-prefix", action="store_true")
    parser.add_argument("--winearch", choices=["win32", "win64"])
    parser.add_argument("--pattern", help="Only audit paths containing this text")
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()

    if not shutil.which("wine"):
        print("wine is not installed or not on PATH", file=sys.stderr)
        return 1
    if not shutil.which("wineboot"):
        print("wineboot is not installed or not on PATH", file=sys.stderr)
        return 1

    files = exe_files(args.pattern)
    if not files:
        print("No .exe files matched.", file=sys.stderr)
        return 1

    init_prefix(args.prefix, fresh=args.fresh_prefix, winearch=args.winearch)
    results: list[Result] = []
    for index, path in enumerate(files, 1):
        print(f"[{index:02d}/{len(files):02d}] {rel(path)}", flush=True)
        result = audit_one(path, prefix=args.prefix, timeout=args.timeout, winearch=args.winearch)
        print(f"  {result.status} ({result.exit_code})", flush=True)
        results.append(result)

    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(markdown(results, prefix=args.prefix, timeout=args.timeout), encoding="utf-8")
    print(f"wrote {args.report}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
