"""Single source of truth for values the generator injects into pages.

Versions, the repo URL and the vendor file list used to be hardcoded in
templates, the README and the generator separately, and they drifted.
Change them here; templates receive them as placeholders, and the
vendor check below reads VENDOR_FILES from this module.
"""

REPO_URL = "https://github.com/enonymous1/achievement-trackers"

SHELL = {
    "adminlte": "4.10.0",
    "bootstrap": "5.3.8",
    "bootstrap_icons": "1.11.3",
}

SHELL_TEXT = (
    f"AdminLTE {SHELL['adminlte']} + Bootstrap {SHELL['bootstrap']} "
    f"+ Bootstrap Icons {SHELL['bootstrap_icons']}"
)

VENDOR_FILES = (
    "bootstrap.min.css",
    "bootstrap-icons.min.css",
    "adminlte.min.css",
    "bootstrap.bundle.min.js",
    "adminlte.min.js",
)
