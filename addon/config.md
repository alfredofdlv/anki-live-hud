# Anki Live HUD

Use **Tools → Anki Live HUD → Settings…** for a graphical editor.

- `enabled`: run the HUD during reviews.
- `visible`: show it (also available in the Tools menu).
- `collapsed`: show a slim expandable rail.
- `width`: preferred expanded width in pixels, 240–480. Drag the dock divider to resize.
- `daily_goal`: target number of rated answer events, 1–100000.
- `animations`: animate counters, deltas and progress. Anki and OS reduced-motion preferences take precedence.
- `compact`: reduce spacing and hide the explanatory footer.
- `theme`: `auto`, `light` or `dark`. Auto follows Anki.
- `show_distribution`: show Again / Hard / Good / Easy counts.

Daily figures cover the whole collection and use Anki's study-day rollover.
Queue remaining covers the selected study deck, including its subdecks, using the scheduler's queue counts.
Accuracy means Hard + Good + Easy divided by all rated answers; it is not True Retention.
Repeated answers to the same card count as separate review events.
