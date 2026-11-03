#!/usr/bin/env python3
"""Generate achievement-tracker pages from data/*.json.

Source of truth is the JSON, not the HTML. The generator:
  * validates every game (Gamerscore sum, unique ids, counter groups,
    non-empty requirement/route text, declared sources),
  * renders one self-contained index.html per game from tools/template.html
    (CSS/JS are inlined, so each page works on its own at a Pages subpath),
  * renders the hub index.html from the same data, with per-game progress
    read from localStorage on the hub page itself.

Usage, from the repo root:
    python3 tools/generate.py            # write all outputs
    python3 tools/generate.py --check    # exit 1 if any output would change
    python3 tools/generate.py --game minecraft-dungeons

Adding a game: copy data/minecraft-dungeons.json to data/<slug>.json,
fill it in (see that file for the schema), run the generator, preview
with `python3 -m http.server 8000`, then commit the JSON *and* the
generated HTML. Never hand-edit a generated page — edit the JSON and
regenerate, or the next run will overwrite your edit (and --check
exists to catch exactly that drift in CI).
"""

import argparse
import html as html_lib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
TOOLS_DIR = ROOT / "tools"

# Short filter labels for section ids. Unknown ids fall back to the
# section title up to the first "·" (or the id itself).
FILTER_LABELS = {
    "story": "First run",
    "steps": "Secrets & runes",
    "replay": "Replays & mop-up",
    "jungle": "Jungle",
    "winter": "Creeping Winter",
}


def fail(message):
    print(f"generate: error: {message}", file=sys.stderr)
    raise SystemExit(1)


def load_games():
    files = sorted(DATA_DIR.glob("*.json"))
    if not files:
        fail("no data/*.json files found")
    games = []
    for path in files:
        try:
            game = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            fail(f"{path.name}: invalid JSON: {exc}")
        validate_game(path.name, game)
        games.append(game)
    return games


def validate_game(filename, game):
    def check(condition, message):
        if not condition:
            fail(f"{filename}: {message}")

    for field in ("slug", "title", "tagline", "order_note", "scope_note",
                  "storage_key", "sections", "sources"):
        check(game.get(field), f"missing/empty field {field!r}")
    check(game["slug"] == Path(filename).stem,
          f"slug {game['slug']!r} does not match filename {filename!r}")
    check(re.fullmatch(r"[a-z0-9][a-z0-9-]*", game["slug"]),
          f"slug {game['slug']!r} is not URL-safe")
    check(game["sources"], "sources must list at least one source")
    for source in game["sources"]:
        check(source.get("label") and source.get("url", "").startswith("https://"),
              f"bad source entry: {source!r}")

    task_ids, step_ids, counter_groups = set(), set(), {}
    achievements, total_gs, number = [], 0, 0
    for section in game["sections"]:
        check(section.get("id") and section.get("title"),
              f"section missing id/title: {section!r}")
        for ach in section.get("achievements", []):
            number += 1
            achievements.append(ach)
            check(ach["id"] not in task_ids, f"duplicate achievement id {ach['id']!r}")
            task_ids.add(ach["id"])
            check(isinstance(ach.get("gs"), int) and ach["gs"] > 0,
                  f"{ach['id']}: gs must be a positive integer")
            total_gs += ach["gs"]
            for field in ("name", "req", "how"):
                check(ach.get(field), f"{ach['id']}: missing/empty {field!r}")
            for step in ach.get("steps", []):
                check(step["id"] not in step_ids, f"duplicate step id {step['id']!r}")
                step_ids.add(step["id"])
                check(step.get("label"), f"{ach['id']}: step missing label")
            for counter in ach.get("counters", []):
                group = counter.get("group")
                check(group and isinstance(counter.get("target"), int)
                      and counter["target"] > 0,
                      f"{ach['id']}: bad counter {counter!r}")
                counter_groups.setdefault(group, set()).add(counter["target"])
        for card in section.get("step_cards", []):
            check(card.get("title") and card.get("how") and card.get("steps"),
                  f"step card missing title/how/steps: {card!r}")
            for step in card["steps"]:
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
    game["_counter_groups"] = counter_groups
    # The hub and the header show the declared scope; the generator's
    # own total is the check, so a typo in a single GS value fails here
    # instead of silently shipping a wrong progress bar.
    return game


def esc(text):
    return html_lib.escape(str(text), quote=True)


def render_counter(counter):
    group, target = esc(counter["group"]), int(counter["target"])
    return (
        f'<div class="counter mt-2"><input type="number" class="count form-control d-inline-block" '
        f'style="width:110px" '
        f'data-counter="{group}" data-target="{target}" min="0" value="0"> '
        f'<span class="count-text text-secondary"></span>'
        f'<div class="progress mt-2" style="height:10px"><div class="progress-bar bg-success" style="width:0%"></div></div></div>'
    )


def render_steps(steps, parent_id=None):
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


def render_achievement(ach, number):
    parts = [
        '<article class="ach item card col-12 col-md-6 col-xl-4" data-name="'
        + esc(f"{ach['name']} {ach['req']} {ach['how']}") + '">',
        '<div class="card-header ach-head d-flex gap-2 align-items-start">'
        f'<input type="checkbox" class="task" id="{esc(ach["id"])}" data-gs="{ach["gs"]}">'
        f'<div><span class="num text-secondary small fw-semibold">#{number}</span>'
        f'<h3 class="fs-6 mb-0">{esc(ach["name"])}</h3></div>'
        f'<span class="gs badge text-bg-warning ms-auto">{ach["gs"]}G</span></div>',
        '<div class="card-body">',
        f'<p class="req text-secondary">{esc(ach["req"])}</p>',
        f'<p class="how">{esc(ach["how"])}</p>',
        render_steps(ach.get("steps", []), parent_id=ach["id"]),
    ]
    for counter in ach.get("counters", []):
        parts.append(render_counter(counter))
    parts.append("</div></article>")
    return "".join(parts)


def render_step_card(card):
    return (
        '<article class="ach item card col-12 col-md-6 col-xl-4" data-name="'
        + esc(f"{card['title']} {card['how']}") + '">'
        f'<div class="card-header"><h3 class="fs-6 mb-0">{esc(card["title"])}</h3></div>'
        '<div class="card-body">'
        f'<p class="how">{esc(card["how"])}</p>'
        + render_steps(card["steps"])
        + "</div></article>"
    )


def render_sections(game):
    number = 0
    out = []
    for section in game["sections"]:
        achievements = section.get("achievements", [])
        cards = section.get("step_cards", [])
        is_first = section is game["sections"][0]
        open_attr = " open" if is_first else ""
        if achievements:
            sec_gs = sum(a["gs"] for a in achievements)
            subtitle = f"{len(achievements)} achievements, {sec_gs}G"
            if section.get("subtitle"):
                subtitle = section["subtitle"]
            summary = (f'{section["title"]} <small>{esc(subtitle)} · '
                       f'<span class="sec-progress" data-section="{esc(section["id"])}"></span></small>')
        else:
            summary = (f'{section["title"]} <small>{esc(section.get("subtitle", ""))}</small>'
                       if section.get("subtitle") else section["title"])
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


def games_nav(all_games, current_slug=None, prefix="../"):
    items = []
    for game in all_games:
        active = ' active' if game["slug"] == current_slug else ""
        items.append(
            f'              <li><a class="dropdown-item{active}" '
            f'href="{prefix}{esc(game["slug"])}/">{esc(game["title"])}</a></li>'
        )
    return "\n".join(items)


def render_game(game, all_games):
    template = (TOOLS_DIR / "template.html").read_text(encoding="utf-8")
    filters = []
    for section in game["sections"]:
        label = FILTER_LABELS.get(section["id"])
        if not label:
            label = section["title"].split("·")[0].strip() or section["id"]
        filters.append(
            f'      <button type="button" class="filter" data-filter="{esc(section["id"])}">'
            f"{esc(label)}</button>"
        )
    sources = " · ".join(
        f'<a href="{esc(s["url"])}">{esc(s["label"])}</a>' for s in game["sources"]
    )
    replacements = {
        "@@ASSET_PREFIX@@": "../assets/",
        "@@GAMES_NAV@@": games_nav(all_games, current_slug=game["slug"]),
        "@@TITLE@@": esc(game["title"]),
        "@@TAGLINE@@": esc(game["tagline"]),
        "@@ORDER_NOTE@@": esc(game["order_note"]),
        "@@SCOPE_NOTE@@": esc(game["scope_note"]),
        "@@SLUG@@": esc(game["slug"]),
        "@@STORAGE_KEY@@": esc(game["storage_key"]),
        "@@LEGACY_KEY@@": esc(game.get("legacy_key", "")),
        "@@LEGACY_MIGRATION_JSON@@": json.dumps(game.get("legacy_migration") or {}),
        "@@TOTAL_GS@@": str(game["_total_gs"]),
        "@@TOTAL_COUNT@@": str(game["_total_count"]),
        "@@FILTER_BUTTONS@@": "\n".join(filters),
        "@@SECTIONS_HTML@@": render_sections(game),
        "@@SOURCES_HTML@@": sources,
    }
    out = template
    for key, value in replacements.items():
        if key not in out:
            fail(f"template.html is missing placeholder {key}")
        out = out.replace(key, value)
    leftovers = re.findall(r"@@[A-Z_]+@@", out)
    if leftovers:
        fail(f"unreplaced placeholders in {game['slug']}: {sorted(set(leftovers))}")
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
        cards.append(
            f'<div class="game item card col-12 col-md-6" data-name="{esc(game["title"])}">'
            f'<div class="card-header"><h3 class="fs-5 mb-0"><a href="{esc(game["slug"])}/">{esc(game["title"])}</a></h3></div>'
            f'<div class="card-body">'
            f'<p class="text-secondary">{esc(game["scope_note"])}</p>'
            f'<p><strong>{total_count} achievements · {total_gs:,}G</strong> · '
            f'<span class="game-progress" data-slug="{esc(game["slug"])}">Not started yet</span></p>'
            f'<p class="mb-0"><a class="btn btn-success" href="{esc(game["slug"])}/">Open tracker →</a></p>'
            f'</div></div>'
        )
    replacements = {
        "@@ASSET_PREFIX@@": "./assets/",
        "@@GAMES_NAV@@": games_nav(games, prefix="./"),
        "@@GAMES_CARDS@@": chr(10).join(cards),
        "@@HUB_DATA@@": json.dumps(hub_data),
    }
    out = template
    for key, value in replacements.items():
        if key not in out:
            fail(f"hub_template.html is missing placeholder {key}")
        out = out.replace(key, value)
    leftovers = re.findall(r"@@[A-Z_]+@@", out)
    if leftovers:
        fail(f"unreplaced placeholders in hub: {sorted(set(leftovers))}")
    return out


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

    # The AdminLTE shell is vendored, not CDN-loaded. If the vendor
    # set is missing, every generated page would ship broken links,
    # so fail here instead of generating them.
    for vendor_file in ("bootstrap.min.css", "bootstrap-icons.min.css",
                        "adminlte.min.css", "bootstrap.bundle.min.js",
                        "adminlte.min.js"):
        if not (ROOT / "assets" / "vendor" / vendor_file).exists():
            fail(f"missing vendored shell asset: assets/vendor/{vendor_file}")

    outputs = {}
    for game in games:
        out_dir = ROOT / game["slug"]
        outputs[out_dir / "index.html"] = render_game(game, all_games)
    outputs[ROOT / "index.html"] = render_hub(all_games)

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
