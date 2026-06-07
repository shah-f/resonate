# Retention Calibration

Provisional correction fit for the current Tribe-derived retention proxy.

## What It Uses

- Input feature: mean of the normalized `overall` curve from the deterministic analysis.
- Target: real average watch-time ratio from the analytics files.
- Scope: four short-form clips with real watch-time data.

## Correction

```text
corrected_retention_ratio = -3.5691 * raw_proxy + 2.2361
corrected_watch_time_seconds = -50.6172 * raw_proxy + 31.7527
```

Where `raw_proxy` is the mean of the normalized `overall` curve expressed as a fraction from `0.0` to `1.0`.

## Calibration Stats

- Retention MAE: `9.6 percentage points`
- Retention RMSE: `12.6 percentage points`
- Watch-time MAE: `1.36s`
- Watch-time bias: `+0.08s`

## Clip-Level Results

| Clip | Actual watch time | Corrected watch time | Error |
|---|---:|---:|---:|
| `when you reach flow state on zetamac` | `8.9s` | `6.56s` | `-2.34s` |
| `complaint_tiktok` | `10.0s` | `9.78s` | `-0.23s` |
| `walk_in_park` | `5.1s` | `7.81s` | `+2.71s` |
| `outfit_transition` | `5.6s` | `5.78s` | `+0.18s` |

## Caveat

This correction is in-sample and only based on four clips. It is useful as a
temporary calibration, but it should be replaced once we have more 10-15 second
examples.
