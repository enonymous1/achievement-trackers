#!/usr/bin/env python3
"""Syntax-check the inline <script> blocks in generated pages.

Extracts every inline script (scripts with a src are skipped) from
index.html and each <slug>/index.html, writes each block to a temp
file, and runs `node --check` on it. Exits non-zero on the first
failure, or if node is not available (CI installs it via setup-node).
"""
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


def main() -> int:
    node = shutil.which("node")
    if node is None:
        print("check_js.py: node not found in PATH", file=sys.stderr)
        return 1
    pages = [ROOT / "index.html", *sorted(ROOT.glob("*/index.html"))]
    if not pages:
        print("check_js.py: no generated pages found", file=sys.stderr)
        return 1
    failures = 0
    for page in pages:
        blocks = SCRIPT_RE.findall(page.read_text(encoding="utf-8"))
        if not blocks:
            print(f"check_js.py: WARNING no inline scripts in {page.relative_to(ROOT)}")
            continue
        for i, block in enumerate(blocks):
            if not block.strip():
                continue
            with tempfile.NamedTemporaryFile(
                "w", suffix=".js", delete=False, encoding="utf-8"
            ) as tmp:
                tmp.write(block)
                tmp_path = tmp.name
            result = subprocess.run(
                [node, "--check", tmp_path], capture_output=True, text=True
            )
            if result.returncode != 0:
                failures += 1
                print(
                    f"check_js.py: FAIL {page.relative_to(ROOT)} script {i}:\n"
                    f"{result.stderr}",
                    file=sys.stderr,
                )
    if failures:
        print(f"check_js.py: {failures} script block(s) failed node --check", file=sys.stderr)
        return 1
    print(f"check_js.py: OK ({len(pages)} page(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
