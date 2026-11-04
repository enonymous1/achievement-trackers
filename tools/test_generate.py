#!/usr/bin/env python3
"""Tests for tools/generate.py. Run from the repo root:

    python3 -m unittest discover -s tools -v

Deliberately stdlib-only (unittest): the project has no Python
dependencies, and this file must not become the first one.
"""

import unittest

from generate import (
    render_demos,
    render_how,
    render_sections,
    sidebar_how_href,
    sidebar_menu,
    validate_game,
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
