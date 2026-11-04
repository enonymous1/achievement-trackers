#!/usr/bin/env python3
"""Generate achievement-tracker pages from data/*.json.

Source of truth is the JSON, not the HTML. The generator:
  * validates every game (Gamerscore sum, unique ids, counter groups,
    non-empty requirement/route text, declared sources),
  * renders one index.html per game from tools/template.html, using the
    shared vendored shell under assets/vendor/ (so a game page is not
    portable on its own — the repo is the distribution unit),
  * renders the hub index.html from the same data, with per-game progress
    read from localStorage on the hub page itself.

Usage, from the repo root:
    python3 tools/generate.py            # write all outputs
    python3 tools/generate.py --check    # exit 1 if any output would change
    python3 tools/generate.py --game minecraft-dungeons

Note on --game: it regenerates the hub plus one game page only, leaving
other game pages untouched. Always run the full generator before
committing; --game is a preview shortcut, not a commit step.

Adding a game: copy data/minecraft-dungeons.json to data/<slug>.json,
fill it in (see that file for the schema), run the generator, preview
with `python3 -m http.server 8000`, then commit the JSON *and* the
generated HTML. Never hand-edit a generated page — edit the JSON and
regenerate, or the next run will overwrite your edit (and --check
exists to catch exactly that drift in CI).
"""

import argparse
import copy
import html
import json
import re
import sys
from pathlib import Path

from config import REPO_URL, SHELL_TEXT, VENDOR_FILES

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
TOOLS_DIR = ROOT / "tools"

# Short filter labels for section ids. These are a fallback only: a
# section may carry its own "filter_label" in the JSON, and that wins.
# New section types should get a filter_label in data, not a new entry
# here — adding a game is supposed to be data-only.
FILTER_LABELS = {
    "story": "First run",
    "steps": "Secrets & runes",
    "replay": "Replays & mop-up",
    "jungle": "Jungle",
    "winter": "Creeping Winter",
}


def _is_positive_int(value):
    # type(value) is int, not isinstance: bool is a subclass of int in
    # Python, so isinstance(True, int) is True and "gs": true would
    # otherwise sum as 1G and pass validation.
    return type(value) is int and value > 0


def fail(message):
    print(f"generate: error: {message}", file=sys.stderr)
    raise SystemExit(1)


def load_games():
    """Load and validate every game JSON, in filename order.

    data/schema.json is the human-readable schema, not a game, so it
    is skipped here — otherwise it would be validated as a game and
    fail for missing game fields.
    """
    files = [p for p in sorted(DATA_DIR.glob("*.json"))
             if p.name != "schema.json"]
    if not files:
        fail("no data/*.json files found")
    games = []
    for path in files:
        try:
            game = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            fail(f"{path.name}: invalid JSON: {exc}")
        except OSError as exc:
            fail(f"{path.name}: cannot be read: {exc}")
        validate_game(path.name, game)
        games.append(game)
    return games


def validate_game(filename, game):
    """Validate one game dict, failing loudly on the first problem.

    Shape is checked before indexing: a malformed file must produce a
    one-line ``generate: error:`` message, not a KeyError traceback.
    On success the computed totals are stored on the dict under
    underscore-prefixed keys, so renderers never recompute them from
    the declared (possibly wrong) totals.
    """
    def check(condition, message):
        if not condition:
            fail(f"{filename}: {message}")

    def check_media_entry(entry, ach_id):
        """Shared shape checks for media and slideshow entries:
        a usable src, an optional full of the same shape, and
        string alt/caption/credit when present."""
        check(isinstance(entry, dict)
              and isinstance(entry.get("src"), str) and entry["src"],
              f"{ach_id}: bad media entry {entry!r}")
        for key in ("src", "full"):
            if entry.get(key):
                check(isinstance(entry[key], str)
                      and (entry[key].startswith("assets/")
                           or entry[key].startswith("https://")),
                      f"{ach_id}: bad media {key} {entry[key]!r}")
        for field in ("alt", "caption", "credit"):
            check(field not in entry or isinstance(entry[field], str),
                  f"{ach_id}: media {field} must be a string")

    check(isinstance(game, dict),
          f"top level must be a JSON object, not {type(game).__name__}")
    for field in ("slug", "title", "tagline", "order_note", "scope_note",
                  "storage_key", "sections", "sources"):
        check(game.get(field), f"missing/empty field {field!r}")
    check(game["slug"] == Path(filename).stem,
          f"slug {game['slug']!r} does not match filename {filename!r}")
    check(re.fullmatch(r"[a-z0-9][a-z0-9-]*", game["slug"]),
          f"slug {game['slug']!r} is not URL-safe")
    check(isinstance(game["sources"], list) and game["sources"],
          "sources must list at least one source")
    for source in game["sources"]:
        check(isinstance(source, dict)
              and source.get("label")
              and source.get("url", "").startswith("https://"),
              f"bad source entry: {source!r}")

    task_ids, step_ids, xbox_ids = set(), set(), set()
    achievements, total_gs = [], 0
    # Xbox sync is opt-in per game: a game with xbox_title_id must map
    # every achievement, and a game without it must map none. A partial
    # mapping would silently leave some achievements unsyncable, so it
    # fails here instead of shipping.
    has_xbox = "xbox_title_id" in game
    if has_xbox:
        check(isinstance(game["xbox_title_id"], str)
              and re.fullmatch(r"[0-9]+", game["xbox_title_id"]),
              "xbox_title_id must be a string of digits")
    for section in game["sections"]:
        check(isinstance(section, dict)
              and section.get("id") and section.get("title"),
              f"section missing id/title: {section!r}")
        if "filter_label" not in section:
            # Warning, not failure: existing files predate filter_label
            # and fall back to FILTER_LABELS, but new sections should
            # carry their own label so adding a game stays data-only.
            print(f"{filename}: section {section['id']!r} has no "
                  f"filter_label; add one to the JSON", file=sys.stderr)
        for ach in section.get("achievements", []):
            check(isinstance(ach, dict) and ach.get("id"),
                  f"achievement missing 'id': {ach!r}")
            achievements.append(ach)
            check(ach["id"] not in task_ids, f"duplicate achievement id {ach['id']!r}")
            task_ids.add(ach["id"])
            check(_is_positive_int(ach.get("gs")),
                  f"{ach['id']}: gs must be a positive integer")
            xid = ach.get("xbox_id")
            if has_xbox:
                check(isinstance(xid, str) and xid,
                      f"{ach['id']}: missing xbox_id for a synced game")
                check(xid not in xbox_ids,
                      f"duplicate xbox_id {xid!r}")
                xbox_ids.add(xid)
            else:
                check(not xid,
                      f"{ach['id']}: xbox_id without xbox_title_id")
            total_gs += ach["gs"]
            for field in ("name", "req", "how"):
                check(ach.get(field), f"{ach['id']}: missing/empty {field!r}")
            for step in ach.get("steps", []):
                check(isinstance(step, dict) and step.get("id"),
                      f"{ach['id']}: step missing 'id': {step!r}")
                check(step["id"] not in step_ids, f"duplicate step id {step['id']!r}")
                step_ids.add(step["id"])
                check(step.get("label"), f"{ach['id']}: step missing label")
            for counter in ach.get("counters", []):
                # Counter groups deliberately allow different targets
                # per achievement: one shared value (e.g. mobs defeated)
                # feeds several thresholds (50 and 2,500). The JS syncs
                # the value across inputs in the group and computes each
                # bar against its own target, so do NOT add a
                # "targets must match" check here.
                check(isinstance(counter, dict)
                      and counter.get("group")
                      and _is_positive_int(counter.get("target")),
                      f"{ach['id']}: bad counter {counter!r}")
            if "missable" in ach:
                check(isinstance(ach["missable"], bool),
                      f"{ach['id']}: missable must be true/false, not {ach['missable']!r}")
            for entry in ach.get("media", []):
                check(isinstance(entry, dict)
                      and entry.get("type") in ("image", "video"),
                      f"{ach['id']}: bad media entry {entry!r}")
                check_media_entry(entry, ach["id"])
                if entry["type"] == "video" and entry["src"].startswith("https://"):
                    check(entry["src"].lower().endswith((".mp4", ".webm", ".ogg"))
                          or _youtube_id(entry["src"]),
                          f"{ach['id']}: bad remote video {entry['src']!r}")
            slides = ach.get("slideshow", [])
            check(isinstance(slides, list),
                  f"{ach['id']}: slideshow must be a list")
            for entry in slides:
                check_media_entry(entry, ach["id"])
        for card in section.get("step_cards", []):
            check(isinstance(card, dict)
                  and card.get("title") and card.get("how") and card.get("steps"),
                  f"step card missing title/how/steps: {card!r}")
            for step in card["steps"]:
                check(isinstance(step, dict) and step.get("id"),
                      f"step card step missing 'id': {step!r}")
                check(step["id"] not in step_ids, f"duplicate step id {step['id']!r}")
                step_ids.add(step["id"])
                check(step.get("label"), f"step card step missing label: {step!r}")
        check(section.get("achievements") or section.get("step_cards"),
              f"section {section['id']!r} has neither achievements nor step cards")

    check(game.get("total_gs") == total_gs,
          f"declared total_gs {game.get('total_gs')!r} does not match "
          f"sum of achievement Gamerscore ({total_gs})")
    check(game.get("total_count") == len(achievements),
          f"declared total_count {game.get('total_count')!r} does not match "
          f"achievement count ({len(achievements)})")
    game["_achievements"] = achievements
    game["_total_gs"] = total_gs
    game["_total_count"] = len(achievements)
    # The hub and the header show the declared scope; the generator's
    # own total is the check, so a typo in a single GS value fails here
    # instead of silently shipping a wrong progress bar.
    return game


def esc(text):
    """Escape a value for interpolation into HTML text or an attribute."""
    return html.escape(str(text), quote=True)


_FRAGMENTS = {}


def _fragment(name):
    """Load a card fragment, cached; card markup lives in HTML, not Python."""
    if name not in _FRAGMENTS:
        path = TOOLS_DIR / "fragments" / f"{name}.html"
        if not path.exists():
            fail(f"missing fragment: tools/fragments/{name}.html")
        _FRAGMENTS[name] = path.read_text(encoding="utf-8").strip()
    return _FRAGMENTS[name]


def _fill(template, replacements):
    """Fill @@PLACEHOLDER@@ values in a single pass.

    Single-pass matters: values are inserted verbatim and are never
    re-scanned, so a value that happens to look like a placeholder
    (e.g. a route note mentioning @@TITLE@@) cannot be substituted a
    second time. A placeholder with no value is a hard failure, not a
    silently shipped "@@...@@" string.
    """
    def sub(match):
        key = match.group(1)
        if key not in replacements:
            fail(f"template placeholder @@{key}@@ has no value")
        return replacements[key]

    return re.sub(r"@@([A-Z_]+)@@", sub, template)


def render_counter(counter):
    """Render one shared-counter input for an achievement card."""
    return _fill(_fragment("counter"), {
        "GROUP": esc(counter["group"]),
        "TARGET": str(int(counter["target"])),
    })


def render_counter_bar(counter):
    """Render the progress bar for one counter, placed under the header.

    The bar lives outside the card body, directly under the header, so
    progress is visible without scrolling the card. It is matched to
    its input by both group and target in the tracker JS, because a
    shared group can have different targets per achievement.
    """
    return _fill(_fragment("counter_bar"), {
        "GROUP": esc(counter["group"]),
        "TARGET": str(int(counter["target"])),
    })


def render_steps(steps, parent_id=None):
    """Render step checkboxes; steps with a parent auto-tick it in JS."""
    if not steps:
        return ""
    items = []
    for step in steps:
        parent = f' data-parent="{esc(parent_id)}"' if parent_id else ""
        items.append(
            f'<label><input type="checkbox" class="step" id="{esc(step["id"])}"'
            f"{parent}> {esc(step['label'])}</label>"
        )
    return '<div class="steps">' + "".join(items) + "</div>"


def render_step_bar(ach):
    """Progress bar for a multi-step achievement, under its header.

    Only achievements with two or more sub-steps get one: a single
    step's bar would just mirror the achievement's own tick. Step
    cards get none — they are not achievements, and their steps
    carry no parent id to count against.
    """
    steps = ach.get("steps", [])
    if len(steps) < 2:
        return ""
    return _fill(_fragment("step_bar"), {"PARENT": esc(ach["id"])})


def _youtube_id(src):
    """YouTube video id from a watch or youtu.be URL, else None."""
    from urllib.parse import urlparse, parse_qs

    try:
        u = urlparse(src)
    except ValueError:
        return None
    if u.netloc in ("www.youtube.com", "youtube.com", "m.youtube.com"):
        vid = parse_qs(u.query).get("v", [None])[0]
        return vid or None
    if u.netloc == "youtu.be":
        return u.path.strip("/") or None
    return None


def _media_src(src):
    """Page-relative URL for a media src: repo files live under
    assets/ (one level up from a game page); remote URLs pass
    through unchanged."""
    if src.startswith("assets/"):
        return "../" + src
    return src


def render_media(ach):
    """Media block for one achievement card, under the route note.

    Images render as <img> (lazy); clips render as <video> when the
    src is a media file, or as a privacy-enhanced YouTube embed
    when it is a YouTube URL. Anything else is rejected by
    validate_game, so this never has to guess.
    """
    parts = []
    for entry in ach.get("media", []):
        src = entry["src"]
        if entry["type"] == "image":
            alt = esc(entry.get("alt") or ach["name"])
            img = (f'<img src="{esc(_media_src(src))}" alt="{alt}"'
                   f' loading="lazy" class="img-fluid rounded">')
            if entry.get("full"):
                img = (f'<a href="{esc(_media_src(entry["full"]))}" target="_blank" '
                       f'rel="noopener" title="Open larger version">{img}</a>')
            fig = img
            cap = []
            if entry.get("caption"):
                cap.append(esc(entry["caption"]))
            if entry.get("credit"):
                cap.append(f'Image: {esc(entry["credit"])}')
            if cap:
                fig += f'<figcaption class="figure-caption">{" ".join(cap)}</figcaption>'
            parts.append(f'<figure class="ach-media mt-2 mb-0">{fig}</figure>')
        else:
            if src.lower().endswith((".mp4", ".webm", ".ogg")):
                parts.append(
                    f'<video controls preload="none" class="ach-media w-100 rounded mt-2">'
                    f'<source src="{esc(_media_src(src))}"></video>'
                )
            else:
                vid = _youtube_id(src)
                parts.append(
                    f'<div class="ach-media ratio ratio-16x9 mt-2"><iframe '
                    f'src="https://www.youtube-nocookie.com/embed/{esc(vid)}" '
                    f'title="{esc(ach["name"])}" loading="lazy" allowfullscreen></iframe></div>'
                )
    return "".join(parts)


def render_slideshow(ach):
    """Step-by-step guide block for one achievement card: one
    slide at a time, walked with Previous/Next. Slides reuse
    the media entry shape (src, optional full, caption, credit,
    alt); slide images open in the same viewer as media images.
    """
    slides = ach.get("slideshow", [])
    if not slides:
        return ""
    parts = []
    for i, entry in enumerate(slides):
        img = (f'<img src="{esc(_media_src(entry["src"]))}" '
               f'alt="{esc(entry.get("alt") or ach["name"])}" '
               f'loading="lazy" class="img-fluid rounded">')
        if entry.get("full"):
            img = (f'<a href="{esc(_media_src(entry["full"]))}" target="_blank" '
                   f'rel="noopener" title="Open larger version">{img}</a>')
        cap = []
        if entry.get("caption"):
            cap.append(esc(entry["caption"]))
        if entry.get("credit"):
            cap.append(f'Image: {esc(entry["credit"])}')
        figcap = (f'<figcaption class="figure-caption">{" ".join(cap)}</figcaption>'
                  if cap else "")
        active = " active" if i == 0 else ""
        parts.append(f'<figure class="slideshow-slide{active}">{img}{figcap}</figure>')
    controls = (
        '<div class="slideshow-controls">'
        '<button type="button" class="slideshow-prev btn btn-outline-success btn-sm">'
        '← Previous</button>'
        f'<span class="slideshow-count text-secondary">1 of {len(slides)}</span>'
        '<button type="button" class="slideshow-next btn btn-outline-success btn-sm">'
        'Next →</button></div>'
    )
    return (f'<div class="slideshow mt-2"><div class="slideshow-slides">'
            f'{"".join(parts)}</div>{controls}</div>')


def render_achievement(ach, number, wrap=True):
    """Render one achievement card.

    ``number`` is the running 1-based position in typical unlock order
    across all sections, not the position within this section. Steps
    carry ``data-parent`` so the tracker JS can auto-tick the
    achievement when every step is ticked; counters are rendered once
    per achievement that uses them, and the JS syncs all inputs that
    share a ``data-counter`` group to one value. The fragment itself
    is just the article; the grid-column wrapper lives here, and
    ``wrap=False`` returns the bare article for the How page demos,
    which supply their own caption + column wrapper.
    """
    counters = "".join(render_counter(c) for c in ach.get("counters", []))
    counter_bars = "".join(render_counter_bar(c) for c in ach.get("counters", []))
    step_bar = render_step_bar(ach)
    missable = (
        '<span class="badge text-bg-danger-subtle text-danger-emphasis '
        'border border-danger-subtle ms-2" '
        'title="Missable: can be passed without popping">Missable</span>'
        if ach.get("missable") else ""
    )
    article = _fill(_fragment("achievement"), {
        "ID": esc(ach["id"]),
        "GS": str(ach["gs"]),
        "NUMBER": str(number),
        "NAME": esc(ach["name"]),
        "REQ": esc(ach["req"]),
        "HOW": esc(ach["how"]),
        "MISSABLE": missable,
        "MEDIA": render_media(ach),
        "SLIDESHOW": render_slideshow(ach),
        "STEPS": render_steps(ach.get("steps", []), parent_id=ach["id"]),
        "COUNTERS": counters,
        "COUNTER_BARS": counter_bars,
        "STEP_BAR": step_bar,
    })
    if not wrap:
        return article
    data_name = esc(f"{ach['name']} {ach['req']} {ach['how']}")
    return (f'<div class="item col-12 col-md-6 col-xl-4" '
            f'data-name="{data_name}">{article}</div>')


def render_step_card(card, wrap=True):
    """Render a walkthrough step card (not an achievement itself).

    ``wrap`` works as in render_achievement: the tracker grid gets
    the column wrapper, the How page demos get the bare article.
    """
    article = _fill(_fragment("step_card"), {
        "TITLE": esc(card["title"]),
        "HOW": esc(card["how"]),
        "STEPS": render_steps(card["steps"]),
    })
    if not wrap:
        return article
    data_name = esc(f"{card['title']} {card['how']}")
    return (f'<div class="item col-12 col-md-6 col-xl-4" '
            f'data-name="{data_name}">{article}</div>')


def render_sections(game):
    """Render all sections, in JSON order.

    Only the first section is open by default. That is a UX choice,
    not an accident: the first run is where a new player starts, and
    collapsed later sections keep the page scannable. Section titles
    are escaped like every other data value — titles come from data,
    not code, so a title containing ``&`` or ``<`` must not break the
    page or inject markup.
    """
    number = 0
    out = []
    for index, section in enumerate(game["sections"]):
        achievements = section.get("achievements", [])
        cards = section.get("step_cards", [])
        open_attr = " open" if index == 0 else ""
        title = esc(section["title"])
        if achievements:
            sec_gs = sum(a["gs"] for a in achievements)
            subtitle = f"{len(achievements)} achievements, {sec_gs}G"
            if section.get("subtitle"):
                subtitle = section["subtitle"]
            section_id = esc(section["id"])
            summary = (f'{title} <small>{esc(subtitle)} · '
                       f'<span class="sec-progress" '
                       f'data-section="{section_id}"></span></small>')
        else:
            summary = (f'{title} <small>{esc(section.get("subtitle", ""))}</small>'
                       if section.get("subtitle") else title)
        out.append(f'<details{open_attr} data-cat="{esc(section["id"])}">')
        out.append(f"<summary>{summary}</summary>")
        out.append('<div class="section-body">')
        if section.get("intro"):
            out.append(f'<p class="text-secondary">{esc(section["intro"])}</p>')
        out.append('<div class="row g-3">')
        for ach in achievements:
            number += 1
            out.append(render_achievement(ach, number))
        for card in cards:
            out.append(render_step_card(card))
        out.append("</div></div></details>")
    return "\n".join(out)


def render_xbox_sync_card(game):
    """Sync card for games with an Xbox mapping, else nothing.

    The card carries the title id and the xbox_id -> achievement id
    map as data attributes (not a JSON <script> block: check_js.py
    syntax-checks every inline script without src, and a JSON object
    literal is not valid JS at statement position). Games without a
    mapping get no card, so the sync script in the template stays a
    no-op for them.
    """
    if "xbox_title_id" not in game:
        return ""
    mapping = {a["xbox_id"]: a["id"] for a in game["_achievements"]}
    return _fill(_fragment("xbox_sync"), {
        "TITLE_ID": esc(game["xbox_title_id"]),
        "XBOX_MAP_JSON": esc(json.dumps(mapping, sort_keys=True)),
    })



def sidebar_menu(all_games, prefix, current):
    """Sidebar menu items: Home, a Games header, then the games flat
    under it (no dropdown — the list is short for now, and the user
    expects to revisit this when it grows).
    ``current`` is 'home', 'how', or a game slug. ``prefix`` is the
    relative path back to the site root from the page using it."""
    items = []
    home_active = ' active' if current == 'home' else ''
    items.append(
        f'              <li class="nav-item"><a href="{prefix}" '
        f'class="nav-link{home_active}"><i class="nav-icon bi bi-house"></i>'
        f'<p>Home</p></a></li>'
    )
    items.append('              <li class="nav-header">Games</li>')
    for game in all_games:
        active = ' active' if game["slug"] == current else ""
        items.append(
            f'              <li class="nav-item"><a href="{prefix}{esc(game["slug"])}/" '
            f'class="nav-link{active}"><i class="nav-icon bi bi-controller"></i>'
            f'<p>{esc(game["title"])}</p></a></li>'
        )
    return "\n".join(items)


def sidebar_how_href(prefix, current):
    """Href for the bottom-anchored How link: the How page links to
    itself with './', every other page with its root prefix."""
    return "./" if current == "how" else f"{prefix}how-it-works/"


def render_game(game, all_games):
    """Render one game page from template.html plus its fragments."""
    template = (TOOLS_DIR / "template.html").read_text(encoding="utf-8")
    filters = []
    for section in game["sections"]:
        label = (section.get("filter_label")
                 or FILTER_LABELS.get(section["id"]))
        if not label:
            label = section["title"].split("·")[0].strip() or section["id"]
        filters.append(
            f'      <button type="button" class="filter '
            f'btn btn-outline-success" data-filter="{esc(section["id"])}">'
            f"{esc(label)}</button>"
        )
    sources = " · ".join(
        f'<a href="{esc(s["url"])}">{esc(s["label"])}</a>' for s in game["sources"]
    )
    replacements = {
        "ASSET_PREFIX": "../assets/",
        "SIDEBAR_MENU": sidebar_menu(all_games, "../", game["slug"]),
        "SIDEBAR_PREFIX": "../",
        "HOW_HREF": sidebar_how_href("../", game["slug"]),
        "HOW_ACTIVE": "",
        "TITLE": esc(game["title"]),
        "TAGLINE": esc(game["tagline"]),
        "ORDER_NOTE": esc(game["order_note"]),
        "SCOPE_NOTE": esc(game["scope_note"]),
        "SLUG": esc(game["slug"]),
        "STORAGE_KEY": esc(game["storage_key"]),
        "LEGACY_KEY": esc(game.get("legacy_key", "")),
        "LEGACY_MIGRATION_JSON": json.dumps(game.get("legacy_migration") or {}),
        "TOTAL_GS": str(game["_total_gs"]),
        "TOTAL_COUNT": str(game["_total_count"]),
        "FILTER_BUTTONS": "\n".join(filters),
        "XBOX_SYNC_CARD": render_xbox_sync_card(game),
        "SECTIONS_HTML": render_sections(game),
        "SOURCES_HTML": sources,
        "SHELL_TEXT": SHELL_TEXT,
    }
    for key in replacements:
        if f"@@{key}@@" not in template:
            fail(f"template.html is missing placeholder @@{key}@@")
    out = _fill(template, replacements)
    if re.search(r'(?:src|href)="/', out):
        fail(f"{game['slug']}: absolute path found in generated page")
    return out


def render_hub(games):
    template = (TOOLS_DIR / "hub_template.html").read_text(encoding="utf-8")
    cards = []
    hub_data = []
    for game in games:
        total_gs, total_count = game["_total_gs"], game["_total_count"]
        hub_data.append({
            "slug": game["slug"],
            "title": game["title"],
            "storage_key": game["storage_key"],
            "achievements": [
                {"id": a["id"], "gs": a["gs"]} for a in game["_achievements"]
            ],
        })
        slug = esc(game["slug"])
        cards.append(
            f'<div class="game item col-12 col-md-6" '
            f'data-name="{esc(game["title"])}">'
            f'<div class="card h-100">'
            f'<div class="card-header"><h3 class="fs-5 mb-0">'
            f'<a href="{slug}/">{esc(game["title"])}</a></h3></div>'
            f'<div class="card-body">'
            f'<p class="text-secondary">{esc(game["scope_note"])}</p>'
            f'<p><strong>{total_count} achievements · {total_gs:,}G</strong> · '
            f'<span class="game-progress" data-slug="{slug}">'
            f'Not started yet</span></p>'
            f'<p class="mb-0"><a class="btn btn-success" '
            f'href="{slug}/">Open tracker →</a></p>'
            f'</div></div></div>'
        )
    total_games = len(games)
    total_count = sum(g["_total_count"] for g in games)
    total_gs = sum(g["_total_gs"] for g in games)
    game_word = "game" if total_games == 1 else "games"
    replacements = {
        "ASSET_PREFIX": "./assets/",
        "SIDEBAR_MENU": sidebar_menu(games, "./", "home"),
        "SIDEBAR_PREFIX": "./",
        "HOW_HREF": sidebar_how_href("./", "home"),
        "HOW_ACTIVE": "",
        "GAMES_CARDS": chr(10).join(cards),
        "HUB_DATA": json.dumps(hub_data),
        "FOOTER_TOTALS": (
            f"{total_games} {game_word} · {total_count} achievements · "
            f"{total_gs:,}G"
        ),
        "REPO_URL": REPO_URL,
    }
    for key in replacements:
        if f"@@{key}@@" not in template:
            fail(f"hub_template.html is missing placeholder @@{key}@@")
    return _fill(template, replacements)


def _demo_copy_achievement(ach):
    """Deep copy of an achievement with demo-prefixed ids, so demo
    cards on the How page can never collide with real tracker ids
    or be mistaken for saved progress."""
    demo = copy.deepcopy(ach)
    demo["id"] = f"demo-{ach['id']}"
    for step in demo.get("steps", []):
        step["id"] = f"demo-{step['id']}"
    return demo


def _demo_copy_step_card(card):
    demo = copy.deepcopy(card)
    for step in demo.get("steps", []):
        step["id"] = f"demo-{step['id']}"
    return demo


def _find_achievement(game, ach_id):
    number = 0
    for section in game["sections"]:
        for ach in section.get("achievements", []):
            number += 1
            if ach["id"] == ach_id:
                return ach, number
    return None, None


def render_demos(all_games):
    """Live demo cards for the How page, rendered from the real
    game data through the same fragments as the tracker itself.
    Failing loudly if a game (or a demo card) is gone keeps the
    How page from shipping empty demo slots. Demo cards have
    their note buttons stripped: the How page has no notes
    modal, so a demo note button would do nothing."""
    dungeons = next(
        (g for g in all_games if g["slug"] == "minecraft-dungeons"), None
    )
    if dungeons is None:
        fail("How page demos need the minecraft-dungeons game")
    grove = next(
        (g for g in all_games if g["slug"] == "great-god-grove"), None
    )
    if grove is None:
        fail("How page demos need the great-god-grove game")

    demos = []

    def demo_ach(ach_id, caption, game=None):
        ach, number = _find_achievement(game or dungeons, ach_id)
        if ach is None:
            fail(f"How page demo achievement missing: {ach_id}")
        article = render_achievement(
            _demo_copy_achievement(ach), number, wrap=False
        )
        article = re.sub(
            r'<button[^>]*class="note-btn"[^>]*>.*?</button>', "", article
        )
        demos.append(
            f'<div class="col-12 col-md-6 col-xl-4">'
            f'<p class="small text-secondary">{caption}</p>{article}</div>'
        )

    def demo_card(title, caption):
        card = next(
            (
                c
                for s in dungeons["sections"]
                for c in s.get("step_cards", [])
                if c["title"] == title
            ),
            None,
        )
        if card is None:
            fail(f"How page demo step card missing: {title}")
        article = render_step_card(_demo_copy_step_card(card), wrap=False)
        demos.append(
            f'<div class="col-12 col-md-6 col-xl-4">'
            f'<p class="small text-secondary">{caption}</p>{article}</div>'
        )

    demo_ach(
        "ach-happy",
        "<strong>Simple achievement.</strong> Click the header to "
        "tick it. Every achievement at its simplest: name, "
        "Gamerscore, requirement, route.",
    )
    demo_ach(
        "ach-highdry",
        "<strong>Multi-step achievement.</strong> Tick the steps "
        "and watch the bar under the header fill. Ticking all "
        "three ticks the achievement itself.",
    )
    demo_ach(
        "ach-wooden",
        "<strong>Counter achievement.</strong> Tap −/+ or type a "
        "number. The bar under the header shows progress toward "
        "50; on the real page this counter is shared with Diamond Sword.",
    )
    demo_card(
        "Creepy Crypt — secret mission",
        "<strong>Step card, not an achievement.</strong> No "
        "Gamerscore, no header toggle. These are walkthrough "
        "steps, like the secret missions and runes.",
    )
    demo_ach(
        "ach-inspekta",
        "<strong>Slideshow achievement.</strong> Use Previous "
        "and Next to walk through the guide slides — the card "
        "stays the same height throughout, so nothing below it "
        "jumps. Slide images open in the viewer, like on a real "
        "game page.",
        game=grove,
    )
    return "\n".join(demos)


def render_how(all_games):
    """Render the standalone How it works page (no game data)."""
    template = (TOOLS_DIR / "how_template.html").read_text(encoding="utf-8")
    replacements = {
        "ASSET_PREFIX": "../assets/",
        "SIDEBAR_MENU": sidebar_menu(all_games, "../", "how"),
        "SIDEBAR_PREFIX": "../",
        "HOW_HREF": sidebar_how_href("../", "how"),
        "HOW_ACTIVE": " active",
        "DEMO_CARDS": render_demos(all_games),
        "REPO_URL": REPO_URL,
    }
    for key in replacements:
        if f"@@{key}@@" not in template:
            fail(f"how_template.html is missing placeholder @@{key}@@")
    return _fill(template, replacements)


def main():
    parser = argparse.ArgumentParser(description="Generate achievement-tracker pages.")
    parser.add_argument("--check", action="store_true",
                        help="fail if any generated output would change")
    parser.add_argument("--game", help="only generate this slug")
    args = parser.parse_args()

    all_games = load_games()
    games = all_games
    if args.game:
        games = [g for g in all_games if g["slug"] == args.game]
        if not games:
            fail(f"no game with slug {args.game!r}")
        print("generate: warning: --game regenerates only one game page; "
              "run the full generator before committing.",
              file=sys.stderr)

    # The AdminLTE shell is vendored, not CDN-loaded. If the vendor
    # set is missing, every generated page would ship broken links,
    # so fail here instead of generating them.
    for vendor_file in VENDOR_FILES:
        if not (ROOT / "assets" / "vendor" / vendor_file).exists():
            fail(f"missing vendored shell asset: assets/vendor/{vendor_file}")

    outputs = {}
    for game in games:
        out_dir = ROOT / game["slug"]
        outputs[out_dir / "index.html"] = render_game(game, all_games)
    outputs[ROOT / "index.html"] = render_hub(all_games)
    outputs[ROOT / "how-it-works" / "index.html"] = render_how(all_games)

    changed = []
    for path, content in outputs.items():
        if args.check:
            if not path.exists() or path.read_text(encoding="utf-8") != content:
                changed.append(str(path))
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            print(f"wrote {path.relative_to(ROOT)} "
                  f"({len(content):,} bytes)")

    if args.check:
        if changed:
            print("generate --check: these outputs are out of date:", file=sys.stderr)
            for path in changed:
                print(f"  {path}", file=sys.stderr)
            print("run `python3 tools/generate.py` and commit the result.",
                  file=sys.stderr)
            return 1
        print("generate --check: all outputs up to date")
        return 0

    for game in games:
        print(f"{game['slug']}: {game['_total_count']} achievements, "
              f"{game['_total_gs']:,}G")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
