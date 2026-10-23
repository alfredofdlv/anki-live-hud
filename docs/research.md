# API research and architecture

Research date: 23 October 2026. Latest stable upstream release and locally installed
Windows release: **Anki 26.09.3**. The first release deliberately requires 26.09.3;
older Anki versions are not advertised as supported. Qt 6 only.

## Official sources consulted

- [Add-on development guide](https://addon-docs.ankiweb.net/) (now redirects to docs.ankiweb.net).
- [Hooks and filters](https://docs.ankiweb.net/addons/hooks-and-filters).
- [Reviewer JavaScript](https://docs.ankiweb.net/addons/reviewer-javascript).
- [Distribution and archive rules](https://docs.ankiweb.net/addons/sharing).
- [Current release](https://github.com/ankitects/anki/releases/tag/26.09.3).
- [Reviewer implementation at the supported tag](https://github.com/ankitects/anki/blob/26.09.3/qt/aqt/reviewer.py).
- [Hook definitions](https://github.com/ankitects/anki/blob/26.09.3/qt/tools/genhooks_gui.py).
- [Serialized QueryOp implementation](https://github.com/ankitects/anki/blob/26.09.3/qt/aqt/operations/__init__.py).
- [Webview and asynchronous bridge](https://github.com/ankitects/anki/blob/26.09.3/qt/aqt/webview.py).
- [Scheduler queue counts](https://github.com/ankitects/anki/blob/26.09.3/pylib/anki/scheduler/v3.py).
- [Scheduler study-day timing](https://github.com/ankitects/anki/blob/26.09.3/pylib/anki/scheduler/base.py).

The local installation contains compiled Python modules. Exact-version source was
also installed into an isolated development virtual environment for inspection and tests.

## Related implementations inspected

- [Glutanimate's reviewer progress bar](https://github.com/glutanimate/anki-addons-misc/blob/master/src/reviewer_progress_bar/reviewer_progress_bar.py)
  demonstrates a native dock and restoring reviewer focus. Its legacy scheduler and hook
  code is unsuitable for adoption here.
- [Anki Design](https://github.com/NoahLloyd/anki-design/blob/main/__init__.py)
  demonstrates webview integration and a reviewer progress indicator, alongside much
  broader UI changes than this project needs.

No source, artwork or styles from those add-ons are copied into the distribution.
The implementation in this repository is original and MIT licensed.

## Rendering decision

Use a right-hand `QDockWidget` with its own `AnkiWebView`. The card webview and
native bottom answer bar remain Anki's own widgets. The HUD document is loaded once
per profile and stays alive when cards change, when it is hidden or collapsed, and
when moving between review sessions. There is no `card_will_show` injection and no
monkey patch of reviewer or scheduler methods.

`stdHtml()` supplies Anki's bridge script. Its QWebChannel becomes ready
asynchronously; a queued `eval()` calls the HUD connection method after `domDone`.
The HTML, CSS and JavaScript are bundled and inlined into that independent page.
No font CDN, web exports, remote assets, frontend frameworks, telemetry or runtime
downloads are required. Anki serves its own webview resources over local loopback.

The dock uses Qt's native divider for resizing. A 42px rail replaces the expanded
panel in windows narrower than 820 logical pixels. User preferences remain intact
when automatic collapse ends. The dock cannot float or move into other dock areas.

## Hooks used and verified signatures

- `reviewer_did_answer_card(reviewer, card, ease)` — after committed scheduling.
- `reviewer_did_show_question(card)` and `reviewer_did_show_answer(card)` — refresh queue context.
- `reviewer_will_end()` — hide safely.
- `state_did_change(new_state, old_state)` — enter/leave reviews.
- `operation_did_execute(changes, handler)` — refresh after undo, redo, edits, resets and queue changes.
- `theme_did_change()` and `body_classes_need_update()` — theme and accessibility settings.
- `profile_did_open()` / `profile_will_close()` — profile lifecycle.
- `collection_will_temporarily_close(col)` — invalidate pending work for sync/import.

The current reviewer builds an answer, runs the scheduling operation on the
collection worker, then calls `reviewer_did_answer_card` in its success callback,
before fetching the next card. The operation hook follows the success callback.
Refresh requests are coalesced into the next Qt event turn, so queue counts are
queried after this sequence. Both keyboard shortcuts and buttons reach the same
native scheduling operation.

## Data and concurrency

All daily totals are read afresh from `revlog`, never maintained as permanent
add-on counters. Include ease 1–4 and revlog types 0–3 (learning, review,
relearning, filtered); exclude manual/rescheduling rows. Repeated answers count as
separate events. Count distinct card IDs separately.

The study day ends at `col.sched.day_cutoff`. Its start is the previous local
calendar date at that rollover hour; subtracting 86400 seconds would be wrong
across daylight-saving changes. SQL uses half-open millisecond bounds on the
indexed `revlog.id` primary key. Queries touch the current study day only.

Daily metrics cover the collection; remaining is the sum of
`col.sched.counts()` for the selected study deck. Learning steps, filtered decks,
limits and burying follow Anki's scheduler. It is never calculated as yesterday's
remaining minus one. Accuracy is `(Hard + Good + Easy) / rated answers`, including
learning answers, and must not be described as True Retention.

`QueryOp` uses Anki's serialized collection executor without a progress dialog.
A revision/profile gate rejects obsolete snapshots. UI callbacks only serialize
results and update the webview. Polling every 30 seconds while reviewing catches
an idle study-day rollover; answer/card/operation events update immediately.
Profile closure invalidates pending callbacks. Read errors produce an inline
status and a log entry, with retry on the next event instead of a modal popup.

Frontend transitions use a single `requestAnimationFrame` loop and retarget from
the currently rendered number. The latest snapshot wins. Reduced motion from
Anki, the OS or the add-on setting disables transitions and decorative feedback.

## Release boundary

P0 takes priority. The only P1 additions in this release are an animated answer
distribution, compact layout, theme selection and configurable distribution visibility.
FSRS metrics, activity history, streaks, deck-scoped daily totals and exports are deferred.
Anki scheduling, card content and review history are never written by the add-on.
