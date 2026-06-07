# Finance Test Clip Analysis

Source artifacts:

- `results/finance_test_clip.npz`
- `results/finance_test_clip.json`
- `test_clips/finance_test_clip.mp4`

Analysis date: 2026-06-07

No Modal calls were run for this analysis. The analysis used the saved first-run artifacts only.

## What The Data Says

The clip is 10.5s long, with 11 one-second inference segments.

The core pattern is:

| Window | Overall Signal | Visual | Audio | Language |
|---|---:|---:|---:|---:|
| 0-2s hook | 14/100 | 15 | 25 | 3 |
| 3-7s middle | 17/100 | 21 | 4 | 25 |
| 8-10s close | 66/100 | 67 | 56 | 74 |

These are normalized within this one clip, so they are not universal retention percentages. But they are useful for relative timing.

## Human-Facing Insights We Could Give

### 1. The payoff arrives too late.

The strongest predicted brain response happens at 9-10s, when the "Employee" tax-bracket explanation appears. The first 8 seconds are comparatively low, so the video may be asking viewers to wait too long before the educational payoff lands.

### 2. The weakest moment is around 2s.

Combined activation bottoms out at second 2. That is dangerous for short-form video because it is inside the scroll-decision window.

### 3. The hook is mostly setup, not curiosity.

The first frames show the "Boss" setup: "Congrats. I'm giving you a raise..." The model sees relatively weak language activation early, meaning the concept may not become cognitively interesting until later.

### 4. The language track steadily improves.

Language rises almost monotonically and peaks at 10s. That suggests the script gets more meaningful as it goes, especially when the tax-bracket logic is revealed.

### 5. Visual novelty is low until the role switch.

Visual activation is weak/negative for most of the clip, then jumps sharply at 9-10s. The character switch and framing change appear to be doing real work.

### 6. Audio also sags in the middle.

Audio reaches its lowest point around 7s, then rebounds at the end. If the middle is mostly repetitive delivery, this is where pacing or vocal emphasis may need help.

## Suggested Creator Feedback

"Your best moment is the ending, but viewers may not make it there. Move the tax-bracket reveal earlier, ideally into the first 2-3 seconds. Open with the surprising misconception, then use the boss role-play as proof."

Possible rewrite:

> "A raise from $38K to $41K does not mean you lose money to taxes. Here's the mistake people make."

Then continue with the boss/employee bit.

## Good Demo Cards For Resonate

- **Attention Dip:** "Predicted engagement drops hardest at 0:02."
- **Why:** "The setup repeats salary information before the actual tax misconception appears."
- **Fix:** "Move the tax-bracket reveal earlier or add a visual contrast at 0-2s."
- **CTA Window:** "Best CTA/info-drop window: 0:09-0:10, but this is currently too late for short-form retention."
- **Modality Balance:** "Language carries the ending; visual and audio need more support in the hook."

## Caveat

This first saved result does not include `parcel_names`, so avoid named brain-region claims from this artifact alone. It supports modality/timing insights, not region-label insights yet.
