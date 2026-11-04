#!/usr/bin/env python3
"""Fill xbox_title_id + xbox_id in a game JSON from a saved OpenXBL
per-title achievements response.

Usage (from the repo root):

    python3 tools/map_xbox.py --title-id 1234567890 response.json
    python3 tools/map_xbox.py --title-id 1234567890 response.json \\
        --game data/minecraft-dungeons.json

``response.json`` is the JSON from
``GET /api/v2/achievements/player/{xuid}/title/{titleId}``, saved by
the user with their own OpenXBL key — this tool never talks to
OpenXBL, and the key never appears in it.

Matching is by achievement name (exact, then punctuation-insensitive),
with Gamerscore as a tiebreak. Every tracker achievement must match
exactly one response entry, or the tool writes nothing and exits 1.
The game file is edited surgically (one inserted field per
achievement line, one title-id line after the slug), so the diff
shows exactly the mapping and nothing else — review it before
committing. The runtime sync still matches by Xbox id only; name
matching happens here, once, at build time.
"""

import argparse
import json
import re
import sys
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent
ROOT = TOOLS_DIR.parent


class MatchError(Exception):
    """A tracker achievement could not be matched unambiguously."""


def extract_achievements(payload):
    """Achievement entries from an OpenXBL response, or None.

    Accepts the two shapes seen in the wild: a bare array, and an
    object with an ``achievements`` array. Anything else is not a
    per-title achievements response.
    """
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict) and isinstance(payload.get("achievements"), list):
        return payload["achievements"]
    return None


def entry_gamerscore(entry):
    """Gamerscore for a response entry, or None if it carries none.

    Xbox entries carry rewards like [{"name": "Gamerscore",
    "value": "10"}]; some wrappers flatten that to a gamerscore field.
    """
    for reward in entry.get("rewards", []) or []:
        if isinstance(reward, dict) and reward.get("name") == "Gamerscore":
            try:
                return int(reward["value"])
            except (TypeError, ValueError):
                continue
    for field in ("gamerscore", "gamerscoreValue"):
        if entry.get(field) is not None:
            try:
                return int(entry[field])
            except (TypeError, ValueError):
                continue
    return None


def normalize(name):
    """Punctuation-insensitive form, for the fallback match."""
    return re.sub(r"[^a-z0-9]", "", str(name).lower())


def match_entries(tracker_achievements, entries):
    """Map tracker achievement id -> Xbox id.

    Returns (mapping, report) where report is a list of
    (tracker id, entry id, kind, gs_warning) with kind "exact" or
    "normalized". Raises MatchError listing every unmatched or
    ambiguous achievement, so a partial mapping is never written.
    """
    by_exact = {}
    by_normalized = {}
    for entry in entries:
        name = entry.get("name")
        if not name or entry.get("id") is None:
            continue
        by_exact.setdefault(str(name), []).append(entry)
        by_normalized.setdefault(normalize(name), []).append(entry)
    mapping, report, problems = {}, [], []
    for ach in tracker_achievements:
        candidates = by_exact.get(ach["name"], [])
        kind = "exact"
        if not candidates:
            candidates = by_normalized.get(normalize(ach["name"]), [])
            kind = "normalized"
        if len(candidates) > 1:
            gs_matches = [e for e in candidates
                          if entry_gamerscore(e) == ach["gs"]]
            if len(gs_matches) == 1:
                candidates = gs_matches
        if len(candidates) != 1:
            problems.append(
                f"{ach['id']} ({ach['name']!r}): "
                f"{'no match' if not candidates else 'ambiguous match'} "
                f"in the OpenXBL response")
            continue
        entry = candidates[0]
        gs = entry_gamerscore(entry)
        warning = None
        if gs is not None and gs != ach["gs"]:
            warning = (f"Gamerscore differs: tracker {ach['gs']}G, "
                       f"OpenXBL {gs}G")
        mapping[ach["id"]] = str(entry["id"])
        report.append((ach["id"], str(entry["id"]), kind, warning))
    if problems:
        raise MatchError("\n".join(problems))
    return mapping, report


def apply_mapping(game_text, game, title_id, mapping):
    """Insert the title id and xbox_ids into the game file's text.

    Achievements in this repo's JSON are one object per line, so each
    mapping lands as one inserted field on that achievement's line
    and the rest of the file is byte-identical. The result is parsed
    and validated before the caller writes it.
    """
    if "xbox_title_id" in game:
        raise MatchError("game JSON already has xbox_title_id; "
                         "remove it before re-mapping")
    for ach in game["_achievements"]:
        if ach.get("xbox_id"):
            raise MatchError(f"{ach['id']} already has xbox_id; "
                             "remove existing mappings before re-mapping")
    slug_line = f'  "slug": "{game["slug"]}",'
    if game_text.count(slug_line) != 1:
        raise MatchError("could not find the game's slug line exactly once")
    out = game_text.replace(
        slug_line,
        slug_line + f'\n  "xbox_title_id": "{title_id}",', 1)
    for ach in game["_achievements"]:
        needle = '{"id": "%s",' % ach["id"]
        if out.count(needle) != 1:
            raise MatchError(
                f"could not find achievement {ach['id']!r} exactly once")
        out = out.replace(
            needle,
            '{"id": "%s", "xbox_id": "%s",' % (ach["id"], mapping[ach["id"]]),
            1)
    return out


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Map a saved OpenXBL response onto a game JSON.")
    parser.add_argument("--title-id", required=True,
                        help="Xbox title id (digits, as used in the URL)")
    parser.add_argument("response", help="saved OpenXBL JSON response")
    parser.add_argument("--game", default="data/minecraft-dungeons.json",
                        help="game JSON to update (default: "
                             "data/minecraft-dungeons.json)")
    args = parser.parse_args(argv)
    if not re.fullmatch(r"[0-9]+", args.title_id):
        print("map_xbox: --title-id must be a string of digits",
              file=sys.stderr)
        return 2
    game_path = Path(args.game)
    if not game_path.is_absolute():
        game_path = ROOT / game_path
    sys.path.insert(0, str(TOOLS_DIR))
    from generate import validate_game  # noqa: E402

    try:
        game_text = game_path.read_text(encoding="utf-8")
        game = json.loads(game_text)
        payload = json.loads(Path(args.response).read_text(encoding="utf-8"))
        entries = extract_achievements(payload)
        if entries is None:
            print("map_xbox: response is not an OpenXBL achievements "
                  "list (expected an array or an 'achievements' array)",
                  file=sys.stderr)
            return 2
        validate_game(str(game_path), game)
        mapping, report = match_entries(game["_achievements"], entries)
        new_text = apply_mapping(game_text, game, args.title_id, mapping)
        # Validate the edited text before writing anything.
        validate_game(str(game_path), json.loads(new_text))
    except MatchError as exc:
        print(f"map_xbox: {exc}\nNothing was written.", file=sys.stderr)
        return 1
    except (OSError, json.JSONDecodeError) as exc:
        print(f"map_xbox: {exc}", file=sys.stderr)
        return 2
    game_path.write_text(new_text, encoding="utf-8")
    mapped_xids = set(mapping.values())
    not_in_tracker = sum(
        1 for e in entries
        if e.get("id") is not None and str(e["id"]) not in mapped_xids)
    no_id = sum(1 for e in entries if e.get("id") is None)
    print(f"map_xbox: mapped {len(mapping)} achievements, "
          f"title id {args.title_id}")
    for ach_id, xid, kind, warning in report:
        line = f"  {ach_id} -> {xid} ({kind})"
        if warning:
            line += f"  WARNING: {warning}"
        print(line)
    print(f"  response entries not in this tracker: {not_in_tracker} "
          f"(expected: the title's other achievements)")
    if no_id:
        print(f"  note: {no_id} response entries had no id and were "
              f"ignored")
    return 0


if __name__ == "__main__":
    sys.exit(main())
