# achievement-trackers

Interactive achievement trackers, housed in one Pages site. Every card
is an achievement, grouped and ordered by how it typically unlocks,
with the short route to that achievement underneath it.

**Live site (after push):** `https://enonymous1.github.io/achievement-trackers/`

## How it works

The JSON is the source of truth — never hand-edit a generated page.

```
achievement-trackers/
  index.html                  # hub / landing page (generated)
  <slug>/index.html           # one tracker per game (generated)
  assets/vendor/              # AdminLTE shell, vendored — no CDN
  data/<slug>.json            # the game data — edit this
  tools/generate.py           # validator + renderer
  tools/check_js.py           # node --check for inline scripts
  tools/template.html         # the tracker page template
  tools/hub_template.html     # the hub page template
  .github/workflows/ci.yml    # drift + JS checks on push / PR
  .github/workflows/pages.yml # check, then deploy to Pages
  LICENSE                     # MIT
```

Shell: **AdminLTE 4.10.0 + Bootstrap 5.3.8 + Bootstrap Icons 1.11.3**,
vendored under `assets/vendor/` (see `THIRD_PARTY_NOTICES.md` there),
in a top-nav layout — brand, Games dropdown in the navbar, content
cards, light/dark toggle (`at-theme` key). No CDN for shell assets,
no absolute paths; the generator computes the relative asset prefix
per page (`./assets/` from the hub, `../assets/` from a game page).

That is the one deliberate trade-off versus a single-file page: a
game page is no longer portable on its own, because it references
the shared vendor set. The repo — not the lone file — is the
distribution unit, which is the right shape for a Pages hub. No
build step is needed at runtime.

Progress saves in the browser only (localStorage), one key per game,
so the hub can show progress across games on the same Pages origin.
Nothing is uploaded.

## Add a game

1. Copy `data/minecraft-dungeons.json` to `data/<slug>.json` and fill
   it in. Schema, per section:
   - `id`, `title`, `subtitle` (optional), `intro` (optional)
   - `achievements`: `id`, `name`, `gs`, `req`, `how`,
     optional `steps` (`id`, `label`) — ticking every step auto-ticks
     the achievement — and optional `counters` (`group`, `target`).
     Counters with the same `group` share one number across
     achievements (e.g. mobs → Wooden Sword + Diamond Sword).
   - `step_cards`: walkthrough steps that are *not* achievements
     themselves (secret missions, runes) — `title`, `how`, `steps`.
   - Top level: `slug`, `title`, `tagline`, `order_note`,
     `scope_note`, `total_gs`, `total_count`, `storage_key`,
     `sources` (label + https URL). `total_gs` / `total_count` are
     the generator's check: if the achievements in the file do not
     sum/count to them, generation fails.
     `legacy_migration` is optional, for moving progress from an
     older tracker key (see the Dungeons file).
2. Run the generator — it **fails** on a Gamerscore sum mismatch,
   duplicate ids, a bad counter, or missing requirement/route text,
   instead of shipping a wrong progress bar:
   ```sh
   python3 tools/generate.py
   ```
3. Preview locally:
   ```sh
   python3 -m http.server 8000
   # hub: http://127.0.0.1:8000/
   # game: http://127.0.0.1:8000/minecraft-dungeons/
   ```
4. Commit the JSON **and** the generated HTML together.

Check that generated pages match the data without writing anything:

```sh
python3 tools/generate.py --check
```

That is also the drift check CI runs on every push and pull request,
alongside a syntax check of the inline scripts in the generated pages
(requires Node):

```sh
python3 tools/check_js.py
```

## Publish on GitHub Pages

1. Create an empty public repo named `achievement-trackers`.
2. Push `main` (repo root = this folder).
3. Repo → Settings → Pages → Build and deployment → Source:
   **GitHub Actions**.
4. The `Pages` workflow runs the checks, then deploys on push to
   `main` (manual runs via workflow_dispatch). First run is the
   check to watch.
5. Site: `https://enonymous1.github.io/achievement-trackers/`.

## Content rules

- Do not copy a walkthrough's full text. Route notes are short
  paraphrases, and every game page links back to its sources.
- Achievement names, requirements and Gamerscore are facts from the
  achievement list; unlock order, multi-mission pop points, RNG
  gates, and which secrets feed which achievements need human
  judgement per game — the generator automates rendering and
  checking, not that research, and it must not auto-scrape a
  guide site.
- Scope is stated on each page. If a tracker covers only part of a
  game's achievements (e.g. Dungeons: the walkthrough's 34 of the
  full 104), say so on the page — do not present a partial tracker
  as a complete one.
