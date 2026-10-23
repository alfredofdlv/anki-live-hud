# Install and try Anki Live HUD on Windows

Requires **Anki Desktop 26.09.3 or newer (Qt 6)**. Check Help → About in Anki.
Use the release candidate package `anki-live-hud-0.1.0-rc.1.ankiaddon`.
No Python installation, browser extension, account or API key is needed.

## Install

1. Open Anki Desktop.
2. Select **Tools → Add-ons → Install from file…**.
3. Select `dist\anki-live-hud-0.1.0-rc.1.ankiaddon` from this repository,
   or the equivalent file downloaded from a future GitHub Release.
4. Accept Anki's installation prompt and restart Anki.
5. Select a deck and click **Study Now**. The HUD appears on the right.

The archive installs as `%APPDATA%\Anki2\addons21\anki_live_hud` in a default
Anki setup. Use Anki's installer instead of unzipping into a profile folder.
The add-on does not modify your note templates, scheduling options or review history.

## Check the result

For an initial trial, use File → Switch Profile to create a small test profile
and add a few Basic cards. The HUD has already been tested in a separate,
automatically created test profile; that test profile is not your personal collection.

1. Note **Reviews today**, **Correct answers** and **Again answers**.
2. Press Space to reveal an answer. Rate one card Again (1), Hard (2), Good (3)
   or Easy (4), or click a native answer button. Each rating adds one review
   event; Hard/Good/Easy also add one correct answer.
3. Observe the animated counter, delta and goal bar. Anki defaults may have
   reduced motion enabled; to see animations, enable them in the HUD settings
   and turn off Anki's reduced-motion preference. OS reduced motion also takes precedence.
4. Choose Edit → Undo (Ctrl+Z, or Anki's `u` review shortcut). Totals and
   accuracy return to the actual review history.
5. Set a small goal in **Tools → Anki Live HUD → Settings…** to try completion feedback.
6. Collapse using `›`, expand using `‹`, and drag the sidebar's left divider to resize.
   Narrow windows collapse automatically; expanding from the rail widens the window if needed.
7. Hide with `×`; restore using **Tools → Anki Live HUD → Show during reviews**.
8. Try compact mode and light/dark/automatic themes. Leave the reviewer and
   return. Restart Anki and check that statistics and preferences remain correct.

Daily totals cover all decks in the collection and use Anki's study-day rollover.
The small unique-card count counts cards separately from answer events. Accuracy
means Hard + Good + Easy divided by all rated answers; **it is not True Retention**.
Queue remaining comes from Anki and may stay unchanged or increase after a learning answer.

## Settings and removal

All controls are in Tools → Anki Live HUD → Settings. Anki's normal Tools →
Add-ons → Config editor also works. Settings live in Anki's add-on metadata;
the add-on does not synchronize them between devices.

To temporarily disable it, uncheck Enable Anki Live HUD in its settings.
To uninstall, select Anki Live HUD in Tools → Add-ons, delete it, and restart.
Review data remains in your collection.

## Troubleshooting

- If the panel is hidden, check both Enable and Show during reviews. Expand
  the rail or widen the window if it collapsed automatically.
- If counters jump without animation, check Anki and OS reduced-motion settings.
- If statistics briefly show unavailable, finish pending collection operations
  and answer or reopen the reviewer. Check Anki's add-on log for `anki_live_hud`.
- If Anki's own cards and toolbar are also blank, this is a broader WebEngine
  loading problem. Restart Anki and check Anki's graphics/proxy configuration.
  The development test harness disables proxy auto-discovery only inside its own
  disposable test process; the installed HUD does not change your networking settings.
- For add-on conflicts, test in a separate profile with other add-ons disabled,
  then enable the other add-ons individually. Include Anki/OS versions and a
  sample-deck reproduction in a bug report.
