## Xbox sync setup (OpenXBL)

The sync card is built but dormant: it renders only for games whose
JSON carries an `xbox_title_id` and an `xbox_id` on every
achievement, and no game is mapped yet. No public source lists those
IDs, so they come from a live OpenXBL response — never guessed. To
map a game:

1. **Get an OpenXBL key:** sign in at xbl.io with the Microsoft
   account that owns the Xbox profile and create an API key.
2. **Find your XUID:** `GET https://api.xbl.io/api/v2/player/gamertag/<gamertag>`
   with header `X-Authorization: <key>` (or `GET /api/v2/account`
   for the key owner).
3. **Find the title ID:** `GET https://api.xbl.io/api/v2/player/titleHistory/<xuid>`
   and take the `titleId` from the entry for the game.
4. **Fetch the per-title achievements:** `GET https://api.xbl.io/api/v2/achievements/player/<xuid>/title/<titleId>`
   and save the full response. If it is paginated, fetch the
   following pages and merge the achievement entries into one file
   (an array, or an object with an `achievements` array).
5. **Map it:** `python tools/map_xbox.py --title-id <titleId> response.json`
   — it matches by name and refuses to write on any unmatched or
   ambiguous achievement. Review the diff (names, Gamerscore
   warnings) before continuing.
6. **Regenerate and commit:** `python tools/generate.py`, then
   `--check` and the tests, and commit the JSON and the generated
   HTML together. The sync card then appears on that game's page.
7. **Use it:** the card takes a gamertag and key (stored in that
   browser only, never in Export), shows a preview, and applies on
   Confirm — newly unlocked achievements and their sub-steps only,
   never unticks, never touches notes or counters. If the browser
   blocks the direct fetch, the card's paste-JSON fallback takes the
   same per-title response from step 4.

**Key safety, stated plainly:** a key committed to a public repo is
public, permanently — git history keeps it even after deletion, and
anyone holding it can burn the account's rate limit and query data
through it. OpenXBL keys carry no "only this gamertag" scope, and a
gamertag check in page JavaScript is cosmetic: anyone can edit the
script or call the API directly. So the key stays out of the repo.
Two safe shapes: (a) per-visitor keys — each visitor enters their
own key, which is the model the card uses; (b) if the published
site should show one person's progress with no key asked of
visitors, fetch it at build time in GitHub Actions with the key
stored in the repo's Settings → Secrets (never in a file) and
publish only the resulting achievement states — the key never
reaches the site.
