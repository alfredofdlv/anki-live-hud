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
- `answer_feedback`: show the native impact layer over the review area after a committed answer.
- `feedback_duration`: how long that layer remains visible, 1200–5000 milliseconds (default 2400).
- `show_streak`: show the current Hard/Good/Easy run, best run today and exact Good run.
- `show_recent_chart`: show the last 24 ratings and rolling five-answer accuracy line.

Impact feedback is a separate mouse-transparent native layer: a pop-in medal,
rating, +1 review and real daily-goal progress. Rapid answers replace the current
notification. Undo, hiding the HUD and leaving reviews dismiss it. The reward
does not depend on choosing Easy; all four ratings record one review.
With animations disabled or reduced motion enabled, the notification still
appears, but stays stationary until it disappears. Disable `answer_feedback`
to keep only the quiet sidebar.

Runs cover the collection's current Anki study day, not a number of calendar days.
Again resets the passing run; any non-Good rating resets the exact Good run.
Undo, deck switching and restart reconstruct these values from the review log.
The chart's x-axis is answer order, not time. Its percentage is not True Retention.

Daily figures cover the whole collection and use Anki's study-day rollover.
Queue remaining covers the selected study deck, including its subdecks, using the scheduler's queue counts.
Accuracy means Hard + Good + Easy divided by all rated answers; it is not True Retention.
Repeated answers to the same card count as separate review events.
