# Changelog

All notable changes to this project are documented here. Dates are
when the change landed, not version numbers — this repo is not
versioned; the git log is the release history.

## 2026-11-04 — Great God Grove (game #2)

### Added

- `data/great-god-grove.json` + generated `great-god-grove/` page:
  all 42 achievements / 1,000G in walkthrough order across 5
  chapters (Grove Cove, Milldread, HobbyHoo, BuzzHuzz, the finale),
  with the hub now listing 2 games (76 achievements, 2,250G). No
  counters, sub-steps, or step cards — every achievement is a single
  card. Route notes are short paraphrases of the TrueAchievements
  walkthrough; a few miscellaneous pop points (the four rabbits as
  the him chain, the beach ball, the pig) are placed at the
  walkthrough moment that triggers them, and the page's order note
  says chapter-end pops may vary slightly.

## 2026-11-04 — Xbox sync setup documented

### Added

- README section documenting the OpenXBL activation steps (key,
  XUID, title ID via title history, per-title fetch, `map_xbox.py`,
  regenerate and commit) and the key-safety rule: the key never goes
  in the repo, because a key in a public repo is public permanently
  and OpenXBL keys carry no per-gamertag scope.

## 2026-11-04 — Privacy Dashboard import (live on every game page)

### Added

- An "Import from a Microsoft export" card on every game page, with
  step-by-step instructions for getting the file: sign in at
  account.microsoft.com/privacy, "Download your data" → "Create new
  archive" with the gaming/activity types ticked, download under
  "Archives" before it expires, extract the ZIP, and pick its JSON
  files (or the whole folder) here. Files are read with FileReader
  in the browser only; nothing is uploaded.
- Import analysis + mapping, before anything is ticked: the parser
  walks whatever JSON (or CSV) the user picks and collects
  achievement-like records — Microsoft documents no filename or
  field list, so it accepts Xbox-style shapes (`progressState`,
  `progression.timeUnlocked`, `titleAssociations`) and generic
  name/date/Gamerscore shapes, and reports files read, records
  found, and unreadable files. Matches are split into confident
  (the file attributes the record to this game — exact title or a
  known edition suffix, so "Minecraft Dungeons II" never counts),
  possible (no game shown — held back unless the user ticks the
  box), ambiguous (one name, several tracker cards — never
  applied), unmatched records for this game (likely later DLC),
  other-game records (never applied even when a name matches), and
  tracker achievements not found in the export. Confirm then ticks
  through the same shared preview/apply path as Xbox sync: newly
  unlocked achievements and their sub-steps only, never unticks,
  never touches notes or counters.
- The Xbox sync preview/apply code is now shared machinery used by
  both import cards (same plan, preview, and Confirm path); the
  sync browser test was re-run after the refactor and still passes.

## 2026-11-04 — Xbox sync support (built, dormant until a game is mapped)

### Added

- A per-game "Sync from Xbox" card and script, rendered only for
  games whose JSON carries `xbox_title_id` and an `xbox_id` per
  achievement. The user pastes their own OpenXBL key (browser only,
  under a separate `at-xbox` key that Export never writes); sync
  fetches via OpenXBL, shows a preview, and applies only on Confirm.
  It ticks newly unlocked achievements and their sub-steps, and
  never unticks, never touches notes or counters. A paste-JSON
  fallback covers browsers where the direct fetch is blocked.
- `tools/map_xbox.py`: fills `xbox_title_id` + all `xbox_id`
  values in a game JSON from a saved OpenXBL per-title response,
  matched by name at build time (exact, then punctuation-insensitive,
  Gamerscore as tiebreak), refusing to write on any unmatched or
  ambiguous achievement. The runtime sync still matches by Xbox id
  only. The generator now rejects partial or duplicate Xbox
  mappings, and the sync card's config travels as data attributes
  (a JSON `<script>` block would fail `check_js.py`).

### Not yet live

- No game JSON carries a mapping yet, so no page shows the sync
  card today. Activation for Dungeons is: fetch the OpenXBL
  per-title response with your own key, run
  `python3 tools/map_xbox.py --title-id <id> response.json`,
  review the diff, regenerate, and commit. The title id and the 34
  Xbox ids are still unfilled and are never guessed.

## 2026-11-04 — Live demo cards on the How page

### Added

- The How page now has a "The cards, up close" section with four
  live demo cards, rendered from the real Minecraft Dungeons data
  through the same fragments as the tracker: a simple achievement
  (Happy Camper), a multi-step achievement (High and Dry), a
  counter achievement (Wooden Sword), and a step card (Creepy
  Crypt), each with a caption saying what to try. They toggle,
  tick and count exactly like the real cards, but the demo script
  is sandboxed — it never touches localStorage, so trying them
  cannot change saved progress, and reloading resets them.

### Changed

- The tracker card styling moved out of the game template into
  `assets/css/tracker-cards.css`, loaded by both the game pages
  and the How page, so the demos cannot drift from the real
  cards. Card fragments are now bare articles; the grid-column
  wrapper is added by the generator, which lets the demos supply
  their own caption + column wrapper. Game pages look identical;
  their HTML is simply smaller because the card CSS now loads as
  a file instead of sitting inline.
- `check_js.py` no longer special-cases the How page: it now has
  its own inline script (the demo handler), so a template edit
  that deleted it would fail the check like any other page.

## 2026-11-03 — Centered step cards, step progress bars

### Changed

- Secrets & runes step cards now center their header title and
  description text. The step pills themselves stay left-aligned so
  the checklist still reads normally.

### Added

- Achievements with two or more sub-step checkboxes now show a
  progress bar right under the card header, like the counter bars:
  it fills as sub-steps are ticked (High and Dry: 0% → 33% → 67% →
  100%, auto-ticking the achievement at 100%) and survives reload.
  Single-step achievements get no bar — it would just mirror the
  achievement's own tick — and step cards get none either, since
  their steps carry no parent to count against.

## 2026-11-03 — Left sidebar, How page

### Changed

- The top nav is gone: navigation is now a collapsible left sidebar
  (AdminLTE `layout-fixed sidebar-expand-lg`). It holds the
  "Achievement Trackers" brand, Home, a Games header with the games
  listed flat underneath it — no dropdown while the list is short —
  and Notes on game pages. The hamburger in the top bar collapses
  the sidebar, and that state persists across pages on its own
  localStorage key (`at-sidebar`), restored before AdminLTE's own
  init so the drawer does not flash open on navigation. On phones
  the sidebar is a drawer over the content, as before with the
  collapsed top nav.
- "How it works" is its own page (`how-it-works/`), linked from the
  bottom of the sidebar and from the hub welcome text, instead of a
  card on the hub. It covers what a tracker is, ticking, sub-steps,
  counters, search and filters, where progress lives, and how the
  site is built.

### Fixed

- The Gamerscore progress card's sticky pin broke in the sidebar
  layout: AdminLTE's `layout-fixed` sets `.app-main` to
  `overflow:auto`, which made it the sticky element's scrolling
  ancestor even though it never scrolls itself. The tracker
  template now restores `overflow:visible` at the same specificity
  (the first attempt, at lower specificity, was verified not to
  take effect), and the bar pins to the top again.

## 2026-11-03 — Full-width headers, card gaps, steppers, header bars

### Fixed

- Achievement headers now fill the whole card: the card was also
  acting as its own grid column, so Bootstrap's column padding inset
  the tinted header by 9px on each side and left the card borders
  touching with no horizontal gap. Cards are now a column wrapper
  around an inner card, so headers run edge to edge (clipped to the
  card's rounded corners) and there is a 16px gap between cards.
  Filtering still hides the whole wrapper, so no empty column is
  left behind.

### Added

- Counter inputs now have -/+ stepper buttons on either side for
  easy tapping, clamped at 0 and synced across shared counters; the
  tiny native number spinner is hidden so it does not duplicate them.
- Each counter's progress bar now lives right under its card header
  (matched by group and target, so shared counters with different
  thresholds still show their own percentage), instead of under the
  input at the bottom of the card.

## 2026-11-03 — Slim sticky progress bar, colorized headers

### Changed

- Only the progress bar sticks now: the Gamerscore progress card was
  split in two, so the slim card holding the title, counts and bar
  pins to the top while scrolling, and search, filters and the
  Order/Scope text scroll away normally. This supersedes the previous
  whole-card sticky behaviour.
- Achievement card headers are now colorized: a moss-green tint with
  a green rule underneath, stronger when the achievement is done, so
  the header stands out against the plain card body in both themes.
- Header elements are vertically centered with each other: state
  box, number, title and Gamerscore pill share one middle line.

## 2026-11-03 — Clickable card headers, sticky progress card

### Changed

- Each achievement card's header is now the toggle itself: a button
  holding the number, name and Gamerscore pill, with its state in
  `aria-pressed` and a small state box as the visual indicator. The
  small checkbox is gone; clicking anywhere in the header toggles.
  Save, export, import, step auto-tick and the "Incomplete only"
  filter all use the same id / Gamerscore contract as before, so
  existing saved progress carries over unchanged.
- The Gamerscore progress card is now sticky: it pins to the top of
  the viewport while scrolling (the navbar scrolls away first), so
  search, filters and the progress bar stay reachable, and it now
  has a full 1rem gap before the first section.

## 2026-11-03 — Review fixes

### Added

- `tools/test_generate.py`: stdlib-only unit tests for validation and
  rendering, run in CI.
- `data/schema.json`: human-readable JSON Schema for game data.
- `tools/config.py`: single source for the repo URL, shell versions
  and the vendor file list.
- `tools/fragments/`: card markup (achievement, step card, counter)
  moved out of Python f-strings into HTML fragments.
- `assets/js/theme-toggle.js`: shared theme toggle script, replacing
  identical inline copies in both templates.
- `assets/favicon.svg`, Open Graph tags, and a Dependabot config for
  GitHub Actions.
- Reusable `.github/workflows/check.yml`, called by both CI and Pages.

### Changed

- Hub and game pages are now deployed from a staged `_site/`
  directory (site files only) instead of the whole repo root.
- Game sections carry their own `filter_label` in the JSON; the
  code map in the generator is now only a fallback.
- README rewritten (Description, Prerequisites, Installation, Local
  Development, Deployment) with screenshots and an architecture
  diagram.

### Fixed

- Section titles are now HTML-escaped in rendered pages.
- The validator now fails cleanly (one-line error) on malformed
  shapes instead of raising KeyError/AttributeError.
- `gs` and counter targets now reject JSON `true` (bool is an int
  subclass in Python).
- Achievement checkboxes and counter inputs now have accessible
  names (`aria-label`).
- `check_js.py` no longer leaks temp files, now times out subprocess
  calls, and fails (instead of warning) on a page with no scripts.

## 2026-11-03 — Hub tidy

- "Adding a game?" contributor blurb removed from the landing page.
- Hub capped to the same 1100px column as game pages, card headers
  integrated, uniform 1rem gaps.
- Footer replaced with generator-rendered library totals plus a
  disclaimer and a source link.

## 2026-11-02 — v2-style tracker cards

- Game pages restyled inside the AdminLTE shell: contained column,
  integrated card headers, gold outline Gamerscore pill, moss-green
  accents, gradient progress bar, readable phase pills.
- Stale "self-contained" wording fixed in the hub and the generator.

## 2026-11-02 — Initial hub

- Pages hub with Minecraft Dungeons as game #1 (34 achievements,
  1,250G), AdminLTE shell vendored, MIT licence, CI + Pages
  workflows.
