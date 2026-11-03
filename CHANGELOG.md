# Changelog

All notable changes to this project are documented here. Dates are
when the change landed, not version numbers — this repo is not
versioned; the git log is the release history.

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
