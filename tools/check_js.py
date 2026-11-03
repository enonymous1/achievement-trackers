#!/usr/bin/env python3
"""Syntax-check JavaScript in generated pages and shared JS files.

Checks every inline <script> block in index.html and each
<slug>/index.html (scripts with a src are skipped there, because they
are checked as files below), plus every file under assets/js/.
Each block/file is written to a temp file only when it comes from an
inline block, and temp files are always removed. A page with no inline
scripts is a failure, not a warning: a template edit that accidentally
deletes the tracker script must not ship silently. Exits non-zero if
any check fails, or if node is not available (CI installs it via
setup-node).
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT_RE = re.compile(
    r"<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>", re.DOTALL | re.IGNORECASE
)


def check_inline_block(node, page, index, block, failures):
    """node --check one inline script block, reporting into failures."""
    if not block.strip():
        return
    fd, tmp_path = tempfile.mkstemp(suffix=".js")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(block)
        result = subprocess.run(
            [node, "--check", tmp_path],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode != 0:
            failures.append((str(page), index, result.stderr))
    finally:
        os.unlink(tmp_path)


def check_file(node, path, failures):
    """node --check one JS file on disk."""
    result = subprocess.run(
        [node, "--check", str(path)],
        capture_output=True, text=True, timeout=30,
    )
    if result.returncode != 0:
        failures.append((str(path), None, result.stderr))


def main() -> int:
    node = shutil.which("node")
    if node is None:
        print("check_js.py: node not found in PATH", file=sys.stderr)
        return 1
    pages = [ROOT / "index.html", *sorted(ROOT.glob("*/index.html"))]
    if not pages:
        print("check_js.py: no generated pages found", file=sys.stderr)
        return 1
    failures = []
    for page in pages:
        blocks = SCRIPT_RE.findall(page.read_text(encoding="utf-8"))
        if not blocks:
            # The How page deliberately has no inline script: its
            # behaviour is the shared theme/sidebar files. Every other
            # page must have inline scripts, or a template edit that
            # deletes the tracker script would ship silently.
            if page.relative_to(ROOT).parts[0] == "how-it-works":
                continue
            failures.append((str(page.relative_to(ROOT)), None,
                             "no inline scripts found"))
            continue
        for i, block in enumerate(blocks):
            check_inline_block(node, page.relative_to(ROOT), i, block, failures)
    js_dir = ROOT / "assets" / "js"
    if js_dir.is_dir():
        for path in sorted(js_dir.glob("*.js")):
            check_file(node, path.relative_to(ROOT), failures)
    if failures:
        for page, index, stderr in failures:
            label = f"{page} script {index}" if index is not None else page
            print(f"check_js.py: FAIL {label}:\n{stderr}", file=sys.stderr)
        print(f"check_js.py: {len(failures)} failure(s)", file=sys.stderr)
        return 1
    print(f"check_js.py: OK ({len(pages)} page(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
