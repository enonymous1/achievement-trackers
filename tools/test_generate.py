#!/usr/bin/env python3
"""Tests for tools/generate.py. Run from the repo root:

    python3 -m unittest discover -s tools -v

Deliberately stdlib-only (unittest): the project has no Python
dependencies, and this file must not become the first one.
"""

import unittest
from pathlib import Path

from generate import (
    render_demos,
    render_how,
    render_sections,
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

    def test_sidebar_menu_and_how_href(self):
        games = [make_game(), make_game(slug="other", title="Other")]
        html = sidebar_menu(games, "../", "test", include_notes=True)
        self.assertIn('href="../"', html)
        self.assertIn('href="../other/"', html)
        self.assertIn("Games</li>", html)
        self.assertIn('href="#notes-section"', html)
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
        # Demos are rendered from the real Dungeons data, with
        # demo-prefixed ids, and a missing source game fails loudly
        # instead of shipping empty demo slots.
        game = make_game(slug="minecraft-dungeons")
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
        html = render_demos([game])
        self.assertIn('id="demo-ach-happy"', html)
        self.assertIn('data-step-parent="demo-ach-highdry"', html)
        self.assertIn('data-counter="mobs"', html)
        self.assertIn("Creepy Crypt", html)
        self.assertNotIn('id="ach-happy"', html)
        with self.assertRaises(SystemExit):
            render_demos([make_game()])
        with self.assertRaises(SystemExit):
            render_how([make_game()])

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
