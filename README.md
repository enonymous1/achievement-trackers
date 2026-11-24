# achievement-trackers

Interactive achievement trackers, housed in one GitHub Pages site.
Every card *is* an achievement — its name, Gamerscore and requirement —
with the short route to that achievement underneath it. Achievements
are grouped and ordered by how they typically unlock, so you can work
through a game in order instead of hunting through a flat list.

**Live site:** https://enonymous1.github.io/achievement-trackers/

<!-- The demo GIF below is still commented out on purpose: it needs a
     real interaction recording (ticking, counting, theme toggle), not
     a mocked animation. Uncomment it when that capture exists.
     Every other screenshot here was captured from the real local app.
-->
![Hub landing page, dark mode](docs/screenshots/hub-dark.png)
<!-- ![Ticking achievements, counters and theme toggle](docs/screenshots/tracker-demo.gif) -->

## What it looks like

![Dungeons tracker, dark mode, with three achievements ticked](docs/screenshots/tracker-dark.png)
![Same tracker, light mode](docs/screenshots/tracker-light.png)
![Dungeons tracker on a phone](docs/screenshots/tracker-mobile.png)

The hub is the landing page: a welcome line, a how-it-works card, a
search box with a sort control beside it (name, completion,
achievements, started), and one card per game showing its achievement count,
Gamerscore total, and your saved progress on this browser. The footer
totals the whole library (currently: 16 games · 523 achievements ·
16,250G) and links to this repo.

Each game page has a Gamerscore progress bar, search, an
incomplete-only toggle, phase filters, and export / import / reset for
your progress. Ticking an achievement fills its steps and counters,
and unticking clears them; counters stop at their target with a
yes/no gate to go past it. The top bar stays frozen while scrolling
and carries the compact progress. Cards can carry notes, a Missable
pill, and screenshots or step-by-step slideshows. Progress saves in your browser only (localStorage, one
key per game); nothing is uploaded, and the hub can show progress
across games because they share the same Pages origin. Each page also
has an [Xbox sync card](docs/xbox-sync.md) (when a game is mapped) that ticks from your
Xbox data with your own key. A Privacy Dashboard import was tried
and dropped: the archive holds app usage, not achievement records —
see "We tried the Microsoft export" on the How it works page.

Xbox sync (OpenXBL) is built but dormant — no game is mapped yet. Setup lives in [docs/xbox-sync.md](docs/xbox-sync.md).

## Description

This repo is a small static-site pipeline, not a web app with a
backend. The pipeline is:

1. **Data:** one JSON file per game in `data/<slug>.json` is the
   source of truth.
2. **Generator:** `tools/generate.py` validates that JSON (Gamerscore
   sums, unique ids, counter groups, non-empty requirement/route text,
   declared sources) and renders the pages.
3. **Pages:** the generated HTML is committed to the repo, and
   GitHub Actions deploys it to GitHub Pages. There is no runtime
   build step and no server.

The trade-off, stated plainly: a game page is **not** portable on its
own. It references the shared vendored shell under `assets/vendor/`,
so the repo — not a lone file — is the distribution unit. That is the
right shape for a Pages hub, and it is why generated pages are
committed rather than built on deploy.

**Current games:**

| Game | Achievements | Gamerscore | Notes |
| --- | --- | --- | --- |
| Minecraft Dungeons | 34 | 1,250G | Partial: base + Jungle Awakens + Creeping Winter; full game is 104 / 3,000G |
| Great God Grove | 42 | 1,000G | Full game, walkthrough order |
| Barbie Horse Trails | 15 | 1,000G | Full game, story order |
| Pigeon Simulator | 10 | 1,000G | Full game, walkthrough order |
| Winter Burrow | 32 | 1,000G | Full game, walkthrough order |
| 1000xRESIST | 32 | 1,000G | Full game, story order; 7 missables |
| GoldenEye 007 | 55 | 1,000G | Full game, walkthrough order |
| Relic Hunters Legend | 18 | 1,000G | Full game, story order |
| Wreckfest (Windows) | 20 | 1,000G | Full game |
| Dragon Ball Xenoverse 2 | 50 | 1,000G | Base game only; 11 DLC out of scope |
| Moonlighter | 57 | 1,000G | Full base game; 7 missables; Between Dimensions DLC out of scope |
| Police Simulator: Patrol Officers | 25 | 1,000G | Full game |
| Firefighting Simulator: The Squad | 30 | 1,000G | Full game |
| Total Chaos | 37 | 1,000G | Full game; 6 missables |
| Gabby's Dollhouse: Ready to Party | 16 | 1,000G | Full game, walkthrough order |
| Generation Zero | 50 | 1,000G | Base game only; 3 DLC packs out of scope |
| **Total** | **523** | **16,250G** | |

## Prerequisites

- **Python 3.12** — for `tools/generate.py` and `tools/check_js.py`.
  No Python packages to install; the tools use the standard library
  only.
- **Node.js 20+** — only for `tools/check_js.py`, which runs
  `node --check` on the inline scripts in the generated pages.
  If you never touch the templates, you can skip Node and still run
  the generator.
- **Git** — for cloning and committing.
- A browser, for previewing. No other services, accounts, or API keys
  are needed.

## Installation

```sh
git clone https://github.com/enonymous1/achievement-trackers.git
cd achievement-trackers
```

There is nothing to install. Verify the checkout is clean and the
generated pages match the data:

```sh
python3 tools/generate.py --check
```

If that reports out-of-date outputs, run the generator (see Local
Development) and commit the result — never hand-edit a generated page.

## Local Development

### Preview the site

```sh
python3 -m http.server 8000
# hub:  http://127.0.0.1:8000/
# game: http://127.0.0.1:8000/games/minecraft-dungeons/
```

### Regenerate after editing data or templates

```sh
python3 tools/generate.py
```

The generator **fails** instead of shipping a wrong page: on a
Gamerscore sum mismatch against the declared `total_gs` / `total_count`,
a duplicate achievement or step id, a bad counter, missing
requirement/route text, a missing vendored shell asset, an unreplaced
template placeholder, or an absolute path in a generated page.

### Checks (also run in CI)

```sh
python3 -m unittest discover -s tools -v   # validator + rendering tests (stdlib only)
pip install ruff && ruff check tools/       # lint (line length 100, see pyproject.toml)
python3 tools/generate.py --check           # generated pages match the data, without writing
python3 tools/check_js.py                   # scripts pass node --check (requires Node)
```

### Adding a game

1. Copy `data/minecraft-dungeons.json` to `data/<slug>.json` and fill
   it in. The filename must match the `slug` field, and the slug must
   be URL-safe (`[a-z0-9][a-z0-9-]*`).
2. Run the generator, preview locally, and commit the JSON **and**
   the generated HTML together.

Schema, per game file:

- Top level: `slug`, `title`, `tagline`, `order_note`, `scope_note`,
  `total_gs`, `total_count`, `storage_key`, `sources` (each a `label`
  + `https://` URL). `total_gs` / `total_count` are the generator's
  check: if the achievements in the file do not sum/count to them,
  generation fails.
- `legacy_key` and `legacy_migration` are optional, for moving
  progress from an older tracker key (see the Dungeons file).
- Sections: `id`, `title`, optional `subtitle`, optional `intro`,
  `achievements`, `step_cards`. The first section is open by
  default; later sections start collapsed. If `subtitle` is set on
  an achievement section it replaces the computed
  "N achievements, XG" summary; otherwise that summary is computed.
- Achievements: `id`, `name`, `gs` (non-negative integer — a
  genuine 0G achievement exists), `req`, `how`,
  optional `steps` (`id`, `label`) — ticking every step auto-ticks
  the achievement, and ticking the achievement fills its steps
  and counters (unticking clears them) — and optional `counters` (`group`, `target`).
  Counters with the same `group` share one number across
  achievements, and different achievements in one group may have
  different targets (one shared value, several thresholds — e.g.
  mobs defeated feeds both a 50 and a 2,500 target).
  Optional `missable: true` renders a Missable pill (a choice or
  one-time window). Optional `media` lists screenshots/clips under
  the route note: `type` image/video, `src` an `assets/` path
  (files live under `assets/media/<slug>/`, referenced as
  `assets/...` in the JSON) or an `https://` URL; a remote video
  must be a media file or a YouTube URL (embedded
  privacy-enhanced). `credit` renders an "Image: …" overlay
  on the image, shown on hover (and in the viewer caption);
  guide images carry their source as credit, and a
  failed load swaps in a placeholder explaining why instead of a
  broken-image icon. `full` (optional) is a larger version the
  image opens in an on-page viewer (a new tab if scripts are
  off). Media must be real captures, never mocked.
  Optional `slideshow` is an ordered step-by-step guide for
  the card (same entry shape as media, images only), rendered
  one slide at a time with Previous/Next buttons; slide images
  open in the same viewer, where Previous/Next step through
  the slideshow too (or tap the left/right side of the
  image). Card headers shrink long names toward a floor and
  equalise per row, so bodies start on one line.
- `step_cards`: walkthrough steps that are *not* achievements
  themselves (secret missions, runes) — `title`, `how`, `steps`.
- Filter buttons: each section may carry its own `filter_label`
  (preferred). A section without one falls back to a short map in
  `tools/generate.py` (`FILTER_LABELS`, keyed by section id), then
  to the section title up to the first `·`, or the id itself.
  New section types should get a `filter_label` in the JSON, not a
  code change.
- The formal schema is `data/schema.json` (human-readable contract;
  enforcement lives in `tools/generate.py`).

> **Do not run `python3 tools/generate.py --game <slug>` before
> committing.** That mode regenerates the hub plus one game page
> only, leaving other game pages untouched. Always run the full
> generator before committing.

### Project layout

```
achievement-trackers/
  index.html                  # hub / landing page (generated)
  games/<slug>/index.html     # one tracker per game (generated)
  how-it-works/index.html     # How it works page (generated)
  assets/vendor/              # AdminLTE shell, vendored — no CDN
  assets/css/sidebar.css      # shared left-sidebar layout
  assets/css/tracker-cards.css # shared card language (game + How demos)
  assets/js/theme-toggle.js   # shared theme toggle (see below)
  assets/js/sidebar-state.js  # sidebar collapsed/open persistence
  assets/favicon.svg          # trophy favicon
  data/<slug>.json            # the game data — edit this
  data/schema.json            # human-readable schema for game data
  docs/architecture.svg       # pipeline diagram
  docs/screenshots/           # real captures from the local app
  tools/generate.py           # validator + renderer
  tools/config.py             # repo URL, shell versions, vendor list
  tools/fragments/            # card markup (achievement, step, counter)
  tools/check_js.py           # node --check for scripts
  tools/test_generate.py      # stdlib unit tests
  tools/template.html         # the tracker page template
  tools/hub_template.html     # the hub page template
  tools/how_template.html     # the How it works page template
  .github/workflows/check.yml # shared checks, called by CI + Pages
  .github/workflows/ci.yml    # checks on push / PR
  .github/workflows/pages.yml # check, then deploy to Pages
  pyproject.toml              # ruff configuration
  CHANGELOG.md                # notable changes, by date
  LICENSE                     # MIT
```

### Troubleshooting

| Symptom | Cause / fix |
|---|---|
| `generate --check` lists out-of-date outputs | Run `python3 tools/generate.py` and commit the JSON + HTML together. Do not edit the generated HTML by hand. |
| `declared total_gs … does not match sum` | A `gs` value in the JSON is wrong, or `total_gs` is stale. Fix the data, not the check. |
| `duplicate achievement/step id` | Ids must be unique across the whole game file, not just within a section. Rename the newer one. |
| `missing vendored shell asset` | `assets/vendor/` is incomplete (e.g. a partial clone). Restore it; the generator refuses to ship pages with broken shell links. |
| `check_js.py: node not found` | Install Node 20+, or skip the JS check locally — CI still runs it. |
| Progress lost / "Not started yet" after clearing data | Progress lives in localStorage only. Clearing site data, switching browsers, or using private mode starts fresh. Export progress first if it matters. |

## Architecture

![Pipeline diagram](docs/architecture.svg)

One JSON file per game is validated and rendered by a single Python
generator into committed HTML. The shell — AdminLTE 4.10.0 +
Bootstrap 5.3.8 + Bootstrap Icons 1.11.3, vendored under
`assets/vendor/` (see `THIRD_PARTY_NOTICES.md` there) — is shared by
every page, in a left-sidebar layout: the sidebar holds the
"Achievement Trackers" brand, Home, a Games header with the games
grouped under A–Z letter headers, and a How it works link anchored to the
bottom; the sidebar collapses with the hamburger in the top bar,
and that state persists across pages on its own localStorage key.
The top bar is frozen while scrolling and carries the compact
progress (text plus a thin bar) and the icon light/dark toggle, on
the shared `at-theme` localStorage key. The generator computes the relative
asset prefix per page (`./assets/` from the hub, `../assets/` from a
game or How page), and refuses to emit absolute paths.

Pages carry no backend and no tracking. The only state is localStorage:
one key per game for ticks, steps, counters and notes, read by the hub
to show per-game progress. Card markup lives in HTML fragments under
`tools/fragments/` (not in Python strings), shell versions and the
repo URL live in `tools/config.py`, and the tracker JS is inline in
each generated page while the theme toggle and sidebar-state
persistence are shared files (`assets/js/theme-toggle.js`,
`assets/js/sidebar-state.js`) loaded by all three templates. The
card styling itself is shared too (`assets/css/tracker-cards.css`),
so the How page's live demo cards — real cards rendered from the
Dungeons data through the same fragments, with demo-prefixed ids
and a sandboxed demo script that never touches localStorage — look
exactly like the real ones.

## Deployment

Deployment is GitHub Actions, not branch publishing:

1. Push to `main` (or run the `Pages` workflow manually via
   `workflow_dispatch`).
2. The `Pages` workflow first calls the shared `check.yml` workflow
   (unit tests, ruff, `generate.py --check`, `check_js.py`), then —
   on `main` only — stages only site files (`index.html`, `assets/`,
   `how-it-works/`, and each game directory under `games/`, all
   derived from the data slugs) into `_site/` and deploys with
   `configure-pages` → `upload-pages-artifact` (`_site/`) →
   `deploy-pages`, under the `github-pages` environment with
   `contents: read`, `pages: write`, `id-token: write` permissions
   and a `pages` concurrency group that never cancels an in-flight
   deploy.
3. The `CI` workflow calls the same shared checks on every push and
   pull request to `main`, so the two workflows cannot drift apart.

One-time repo setup (after the first push): Settings → Pages →
Build and deployment → Source: **GitHub Actions**. The site is then
https://enonymous1.github.io/achievement-trackers/.

After pushing, also set the repo's social preview image (Settings →
General → Social preview, 1280×640) — GitHub uses it on every link
share, and no README setting can replace it. Suggested image: trophy
icon + "Achievement Trackers" + the current library totals.

## Content rules

- Do not copy a walkthrough's full text. Route notes are short
  paraphrases, and every game page links back to its sources.
- Achievement names, requirements and Gamerscore are facts from the
  achievement list; unlock order, multi-mission pop points, RNG
  gates, and which secrets feed which achievements need human
  judgement per game — the generator automates rendering and
  checking, not that research, and it must not auto-scrape a guide
  site.
- Scope is stated on each page. If a tracker covers only part of a
  game's achievements (e.g. Dungeons: the walkthrough's 34 of the
  full 104), say so on the page — do not present a partial tracker
  as a complete one.

## Contributing

Contributions are welcome, with one rule that matters more than the
rest: **data first, never generated HTML.** Edit `data/<slug>.json`
(or a template, if you are changing presentation for all games), run
the full generator, run both checks, preview locally, and commit the
JSON and the generated HTML together. Pull requests that hand-edit a
generated page will fail `--check` in CI and will not be merged.

If you add a game, include its sources, state its scope honestly, and
keep route notes to short paraphrases — see Content rules above.

## License

MIT — see [LICENSE](LICENSE). The vendored shell under
`assets/vendor/` carries its own MIT licences; see
[assets/vendor/THIRD_PARTY_NOTICES.md](assets/vendor/THIRD_PARTY_NOTICES.md).
