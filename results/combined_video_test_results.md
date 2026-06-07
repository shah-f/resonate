# Combined Video Test Results

This file collects the video-level validation runs we have completed so far.
Each entry keeps the source clip, any external analytics, the Tribe inference shape,
and the deterministic analysis summary used for product validation.

## Provisional Calibration

The current raw Tribe proxy is not calibrated, so for now we also keep a simple
in-sample correction fit on the clips with real watch-time data.

### Fit

- Input: mean of the normalized `overall` curve from `analysis/resonate_analysis.py`
- Target: real average watch-time ratio from the analytics files
- Model: linear correction fit on the four clips below

### Correction

- Corrected retention ratio = `-3.5691 * raw_proxy + 2.2361`
- Corrected watch time = `-50.6172 * raw_proxy + 31.7527`

### Calibration stats on the four benchmark clips

- Retention MAE: `9.6 percentage points`
- Retention RMSE: `12.6 percentage points`
- Watch-time MAE: `1.36s`
- Watch-time bias: `+0.08s`

### Clip-level corrected watch times

- `when you reach flow state on zetamac`: `6.56s` vs actual `8.9s`
- `complaint_tiktok`: `9.78s` vs actual `10.0s`
- `walk_in_park`: `7.81s` vs actual `5.1s`
- `outfit_transition`: `5.78s` vs actual `5.6s`

This is still in-sample and provisional, but it is a better "for now" correction
than the raw mean-of-curve proxy.

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
- External analytics source: `test_clips/tiktok_video_analytics.md`
- Real average watch time: `10.0s`
- Real watch ratio: `69.3%`

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
- The simple normalized-curve proxy gives about `6.3s`, which is below the real `10.0s` average watch time.
- So this clip is a useful counterexample: the shape is right, but the current proxy is conservatively low.

## 3. Park Walk

- Source clip: `test_clips/walk_in_park.mp4`
- Clip duration: `15.07s`
- External analytics source: `test_clips/tiktok_video_analytics.md`
- Real average watch time: `5.1s`
- Real watch ratio: `33.8%`

### Tribe run

- Saved inference: `results/walk_in_park.json`
- Saved arrays: `results/walk_in_park.npz`
- Prediction shape: `15 x 20484`
- Parcel shape: `15 x 200`
- Modality tracks: `15` timesteps each

### Deterministic analysis

- Saved insights: `results/walk_in_park_insights.json`
- Hook score: `23.1/100`
- Close score: `64.6/100`
- First dip: `2.0s` to `3.0s`, led by `audio`
- Dominant modality: `visual`
- CTA / payoff window: `10.0s` to `11.0s`

### Readout

- The model sees a late payoff and a very early audio drop.
- The simple normalized-curve proxy gives about `7.3s`, which is above the real `5.1s` average watch time.
- So for this clip the proxy is overpredicting, even though the shape still says the hook is the weak point.

## 4. Outfit Transition

- Source clip: `test_clips/outfit_transition.mp4`
- Clip duration: `15.00s`
- External analytics source: `test_clips/tiktok_video_analytics.md`
- Real average watch time: `5.6s`
- Real watch ratio: `37.3%`

### Tribe run

- Saved inference: `results/outfit_transition.json`
- Saved arrays: `results/outfit_transition.npz`
- Prediction shape: `15 x 20484`
- Parcel shape: `15 x 200`
- Modality tracks: `15` timesteps each

### Deterministic analysis

- Saved insights: `results/outfit_transition_insights.json`
- Hook score: `24.0/100`
- Close score: `67.4/100`
- First dip: `1.0s` to `2.0s`, led by `audio`
- Dominant modality: `visual`
- CTA / payoff window: `12.0s` to `13.0s`

### Readout

- This clip also looks end-loaded, with a strong late payoff and an early audio collapse.
- The simple normalized-curve proxy gives about `7.8s`, again above the real `5.6s` average watch time.
- That means the raw proxy is not calibrated yet, but the structural story is still useful for editing feedback.

## Cross-Clip Takeaway

- Both clips show the same broad pattern: weak hook, stronger ending, late payoff window.
- Both analyses put the strongest moment near the end of the clip.
- The flow-state clip and complaint clip are the two strongest validation cases so far because they have real watch-time benchmarks.
- The raw normalized Tribe proxy is not calibrated yet: it underpredicted the first two clips and overpredicts the newer park/outfit clips.
- That mixed bias is a signal that we need a better calibration model, not just a raw mean-of-curve watch-time proxy.
- `green_top` was intentionally skipped per request.
