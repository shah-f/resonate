# Combined Video Test Results

This file collects the video-level validation runs we have completed so far.
Each entry keeps the source clip, any external analytics, the Tribe inference shape,
and the deterministic analysis summary used for product validation.

## 1. When You Reach Flow State on Zetamac

- Source clip: `test_clips/when you reach flow state on zetamac.mov`
- Clip duration: `13.27s`
- External analytics source: `test_clips/tiktok_video_analytics.md`
- Real average watch time: `8.9s`
- Real watch ratio: `67.1%`

### Tribe run

- Saved inference: `results/when you reach flow state on zetamac.json`
- Saved arrays: `results/when you reach flow state on zetamac.npz`
- Prediction shape: `14 x 20484`
- Parcel shape: `14 x 200`
- Modality tracks: `14` timesteps each

### Deterministic analysis

- Saved insights: `results/when you reach flow state on zetamac_insights.json`
- Hook score: `18.7/100`
- Close score: `71.3/100`
- First dip: `2.0s` to `3.0s`, led by `visual`
- Dominant modality: `audio`
- CTA / payoff window: `11.0s` to `12.0s`

### Readout

- The model says the payoff lands late, which fits the clip structure better than the hook.
- The hook is weak and visually led, with audio almost absent at the start.
- The model is directionally aligned with the external watch-time benchmark, but it underestimates the observed watch time when using the raw normalized curve mean as a proxy.

## 2. Complaint TikTok

- Source clip: `test_clips/complaint_tiktok.mp4`
- Clip duration: `14.24s`
- External analytics source: not provided yet

### Tribe run

- Saved inference: `results/complaint_tiktok.json`
- Saved arrays: `results/complaint_tiktok.npz`
- Prediction shape: `15 x 20484`
- Parcel shape: `15 x 200`
- Modality tracks: `15` timesteps each

### Deterministic analysis

- Saved insights: `results/complaint_tiktok_insights.json`
- Hook score: `14.7/100`
- Close score: `77.3/100`
- First dip: `1.0s` to `2.0s`, led by `audio`
- Dominant modality: `audio`
- CTA / payoff window: `13.0s` to `14.0s`

### Readout

- This clip is even more top-heavy than the flow-state clip: the hook is weak and the payoff lands at the end.
- The first dip happens almost immediately and is driven by audio falling off hardest.
- Once we have external watch-time data for this clip, it will be a clean second validation point for whether the Tribe-derived proxy tracks real retention better than chance.

## Cross-Clip Takeaway

- Both clips show the same broad pattern: weak hook, stronger ending, late payoff window.
- Both analyses put the strongest moment near the end of the clip.
- The flow-state clip is the stronger validation case so far because it has a real watch-time benchmark.
- The complaint clip is useful as a second internal run, but it still needs platform analytics before we can compare prediction to outcome.

