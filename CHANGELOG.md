# Changelog

All notable changes to this project are documented here. Dates are
when the change landed, not version numbers — this repo is not
versioned; the git log is the release history.

## 2026-11-05 — Game #11: Moonlighter

### Added

- Moonlighter — all 57 achievements / 1,000G, the
  full game across five sections: Golem (trees,
  shop pricing, first shop upgrade, Golem King +
  perfect), Forest (second shop upgrade, Saver+/++,
  Carnivorous Mutae + perfect), Desert (Greedy,
  Banker, Luxury, Naja + perfect — the hardest),
  Tech & Finale (all five weapon trees as step
  checklists, Weapon Master, Emporium, Town Board,
  Notebook, decorations, Janitor, 10,000 kills,
  Energy Flux + perfect, final boss, under-40-deaths),
  and New Game+ (sub-10-hour speedrun, 100%). No
  DLC — Between Dimensions is out of scope, stated
  on the page. Gamerscore values come from
  GamesXtreme, cross-checked against
  mygamerprofile and verified by arithmetic
  (45×12 + 7×30 + 3×60 + 26 + 44 = 1,000); route
  notes are paraphrased from the TrueAchievements
  walkthrough by N18p73pwn3r (linked in the page
  sources). 7 missable flags: the four perfect
  boss kills, Janitor, Careful Merchant, and Gotta
  Go fast! — bosses are once per playthrough, so
  a missed perfect or broom finish waits for New
  Game+. About 25–30 hours. Library totals now 11
  games · 365 achievements · 11,250G.

## 2026-11-05 — Fix: Irresponsible babysitter order on Great God Grove

### Fixed

- Irresponsible babysitter moves from Chapter 4
  (#32) to Chapter 1, right after Shaboingboings
  and before H-h-h-historian (now #5). The
  walkthrough puts the beach-ball feed immediately
  after the bridge BizzyBoy and before the
  historian, and Justin confirmed it in-game —
  the Chapter 4 placement was a bad judgment
  call. Chapter subtitles updated (Ch 1: 11,
  Ch 4: 10); totals unchanged.

## 2026-11-04 — Shaboingboings full-size image

### Added

- The 1920×1080 original for the Shaboingboings
  shot, downloaded by Justin (the direct link
  returns 403 from this build box), is now vendored
  under `walkthrough/full/`, so the card has its
  "Open larger version" link like the other Grove
  shots. That closes the one exception noted in the
  fix entry below.

## 2026-11-04 — Fix: Shaboingboings image on Great God Grove

### Fixed

- Shaboingboings (#4) was missing its walkthrough shot:
  it now carries the BizzyBoy-on-the-bridge image with
  the snack-break phrase, captioned and credited like
  the other Grove shots. This one has no larger-version
  link: the 820w display version loads fine, but its
  1920×1080 original returns 403 from
  TrueAchievements, so the `full` field is omitted
  rather than linked to a dead URL. Grove now has 16
  media entries on 16 cards.
- Viewer fix found while verifying that card: the
  viewer binds `.ach-media a`, so an image with no
  `full` rendered as a bare `<img>` and never opened
  in the viewer. Images without `full` now link to
  their own display src (title "Open image"), in both
  media blocks and slideshow slides, so every shot
  opens in the viewer.

## 2026-11-04 — Game #10: Dragon Ball Xenoverse 2

### Added

- Dragon Ball Xenoverse 2 — 50 achievements /
  1,000G, the base game only, across six sections:
  Story (12 sagas from Raditz's Attack through
  Unknown History, plus the 70G ending sequence),
  Class tests (Easy/Kai/Super), Parallel Quests &
  Expert Missions (50% and full PQ completion, 7
  and all Expert Missions, all Challenge Quests),
  Online (first battle, 7 online wins, 7 endless
  wins), Conton City (26: Shenron and the four
  character wishes, all stages, Majin born/change,
  Frieza Force ranks, QQ Bang, Awoken Skills, half
  of skills/equipment/nicknames, Krillin and Yamcha
  training, level 80, all instructors' lessons),
  and Completion (the 0G Bye Bye, Xenoverse).
  The 11 DLC achievements (300G) are out of scope,
  stated on the page. No TrueAchievements
  walkthrough exists (it needs a new owner);
  Gamerscore values come from GamesXtreme and
  route notes from the GameFAQs trophy guide (both
  linked in the page sources), and the 1,000G total
  was verified by arithmetic against the confirmed
  values. About 60–80 hours. Library totals now 10
  games · 308 achievements · 10,250G.

## 2026-11-04 — Game #9: Wreckfest (Windows)

### Added

- Wreckfest (Windows) — all 20 achievements /
  1,000G, the full game across four sections:
  Career (first win, 5 championships in order, all
  career challenges), Ranks & garage (ranks 10/25/50
  on a shared counter, 10/20 vehicles on a shared
  counter, 50,000 credits), Wrecking & stunts
  (100 wrecks, 100 times wrecked, 50 School Bus
  wrecks, 5 minutes airborne, 1 hour in the Lawn
  Mower, 210 km/h in the Rocket), and Multiplayer
  (20 event wins, private-lobby boostable; AI wins
  don't count). No TrueAchievements walkthrough
  exists; Gamerscore values come from the CheatCC
  table and route notes from the Knoef/Fuzionbyte
  guides (all linked in the page sources). About
  15–20 hours. Library totals now 9 games · 258
  achievements · 9,250G.

## 2026-11-04 — Game #8: Relic Hunters Legend

### Added

- Relic Hunters Legend — all 18 achievements /
  1,000G, the full game in story order across two
  sections: 13 chapters and adventures (first story
  mission through Act 3) plus 5 progression
  achievements (new Hunter, levels 6 and 30 on one
  shared Hunter-level counter, first Relic, first
  Treasure Map). No TrueAchievements walkthrough
  exists, so chapter order follows a completed
  playthrough's unlock sequence and Gamerscore
  values come from that playthrough's profile page
  (both linked in the page sources). About 40–50
  hours. Library totals now 8 games · 238
  achievements · 8,250G.

## 2026-11-04 — Game #7: GoldenEye 007

### Added

- GoldenEye 007 — all 55 achievements / 1,000G, the
  full game in walkthrough order across four
  sections: 20 story missions (18 story + Aztec and
  Egyptian bonus missions), 3 difficulty completions,
  21 cheat time trials (each with its mission,
  difficulty, and par time), and 11 multiplayer
  achievements with step checklists for the 11 maps,
  14 weapon sets, and 7 scenarios, plus counters for
  the 10 matches and 100 kills. No missables; about
  15–20 hours across 3 playthroughs plus the
  split-screen cleanup. Note: TrueAchievements
  blocked direct fetches while this game was being
  built, so the achievement list came from its cached
  pages and Gamerscore values were cross-checked
  against the Pure Xbox list (linked in the page
  sources). Library totals now 7 games · 220
  achievements · 7,250G.

## 2026-11-04 — Game #6: 1000xRESIST

### Added

- 1000xRESIST — all 32 achievements / 1,000G, the full
  game in story order across five sections: prologue
  and Chapter 1, Chapters 2–4 with the Orchard
  landmarks, Chapters 5–6, Chapters 7–X, and the
  endings. The seven talk-to-everyone achievements are
  flagged missable (they must be done before each
  section's confirmation interaction, and most
  characters can't be spoken to twice), the five
  Orchard landmarks carry navigation from the Level 1
  waterfall, and each ending carries its epilogue
  light combination. No TrueAchievements walkthrough
  exists, so route notes are paraphrased from the
  Steam 100% guide (linked in the page sources).
  Library totals now 6 games · 165 achievements ·
  6,250G.

## 2026-11-04 — Game #5: Winter Burrow

### Added

- Winter Burrow — all 32 achievements / 1,000G, the full
  game in walkthrough order (wolfnflowers on
  TrueAchievements) across five sections: the beginning
  (bed, armchair, stove, bridge, basement), following
  the owl (Gnarled Oaks, Shadow Pines, campfire, Aunty
  home), Aunty's recovery (first floor, Bufo, White
  Pillars, flint tools, Willow), rebuilding the burrow
  (burrow repair, Gnawtusk, Moss, the feast), then the
  furnishing cleanup. Thirteen counters cover the
  cumulative totals (wood, kills, yarn, clothing,
  recipes, furniture sets, woodworking). No missables;
  about 8–10 hours. Library totals now 5 games · 133
  achievements · 5,250G.

## 2026-11-04 — Game #4: Pigeon Simulator

### Added

- Pigeon Simulator — all 10 achievements / 1,000G, the full
  game in walkthrough order (MarkLaing07 on
  TrueAchievements): cheese the three tutorial gadgets
  first (Revealer 30, Stabilizer 20, Seal 10 — each with
  its own counter), then the first missions including
  the deliberate day-1 failure, then the grind to 50
  anomalies and all $27,860 of upgrades in one life
  (the four upgrade categories as steps). No missables;
  about 1–2 hours. Library totals now 4 games · 101
  achievements · 4,250G.

## 2026-11-04 — Even card headers, viewer side-tap

### Changed

- Card headers no longer stagger: long names shrink toward
  a floor (1.05rem down to 0.85rem) before they are allowed
  to wrap, and headers in the same visible row are then
  equalised to the row's tallest, so card bodies start on
  one line. Re-runs after every filter pass, on resize,
  when a section opens or closes, and once fonts arrive;
  the How demos get the same treatment, scoped to their
  grid.
- Viewer slideshow navigation is now centered under the
  caption as one group, instead of spread to the edges,
  and tapping the left or right side of the image steps
  it too (buttons underneath stay the discoverable
  control; the image gets a pointer cursor while a
  slideshow is open).

## 2026-11-04 — Credit on hover, viewer steps through slideshows

### Changed

- "Image: TrueAchievements" no longer sits as a permanent
  line under every card image: the credit is now a small
  overlay on the image itself, shown on hover (or keyboard
  focus) and never blocking the click. It stays in the
  viewer caption and in the failed-load placeholder, so
  attribution is not lost — and on touch screens, where
  there is no hover, the viewer is where the credit is
  seen.
- The image viewer gains Previous/Next for slideshow
  shots (with a "N of M" count and arrow-key support),
  hidden for standalone images. Viewer navigation drives
  the card's own slideshow buttons, so the card and the
  viewer never disagree about which slide is current.

## 2026-11-04 — Notes move to per-card icons, slideshow stops jumping

### Changed

- The bottom "My notes" section and its sidebar link are
  gone. Notes now live behind a note icon on every
  achievement card and one on the filter card for
  game-wide notes; tapping an icon opens a popup that
  saves as you type, and the icon swaps to a check while
  its note is set. Storage changed from one string to
  one object (`game` + one key per card id); old saves
  and exports holding a string migrate it to the game
  key on load, and Reset clears the object. The Xbox
  sync path still never touches notes.
- Slideshow cards no longer change height as you step
  through slides: slides now stack in one grid cell, so
  the card renders at the tallest slide's height from
  the start. Hidden slides are pulled out of tab order
  by the nav script, since they are visibility-hidden
  rather than gone.

### Added

- The How page demos gain the slideshow card type
  (INSPEKTA, live, sandboxed like the rest), including
  the image viewer for its slide images. Demo cards
  have their note buttons stripped: the How page has no
  notes popup for them to open.

## 2026-11-04 — Game #3: Barbie Horse Trails

### Added

- Barbie Horse Trails: all 15 achievements / 1,000G in
  story/roadmap order, one section, one counter (Horse
  Bond level, target 11, on Bonded). No missables, no
  steps, no media: no walkthrough screenshots were
  captured, and none were lifted from the guides.
- No TrueAchievements walkthrough exists for this game
  (checked: its walkthrough page carries no guide), so
  the route notes are paraphrased from two full guides
  instead: ScorpioOfShadows (roadmap order, mission
  names) and Knoef (packet bar, side-quest markers,
  bond level 11, checkered-flag races). Both are linked
  in the page sources alongside TA. Hub now lists 3
  games (91 achievements, 3,250G).

## 2026-11-04 — Slideshow guide cards (INSPEKTA first)

### Added

- Achievements gain an optional `slideshow`: an ordered
  step-by-step guide rendered one slide at a time with
  Previous/Next buttons (first slide shown, ends disable
  their button) and a "N of M" count. Slides reuse the media
  entry shape (src, optional full, caption, credit, alt) and
  slide images open in the same viewer as media images. The
  media validation was refactored into one shared entry
  check used by both lists.
- INSPEKTA is the first slideshow card (3 slides, both
  sizes cached like the other shots): grab the 'IT'S
  MEGAPON!' phrase from Vib by the net, show it to Capochin
  to get into the van, then meet Inspekta inside. The card's
  route note alone never said how to get into the van, which
  is exactly the gap a slideshow fills. Route-note text
  stays paraphrased; game phrases stay exact.

### Fixed

- The INSPEKTA slideshow first shipped starting at Vib,
  dropping the opening of the chain: it now starts with
  the Bug Wurth / Lumber Jacqueline lead-up (free Bug
  Wurth, deliver his letter, bring back the crush phrase
  to cross her bridge, past the BizzyBoys) for 5 slides
  total, with the annotated location shot cached at both
  sizes. A test guards the slideshow opening on that shot
  so it can't be dropped again.
- The slideshow then gained a 6th slide: the van sequence
  had ended at "work through the dialogue" without the
  collect-and-shoot-back beat — collecting the TOGETHA
  phrase, shooting it back at the deputy question instead
  of nodding, then the snack-break phrase and the
  automatic exit. The guard test now also checks the last
  slide carries that beat.

## 2026-11-04 — Walkthrough shots open in an on-page viewer

### Changed

- Tapping a walkthrough shot now opens its full-size version
  in a modal viewer on the same page (native `<dialog>`,
  captioned, closable by the close button, Escape, or tapping
  outside) instead of a new tab. The link itself is kept, so
  without scripts the shot still opens in a new tab. A test
  guards the dialog sitting before the page script that wires
  it up — the first placement put it after the script, where
  the wiring would have found nothing.

## 2026-11-04 — Icons removed, walkthrough shots open full-size

### Removed

- The 42 achievement icons from Grove cards (entries and the
  `assets/media/great-god-grove/icons/` files). They identified
  the cards but did not help with the guide; the walkthrough
  screenshots are the images that matter.

### Added

- Media entries gain an optional `full` field: the displayed
  image links to a larger version, opening in a new tab. All
  15 Grove walkthrough shots now link to their 1920×1080
  originals under `assets/media/great-god-grove/walkthrough/full/`
  (3MB total), so tapping a shot shows the full scene.

## 2026-11-04 — Inline walkthrough screenshots on Grove cards

### Added

- 13 inline screenshots from the TrueAchievements walkthrough,
  as 15 media entries on 15 Grove cards (the bakery and
  barracks TV-and-bunny shots each illustrate two cards: the
  video and the bunny). Each sits after the card's icon, with
  a caption naming what it shows and "Image:
  TrueAchievements" credit. Mapping rule, kept strict: only
  shots that directly show an achievement's trigger or
  location were attached (the entrance-gate bunny for him, the
  TVs for each video, the historian, the haircut, the sneeze,
  the Clicky Tower video, the HobbyHoo bunny, the click-clack
  editing, the prom dance, the final rift toss). The
  walkthrough's other ~90 inline shots are route aids for
  phrases and steps, or sequences whose achievement trigger
  could not be pinned down, so they were left out rather than
  guessed — the media mechanism supports adding more later.
  Shots are the 820w versions (674K total), cached in the
  repo under `assets/media/great-god-grove/walkthrough/`, so
  they load from the site itself like the icons. The icons
  from the previous commit stay: they identify the cards,
  these shots show how to get them.

## 2026-11-04 — Guide images on Grove cards, with credit and fallback

### Added

- Every Great God Grove card now shows its achievement icon
  under the route note, matched by exact achievement name +
  Gamerscore (all 42 verified, no guessing) and cached in the
  repo under `assets/media/great-god-grove/icons/` (64px, 168K
  total). Hotlinking was tried first and does not work:
  TrueAchievements serves an icon fine direct (HTTP 200) but
  blocks it embedded in another page (0 of 42 loaded in a real
  browser, all swapped to the placeholder). Each icon is
  credited ("Image: TrueAchievements") under the image, and
  the page's sources link the walkthrough itself. Images are
  lazy-loaded (`loading="lazy"`, so off-screen cards cost
  nothing until scrolled to) and served from the site itself,
  so they cache with the rest of the page.
- Media entries gain an optional `credit` field, rendered as an
  "Image: …" line. A guide image that fails to load (moved, or
  the host blocks loading it here) is swapped by page script for
  a dashed placeholder explaining why, instead of a
  broken-image icon.

## 2026-11-04 — Hub card spacing + CI ruff fix

### Fixed

- Home game cards touched side by side (measured gap 0px at
  1440px): the card itself was the grid column, and Bootstrap's
  horizontal gutter is column padding, which sits inside a
  card-as-column's border. Cards now sit inside their columns
  (`col-12 col-md-6` wrapper + inner `card h-100`), so the gutter
  separates them — measured 16px at 1440px and stacked. A test
  guards the nesting so the structure cannot regress silently.
- CI `ruff check tools/` failed with 3 E501 lines over 100 chars
  in `tools/generate.py` (media validation messages, image tag).
  Messages shortened, tag split; `ruff check tools/` is clean.

## 2026-11-04 — Missable pills and card media

### Added

- `missable: true` on an achievement renders a red Missable pill
  in the header (a choice or one-time window); the How page
  explains it. Great God Grove flags its two deputy answers, the
  only missables the walkthrough identifies (the cloud-save trick
  covers both in one run); Dungeons flags none.
- `media` on an achievement renders screenshots/clips under the
  route note: images as lazy `<img>`, clips as `<video>` for media
  files or a privacy-enhanced YouTube embed for YouTube URLs.
  Sources are `assets/` paths (files under `assets/media/<slug>/`)
  or `https://` URLs, enforced by the generator. No media ships
  yet — captures must be real, never mocked, so cards gain media
  as genuine screenshots/clips are added.

## 2026-11-04 — Microsoft export import removed, explained on How page

### Removed

- The "Import from a Microsoft export" card from every game page
  (fragment, template placeholder, and its parser/analysis script).
  The Xbox sync card and its shared preview/apply machinery are
  untouched, and progress Export/Import is a separate feature and
  stays.

### Added

- "We tried the Microsoft export" on the How it works page: the
  Privacy Dashboard archive was tried and holds app/service usage
  (which apps were opened and when, plus searches) — no achievement
  names, unlock dates, or Gamerscore — so there was nothing to match
  and the import would have reported "no achievement records found"
  for every game. The section names the working alternatives (Xbox
  sync on mapped games, ticking by hand) and says the import can
  return if Microsoft ever ships achievement records in the archive.

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
