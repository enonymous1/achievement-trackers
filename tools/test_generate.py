#!/usr/bin/env python3
"""Tests for tools/generate.py. Run from the repo root:

    python3 -m unittest discover -s tools -v

Deliberately stdlib-only (unittest): the project has no Python
dependencies, and this file must not become the first one.
"""

import unittest
from pathlib import Path

from generate import (
    load_games,
    render_achievement,
    render_demos,
    render_game,
    render_how,
    render_hub,
    render_json_example,
    render_media,
    render_sections,
    render_slideshow,
    render_xbox_sync_card,
    sidebar_how_href,
    sidebar_menu,
    validate_game,
)
from map_xbox import (
    MatchError,
    apply_mapping,
    entry_gamerscore,
    extract_achievements,
    match_entries,
)


def make_game(**overrides):
    game = {
        "slug": "test",
        "title": "Test",
        "tagline": "T",
        "order_note": "O",
        "scope_note": "S",
        "storage_key": "test-key",
        "sources": [{"label": "S", "url": "https://example.com"}],
        "total_gs": 10,
        "total_count": 1,
        "sections": [
            {
                "id": "story",
                "title": "Story",
                "filter_label": "Story",
                "achievements": [
                    {"id": "a1", "name": "A", "gs": 10, "req": "R", "how": "H"}
                ],
            }
        ],
    }
    game.update(overrides)
    return game


class TestValidate(unittest.TestCase):
    def test_valid_game_passes(self):
        game = validate_game("test.json", make_game())
        self.assertEqual(game["_total_gs"], 10)
        self.assertEqual(game["_total_count"], 1)

    def test_gs_mismatch_fails(self):
        with self.assertRaises(SystemExit):
            validate_game("test.json", make_game(total_gs=999))

    def test_count_mismatch_fails(self):
        with self.assertRaises(SystemExit):
            validate_game("test.json", make_game(total_count=2))

    def test_bool_gs_fails(self):
        game = make_game()
        game["sections"][0]["achievements"][0]["gs"] = True
        with self.assertRaises(SystemExit):
            validate_game("test.json", game)

    def test_zero_gs_passes(self):
        # Genuine 0G achievements exist (e.g. Xenoverse 2's
        # completion achievement); they must validate and sum as 0.
        game = make_game(total_gs=10, total_count=2)
        game["sections"][0]["achievements"].append(
            {"id": "a0", "name": "Z", "gs": 0, "req": "R", "how": "H"}
        )
        validated = validate_game("test.json", game)
        self.assertEqual(validated["_total_gs"], 10)
        self.assertEqual(validated["_total_count"], 2)

    def test_duplicate_achievement_id_fails(self):
        game = make_game()
        game["sections"][0]["achievements"].append(
            {"id": "a1", "name": "B", "gs": 10, "req": "R", "how": "H"}
        )
        game["total_gs"] = 20
        game["total_count"] = 2
        with self.assertRaises(SystemExit):
            validate_game("test.json", game)

    def test_missing_achievement_id_fails_cleanly(self):
        game = make_game()
        del game["sections"][0]["achievements"][0]["id"]
        with self.assertRaises(SystemExit):
            validate_game("test.json", game)

    def test_non_object_top_level_fails_cleanly(self):
        with self.assertRaises(SystemExit):
            validate_game("test.json", ["not", "a", "dict"])

    def test_slug_must_match_filename(self):
        with self.assertRaises(SystemExit):
            validate_game("other.json", make_game())

    def test_source_must_be_https(self):
        game = make_game()
        game["sources"] = [{"label": "S", "url": "http://example.com"}]
        with self.assertRaises(SystemExit):
            validate_game("test.json", game)


def make_xbox_game():
    game = make_game(xbox_title_id="1234567890")
    game["sections"][0]["achievements"][0]["xbox_id"] = "7"
    return game


class TestXboxValidation(unittest.TestCase):
    def test_synced_game_passes(self):
        game = validate_game("test.json", make_xbox_game())
        self.assertEqual(game["_achievements"][0]["xbox_id"], "7")

    def test_title_id_must_be_digits(self):
        with self.assertRaises(SystemExit):
            validate_game("test.json", make_game(xbox_title_id="abc"))

    def test_missing_xbox_id_fails(self):
        with self.assertRaises(SystemExit):
            validate_game("test.json", make_game(xbox_title_id="123"))

    def test_duplicate_xbox_id_fails(self):
        game = make_xbox_game()
        game["sections"][0]["achievements"].append(
            {"id": "a2", "name": "B", "gs": 10, "req": "R", "how": "H",
             "xbox_id": "7"})
        game["total_gs"] = 20
        game["total_count"] = 2
        with self.assertRaises(SystemExit):
            validate_game("test.json", game)

    def test_xbox_id_without_title_fails(self):
        game = make_game()
        game["sections"][0]["achievements"][0]["xbox_id"] = "7"
        with self.assertRaises(SystemExit):
            validate_game("test.json", game)

    def test_missable_badge_and_media_render(self):
        base = {"id": "a1", "name": "A", "gs": 10, "req": "R", "how": "H"}
        plain = render_achievement(dict(base), 1)
        self.assertNotIn("Missable", plain)
        self.assertNotIn("ach-media", plain)
        flagged = render_achievement(dict(base, missable=True), 1)
        self.assertIn("Missable", flagged)
        self.assertIn("can be passed without popping", flagged)
        media = render_achievement(dict(base, media=[
            {"type": "image", "src": "assets/media/x.png", "alt": "Alt", "caption": "Cap"},
            {"type": "image", "src": "https://example.com/i.jpg", "credit": "Guide"},
            {"type": "video", "src": "assets/media/x.mp4"},
            {"type": "video", "src": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"},
        ]), 1)
        self.assertIn('<img src="../assets/media/x.png" alt="Alt"', media)
        self.assertIn("<figcaption", media)
        # Credit is a hover overlay on the image now, not a
        # permanent caption line — but it is still rendered.
        self.assertIn('<span class="media-credit">Image: Guide</span>', media)
        self.assertIn('<img src="https://example.com/i.jpg"', media)
        linked = render_achievement(dict(base, media=[
            {"type": "image", "src": "assets/media/x.png",
             "full": "assets/media/x-full.png"},
        ]), 1)
        self.assertIn('<a href="../assets/media/x-full.png" target="_blank"', linked)
        self.assertIn('title="Open larger version"', linked)
        self.assertIn('<video controls', media)
        self.assertIn("youtube-nocookie.com/embed/dQw4w9WgXcQ", media)
        template = (Path(__file__).parent / "template.html").read_text()
        self.assertIn("ach-media-fallback", template)
        self.assertIn("Guide image unavailable", template)
        # The viewer dialog must sit before the page script that
        # wires it up, or getElementById finds nothing.
        self.assertLess(template.index('<dialog id="media-modal"'),
                        template.index("modal.showModal"))

    def test_bad_missable_and_media_fail_validation(self):
        game = make_game()
        game["sections"][0]["achievements"][0]["missable"] = "yes"
        with self.assertRaises(SystemExit):
            validate_game("test.json", game)
        for bad in (
            {"type": "audio", "src": "assets/media/x.mp3"},
            {"type": "image", "src": "/tmp/x.png"},
            {"type": "image", "src": "assets/media/x.png", "credit": 5},
            {"type": "image", "src": "assets/media/x.png", "full": "/tmp/x.png"},
            {"type": "video", "src": "https://example.com/page"},
        ):
            game = make_game()
            game["sections"][0]["achievements"][0]["media"] = [bad]
            with self.assertRaises(SystemExit):
                validate_game("test.json", game)

    def test_slideshow_renders_with_first_slide_active(self):
        base = {"id": "a1", "name": "A", "gs": 10, "req": "R", "how": "H"}
        self.assertEqual(render_slideshow(dict(base)), "")
        html = render_slideshow(dict(base, slideshow=[
            {"src": "assets/media/s1.png", "full": "assets/media/s1-full.png",
             "caption": "Step one", "credit": "Guide"},
            {"src": "assets/media/s2.png", "caption": "Step two"},
        ]))
        self.assertIn('class="slideshow-slide active"', html)
        self.assertIn('class="slideshow-slide"', html)
        self.assertIn("1 of 2", html)
        self.assertIn("slideshow-prev", html)
        self.assertIn("slideshow-next", html)
        self.assertIn('<a href="../assets/media/s1-full.png"', html)
        self.assertIn("Step one", html)
        self.assertIn('<span class="media-credit">Image: Guide</span>', html)
        self.assertNotIn("Step one Image: Guide", html)
        full = render_achievement(dict(base, slideshow=[
            {"src": "assets/media/s1.png", "caption": "Step one"},
        ]), 1)
        self.assertIn('class="slideshow mt-2"', full)

    def test_bad_slideshow_fails_validation(self):
        game = make_game()
        game["sections"][0]["achievements"][0]["slideshow"] = "nope"
        with self.assertRaises(SystemExit):
            validate_game("test.json", game)
        for bad in (
            {"caption": "No src"},
            {"src": "/tmp/s.png"},
            {"src": "assets/media/s.png", "full": "notaurl"},
        ):
            game = make_game()
            game["sections"][0]["achievements"][0]["slideshow"] = [bad]
            with self.assertRaises(SystemExit):
                validate_game("test.json", game)

    def test_inspekta_slideshow_starts_with_bug_wurth(self):
        """The INSPEKTA slideshow must open with the Bug Wurth /
        Lumber Jacqueline lead-up: dropping it strands the
        reader at Vib with no route to the van."""
        game = next(g for g in load_games() if g["slug"] == "great-god-grove")
        inspekta = next(
            a for s in game["sections"] for a in s["achievements"]
            if a["id"] == "ach-inspekta")
        slides = inspekta["slideshow"]
        self.assertEqual(len(slides), 6)
        self.assertIn("TOGETHA", slides[-1]["caption"])
        self.assertTrue(slides[0]["src"].endswith("lumber-jacqueline-location.jpg"))
        self.assertTrue(slides[1]["src"].endswith("lumber-jacqueline-location.jpg"))

    def test_shaboingboings_has_snack_break_image(self):
        """Shaboingboings (#4) must carry its walkthrough shot:
        the BizzyBoy on the bridge with the snack-break phrase.
        It shipped without one and the gap was caught from a
        reader's screenshot."""
        game = next(g for g in load_games() if g["slug"] == "great-god-grove")
        shaboing = next(
            a for s in game["sections"] for a in s["achievements"]
            if a["id"] == "ach-shaboing")
        self.assertEqual(len(shaboing["media"]), 1)
        self.assertTrue(
            shaboing["media"][0]["src"].endswith("bizzyboy-snack-break.jpg"))

    def test_media_without_full_links_to_itself(self):
        """A media image with no larger version must still open
        in the viewer: the viewer binds .ach-media links, so a
        bare <img> would never open. It links to its own
        display src instead."""
        html = render_media({"name": "N", "media": [
            {"type": "image", "src": "assets/media/x.jpg",
             "caption": "C", "credit": "T"}]})
        self.assertIn(
            '<a href="../assets/media/x.jpg" target="_blank" '
            'rel="noopener" title="Open image">', html)

    def test_hub_game_cards_are_nested_in_columns(self):
        # Regression: a card that IS the column touches its
        # neighbour — the horizontal gutter is column padding, which
        # sits inside a card-as-column's border and leaves zero
        # visible gap. The card must sit inside the column so the
        # gutter separates the two cards.
        html = render_hub([validate_game("test.json", make_game())])
        self.assertIn('<div class="game item col-12 col-md-6"', html)
        self.assertIn('<div class="card h-100">', html)
        self.assertNotIn("card col-12", html)

    def test_hub_sort_control(self):
        # The hub carries a sort control (name / completion /
        # achievements / started), remembered across visits, and
        # each card carries the static values sorting needs.
        html = render_hub([validate_game("test.json", make_game())])
        self.assertIn('id="sort"', html)
        self.assertIn('value="completion"', html)
        self.assertIn('value="achievements"', html)
        self.assertIn('value="started"', html)
        self.assertIn('data-count="1"', html)
        self.assertIn('data-gs="10"', html)
        self.assertIn('data-slug="test"', html)
        template = (Path(__file__).parent / "hub_template.html").read_text()
        self.assertIn("at-hub-sort", template)
        self.assertIn("sortCards", template)

    def test_no_privacy_import_on_game_pages(self):
        # The Microsoft export import was removed (the archive holds
        # app usage, not achievement records); its explainer lives on
        # the How page instead. Game pages must not render the card,
        # and the template must not still carry its placeholder.
        html = render_game(validate_game("test.json", make_game()), [])
        self.assertNotIn('id="privacy-import"', html)
        self.assertNotIn('id="privacy-files"', html)
        template = (Path(__file__).parent / "template.html").read_text()
        self.assertNotIn("@@PRIVACY_IMPORT_CARD@@", template)
        self.assertNotIn("privacy_import", template)
        how = (Path(__file__).parent / "how_template.html").read_text()
        self.assertIn("We tried the Microsoft export", how)

    def test_sync_card_only_for_synced_games(self):
        self.assertEqual(render_xbox_sync_card(make_game()), "")
        game = validate_game("test.json", make_xbox_game())
        card = render_xbox_sync_card(game)
        self.assertIn('data-xbox-title-id="1234567890"', card)
        self.assertIn('&quot;7&quot;: &quot;a1&quot;', card)
        template = (Path(__file__).parent / "template.html").read_text()
        self.assertIn("@@XBOX_SYNC_CARD@@", template)


class TestMapXbox(unittest.TestCase):
    def test_extract_shapes(self):
        entries = [{"id": "1", "name": "A"}]
        self.assertEqual(extract_achievements(entries), entries)
        self.assertEqual(
            extract_achievements({"achievements": entries}), entries)
        self.assertIsNone(extract_achievements({"titles": []}))

    def test_gamerscore_from_rewards(self):
        entry = {"rewards": [{"name": "Gamerscore", "value": "30"},
                             {"name": "Other", "value": "5"}]}
        self.assertEqual(entry_gamerscore(entry), 30)
        self.assertEqual(entry_gamerscore({"gamerscore": 10}), 10)
        self.assertIsNone(entry_gamerscore({}))

    def test_match_exact_then_normalized(self):
        achs = [{"id": "a1", "name": "Cha-ching!", "gs": 30},
                {"id": "a2", "name": "Wooden Sword", "gs": 10}]
        entries = [{"id": "9", "name": "Cha-ching!",
                    "rewards": [{"name": "Gamerscore", "value": "30"}]},
                   {"id": "3", "name": "Wooden Sword "}]
        mapping, report = match_entries(achs, entries)
        self.assertEqual(mapping, {"a1": "9", "a2": "3"})
        self.assertEqual(report[1][2], "normalized")

    def test_match_unmatched_and_ambiguous_fail(self):
        achs = [{"id": "a1", "name": "Missing", "gs": 10}]
        with self.assertRaises(MatchError):
            match_entries(achs, [{"id": "1", "name": "Other"}])
        achs = [{"id": "a1", "name": "Same", "gs": 10}]
        entries = [{"id": "1", "name": "Same"}, {"id": "2", "name": "Same"}]
        with self.assertRaises(MatchError):
            match_entries(achs, entries)

    def test_apply_mapping_is_surgical(self):
        game = validate_game("test.json", make_game())
        text = ('{\n  "slug": "test",\n  "sections": [],\n'
                '  "ach": {"id": "a1", "name": "A", "gs": 10}\n}\n')
        out = apply_mapping(text, game, "123", {"a1": "7"})
        self.assertIn('"xbox_title_id": "123"', out)
        self.assertIn('{"id": "a1", "xbox_id": "7",', out)
        self.assertEqual(out.count("xbox_id"), 1)
        game2 = validate_game("test.json", make_xbox_game())
        with self.assertRaises(MatchError):
            apply_mapping(text, game2, "123", {"a1": "7"})


class TestRender(unittest.TestCase):
    def test_section_title_is_escaped(self):
        game = make_game()
        game["sections"][0]["title"] = '<b>Bold & "quoted"</b>'
        html = render_sections(game)
        self.assertNotIn("<b>Bold", html)
        self.assertIn("&lt;b&gt;Bold", html)
        self.assertIn("&amp;", html)

    def test_first_section_open_rest_collapsed(self):
        game = make_game()
        game["sections"].append(
            {"id": "second", "title": "Second", "achievements": [] ,
             "step_cards": [{"title": "T", "how": "H",
                             "steps": [{"id": "s1", "label": "L"}]}]}
        )
        html = render_sections(game)
        self.assertIn('<details open data-cat="story">', html)
        self.assertIn('<details data-cat="second">', html)

    def test_counter_bar_and_steppers(self):
        # The bar lives under the header (before the card body), the
        # input gets -/+ steppers, and both are matched by group.
        game = make_game()
        game["sections"][0]["achievements"][0]["counters"] = [
            {"group": "mobs", "target": 50}
        ]
        html = render_sections(game)
        self.assertIn('class="progress counter-bar', html)
        self.assertLess(html.index("counter-bar"), html.index("card-body"))
        self.assertIn('data-step="-1"', html)
        self.assertIn('data-step="1"', html)
        self.assertIn('data-counter="mobs"', html)

    def test_counter_stops_at_max_with_confirm(self):
        # Steppers stop at the card's own target: pushing past it
        # pops a yes/no gate, and Yes only unlocks that card for
        # the visit (in-memory override, never saved). Typed values
        # are gated on change, and declining reverts to the
        # pre-edit value. The How page demos share the guard.
        template = (Path(__file__).parent / "template.html").read_text()
        self.assertIn("Max reached", template)
        self.assertIn("Add anyway?", template)
        self.assertIn("overMax", template)
        self.assertIn("_prev", template)
        how = (Path(__file__).parent / "how_template.html").read_text()
        self.assertIn("Max reached", how)
        self.assertIn("Add anyway?", how)

    def test_progress_lives_in_sticky_header(self):
        # The top bar is frozen and carries the compact progress
        # (text already lived there; the thin bar along its bottom
        # edge mirrors the card's bar). The big progress card is
        # no longer sticky — it scrolls away with the page.
        template = (Path(__file__).parent / "template.html").read_text()
        self.assertIn(".app-header{position:sticky;top:0", template)
        self.assertIn('id="overallBarNav"', template)
        self.assertIn("overallBarNav.style.width", template)
        self.assertNotIn("progress-card{position:sticky", template)

    def test_header_freezes_on_hub_and_how_pages(self):
        # The Home and How pages have no progress card, but the
        # top bar freezes the same way, so the sidebar toggle
        # stays reachable while scrolling.
        for name in ("hub_template.html", "how_template.html"):
            template = (Path(__file__).parent / name).read_text()
            self.assertIn(".app-header{position:sticky;top:0", template)

    def test_theme_toggle_is_icon(self):
        # The toggle is an icon-only button (moon in light mode,
        # sun in dark mode), matching the icon-only sidebar toggle
        # and note buttons — not a text button.
        for name in ("template.html", "hub_template.html", "how_template.html"):
            html = (Path(__file__).parent / name).read_text()
            self.assertIn('<i class="bi bi-moon-fill"', html)
            self.assertNotIn(">Theme</button>", html)
        js = (Path(__file__).parent.parent / "assets" / "js"
              / "theme-toggle.js").read_text()
        self.assertIn("bi-sun-fill", js)
        self.assertIn("bi-moon-fill", js)
        self.assertNotIn("textContent", js)

    def test_ticking_achievement_fills_sub_requirements(self):
        # Clicking an achievement header fills its sub-requirements
        # (all steps checked, counters raised to target) and
        # unchecking clears them (steps unchecked, counters dropped
        # to what a still-ticked sibling needs, or 0). The How
        # page demos share the behaviour.
        template = (Path(__file__).parent / "template.html").read_text()
        self.assertIn("syncSubRequirements", template)
        self.assertIn("fills its sub-requirements", template)
        how = (Path(__file__).parent / "how_template.html").read_text()
        self.assertIn("syncDemoSubs", how)

    def test_sidebar_menu_groups_by_letter(self):
        # Games sit under A–Z letter headers (digits under '#'),
        # sorted by title — the flat list is gone.
        games = [
            make_game(slug="b", title="Barbie"),
            make_game(slug="a", title="1000xRESIST"),
            make_game(slug="m", title="Moonlighter"),
        ]
        html = sidebar_menu(games, "./", "home")
        self.assertIn('<li class="nav-header">#</li>', html)
        self.assertIn('<li class="nav-header">B</li>', html)
        self.assertIn('<li class="nav-header">M</li>', html)
        self.assertLess(html.index("#</li>"), html.index("B</li>"))
        self.assertLess(html.index("B</li>"), html.index("M</li>"))
        self.assertLess(html.index("1000xRESIST"), html.index("Barbie"))

    def test_sidebar_menu_and_how_href(self):
        games = [make_game(), make_game(slug="other", title="Other")]
        html = sidebar_menu(games, "../", "test")
        self.assertIn('href="../"', html)
        self.assertIn('href="../other/"', html)
        self.assertIn("Games</li>", html)
        # The old Notes section and its sidebar link are gone:
        # notes live behind per-card icons now.
        self.assertNotIn('#notes-section', html)
        self.assertEqual(sidebar_how_href("../", "test"), "../how-it-works/")
        self.assertEqual(sidebar_how_href("../", "how"), "./")

    def test_step_bar_and_step_card_centering(self):
        # Multi-step achievements get a step bar under the header,
        # matched to their steps by parent id; step cards get the
        # centering class instead of a bar.
        game = make_game()
        ach = game["sections"][0]["achievements"][0]
        ach["steps"] = [{"id": "s1", "label": "One"}, {"id": "s2", "label": "Two"}]
        game["sections"].append({
            "id": "secrets", "title": "Secrets", "filter_label": "Secrets",
            "step_cards": [{"title": "Secret", "how": "How",
                           "steps": [{"id": "sc1", "label": "Go"}]}],
        })
        html = render_sections(game)
        self.assertIn('class="progress step-bar', html)
        self.assertIn('data-step-parent="a1"', html)
        self.assertIn('class="ach step-card card', html)
        # A single step is not enough for a bar: it would just
        # mirror the achievement's own tick.
        game2 = make_game()
        game2["sections"][0]["achievements"][0]["steps"] = [
            {"id": "s1", "label": "Only"}
        ]
        self.assertNotIn("step-bar", render_sections(game2))

    def test_how_page_demos(self):
        # Demos are rendered from the real game data, with
        # demo-prefixed ids, and a missing source game fails loudly
        # instead of shipping empty demo slots.
        game = make_game(slug="minecraft-dungeons")
        grove = make_game(slug="great-god-grove")
        grove["sections"][0]["achievements"][0] = {
            "id": "ach-inspekta", "name": "INSPEKTA", "gs": 15,
            "req": "R", "how": "H",
            "slideshow": [{"src": "assets/media/s1.png", "caption": "Step one"}],
        }
        ach = game["sections"][0]["achievements"][0]
        ach["id"] = "ach-happy"
        game["sections"][0]["achievements"].append({
            "id": "ach-highdry", "name": "High", "gs": 80,
            "req": "R", "how": "H",
            "steps": [{"id": "s1", "label": "One"},
                      {"id": "s2", "label": "Two"},
                      {"id": "s3", "label": "Three"}],
        })
        game["sections"][0]["achievements"].append({
            "id": "ach-wooden", "name": "Wood", "gs": 10,
            "req": "R", "how": "H",
            "counters": [{"group": "mobs", "target": 50}],
        })
        game["sections"].append({
            "id": "secrets", "title": "Secrets", "filter_label": "Secrets",
            "step_cards": [{"title": "Creepy Crypt — secret mission",
                           "how": "How",
                           "steps": [{"id": "sc1", "label": "Go"}]}],
        })
        html = render_demos([game, grove])
        self.assertIn('id="demo-ach-happy"', html)
        self.assertIn('data-step-parent="demo-ach-highdry"', html)
        self.assertIn('data-counter="mobs"', html)
        self.assertIn("Creepy Crypt", html)
        self.assertNotIn('id="ach-happy"', html)
        # The slideshow demo renders, but demo cards carry no note
        # buttons: the How page has no notes modal for them.
        self.assertIn('id="demo-ach-inspekta"', html)
        self.assertIn('class="slideshow mt-2"', html)
        self.assertNotIn('note-btn', html)
        with self.assertRaises(SystemExit):
            render_demos([make_game()])
        with self.assertRaises(SystemExit):
            render_how([make_game()])

    def test_how_page_json_example(self):
        # The example is one real achievement, pretty-printed from
        # the data — never pasted — so it can never drift, and it
        # lives in a collapsed details element at the bottom of
        # the How page, not in the way of players.
        game = make_game(slug="minecraft-dungeons")
        game["sections"][0]["achievements"][0] = {
            "id": "ach-scrappy", "name": "Scrappy Scout", "gs": 10,
            "req": "Reach Level 10.", "how": "H",
            "counters": [{"group": "level", "target": 10}],
        }
        example = render_json_example([game])
        self.assertIn('"id": "ach-scrappy"', example)
        self.assertIn('"name": "Scrappy Scout"', example)
        self.assertIn('"group": "level"', example)
        self.assertIn('"target": 10', example)
        with self.assertRaises(SystemExit):
            render_json_example([make_game()])
        template = (Path(__file__).parent / "how_template.html").read_text()
        self.assertIn("@@GAME_JSON_EXAMPLE@@", template)
        self.assertIn("Show an example", template)
        self.assertIn("data/schema.json", template)

    def test_notes_modal_and_icons(self):
        # Game pages carry a notes popup and a note icon per card
        # plus one on the filter card — and no bottom notes section.
        html = render_game(validate_game("test.json", make_game()), [])
        self.assertIn('id="notes-modal"', html)
        self.assertIn('data-note-key="a1"', html)
        self.assertIn('data-note-key="game"', html)
        self.assertNotIn('notes-section', html)
        self.assertNotIn('id="notes"', html)
        template = (Path(__file__).parent / "template.html").read_text()
        self.assertIn("refreshNoteIcons", template)
        self.assertIn("notesData", template)

    def test_slideshow_slides_stack_without_shifting(self):
        # Slides share one grid cell so the card renders at the
        # tallest slide's height: stepping never moves content
        # below the card.
        css = (Path(__file__).parent.parent
               / "assets" / "css" / "tracker-cards.css").read_text()
        self.assertIn(".slideshow-slides{display:grid}", css)
        self.assertIn(".slideshow-slide{grid-area:1/1;visibility:hidden}", css)
        self.assertIn(".slideshow-slide.active{visibility:visible}", css)

    def test_headers_normalise_and_viewer_side_tap(self):
        # Header normalisation (shrink + per-row equalisation)
        # and viewer side-tap navigation exist on game pages.
        template = (Path(__file__).parent / "template.html").read_text()
        self.assertIn("fitHeaders", template)
        self.assertIn("0.85rem", template)
        self.assertIn("media-modal-slideshow", template)
        css = (Path(__file__).parent.parent
               / "assets" / "css" / "tracker-cards.css").read_text()
        self.assertIn("justify-content:center", css)

    def test_viewer_has_slideshow_navigation(self):
        # The viewer carries Previous/Next for slideshow shots
        # (hidden for standalone images), and the credit overlay
        # style exists for the cards.
        template = (Path(__file__).parent / "template.html").read_text()
        self.assertIn('id="media-modal-nav"', template)
        self.assertIn('class="media-modal-prev', template)
        self.assertIn('class="media-modal-next', template)
        self.assertIn("modalStep", template)
        css = (Path(__file__).parent.parent
               / "assets" / "css" / "tracker-cards.css").read_text()
        self.assertIn(".media-credit", css)
        self.assertIn(".media-modal-nav", css)

    def test_achievement_header_is_a_toggle_button(self):
        # The whole header toggles via aria-pressed; there is no
        # checkbox, and the button's text content is its accessible
        # name (number + achievement name + Gamerscore).
        html = render_sections(make_game())
        self.assertIn('<button type="button" class="task"', html)
        self.assertIn('aria-pressed="false"', html)
        self.assertIn('<span class="ach-name">A</span>', html)
        self.assertNotIn('input.task', html)


if __name__ == "__main__":
    unittest.main()
