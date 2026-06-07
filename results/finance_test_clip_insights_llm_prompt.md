# Resonate LLM Analysis Prompt

You are writing creator-facing analysis for Resonate, a tool that uses predicted brain-response signals from video.

Write in the same style as the saved finance test clip analysis:

1. `What The Data Says`
2. `Human-Facing Insights We Could Give`
3. `Suggested Creator Feedback`
4. `Good Demo Cards For Resonate`
5. `Caveat`

Rules:

- Use only the evidence packet below.
- Say "predicted brain response", "signal suggests", or "model indicates"; do not say the data proves real viewer behavior.
- Scores are normalized within this clip. Do not call them universal retention percentages.
- Give concrete creator advice tied to timestamps, modalities, windows, or feature cards.
- If `event_context.available` is false, do not claim exact extracted event-row causes.
- Do not translate Schaefer parcel labels into precise named brain regions without a separate translation layer.
- Keep it concise, practical, and demo-ready.

Evidence packet:

```json
{
  "evidence_summary": {
    "main_story": "The strongest combined activation arrives near the end, while the hook is weak.",
    "payoff_delta_close_minus_hook": 51.8,
    "first_major_dip": {
      "timestep": 1,
      "start": 1.0,
      "end": 2.0,
      "overall_before": 28.4,
      "overall_after": 10.7,
      "overall_delta": -17.7,
      "lead_modality": "visual",
      "modality_deltas": {
        "visual": -27.1,
        "audio": -21.7,
        "language": -4.4
      }
    },
    "strongest_moment": {
      "timestep": 10,
      "start": 10.0,
      "end": 11.0,
      "overall": 100.0,
      "modalities": {
        "visual": 100.0,
        "audio": 100.0,
        "language": 100.0
      }
    },
    "weakest_moment": {
      "timestep": 2,
      "start": 2.0,
      "end": 3.0,
      "overall": 2.8,
      "modalities": {
        "visual": 0.0,
        "audio": 4.0,
        "language": 4.5
      }
    },
    "cta_window": {
      "timestep": 10,
      "start": 10.0,
      "end": 11.0,
      "overall": 100.0,
      "modalities": {
        "visual": 100.0,
        "audio": 100.0,
        "language": 100.0
      },
      "note": "Best local moment for payoff/CTA based on combined normalized activation."
    },
    "modality_balance": {
      "shares": {
        "visual": 13.5,
        "audio": 41.6,
        "language": 44.8
      },
      "dominant": "language",
      "verdict": "Language-heavy: this clip is carried most by language signal."
    }
  },
  "feature_cards": {
    "engagement_autopsy": {
      "headline": "Predicted engagement drops around 1.0s.",
      "evidence": {
        "timestep": 1,
        "start": 1.0,
        "end": 2.0,
        "overall_before": 28.4,
        "overall_after": 10.7,
        "overall_delta": -17.7,
        "lead_modality": "visual",
        "modality_deltas": {
          "visual": -27.1,
          "audio": -21.7,
          "language": -4.4
        }
      },
      "suggested_fix": "Strengthen the visual cue at this moment."
    },
    "payoff_timing": {
      "headline": "The payoff appears to land late.",
      "evidence": {
        "hook_overall": 14.0,
        "close_overall": 65.8,
        "close_minus_hook": 51.8
      },
      "suggested_fix": "Move the strongest idea, reveal, or contrast into the first 2-3 seconds."
    },
    "modality_balance": {
      "headline": "Language-heavy: this clip is carried most by language signal.",
      "evidence": {
        "visual": 13.5,
        "audio": 41.6,
        "language": 44.8
      },
      "suggested_fix": "If the clip is too language-heavy, add visual proof, b-roll, captions with contrast, or clearer scene changes."
    },
    "cta_window": {
      "headline": "Best local payoff/CTA moment is around 10.0-11.0s.",
      "evidence": {
        "timestep": 10,
        "start": 10.0,
        "end": 11.0,
        "overall": 100.0,
        "modalities": {
          "visual": 100.0,
          "audio": 100.0,
          "language": 100.0
        },
        "note": "Best local moment for payoff/CTA based on combined normalized activation."
      },
      "suggested_fix": "Use this timing for payoff placement, or move this moment earlier if it lands too late for short-form retention."
    }
  },
  "ranked_moments": {
    "strongest": [
      {
        "timestep": 10,
        "start": 10.0,
        "end": 11.0,
        "overall": 100.0,
        "modalities": {
          "visual": 100.0,
          "audio": 100.0,
          "language": 100.0
        }
      },
      {
        "timestep": 9,
        "start": 9.0,
        "end": 10.0,
        "overall": 62.3,
        "modalities": {
          "visual": 73.9,
          "audio": 48.0,
          "language": 65.1
        }
      },
      {
        "timestep": 8,
        "start": 8.0,
        "end": 9.0,
        "overall": 35.0,
        "modalities": {
          "visual": 26.2,
          "audio": 20.9,
          "language": 57.8
        }
      }
    ],
    "weakest": [
      {
        "timestep": 2,
        "start": 2.0,
        "end": 3.0,
        "overall": 2.8,
        "modalities": {
          "visual": 0.0,
          "audio": 4.0,
          "language": 4.5
        }
      },
      {
        "timestep": 1,
        "start": 1.0,
        "end": 2.0,
        "overall": 10.7,
        "modalities": {
          "visual": 8.2,
          "audio": 24.0,
          "language": 0.0
        }
      },
      {
        "timestep": 5,
        "start": 5.0,
        "end": 6.0,
        "overall": 14.4,
        "modalities": {
          "visual": 22.4,
          "audio": 2.2,
          "language": 18.7
        }
      }
    ]
  },
  "windows": {
    "hook": {
      "label": "0-3s hook",
      "indices": [
        0,
        1,
        2
      ],
      "overall": 14.0,
      "modalities": {
        "visual": 14.5,
        "audio": 24.6,
        "language": 3.0
      }
    },
    "middle": {
      "label": "3-8s middle",
      "indices": [
        3,
        4,
        5,
        6,
        7
      ],
      "overall": 16.7,
      "modalities": {
        "visual": 20.5,
        "audio": 4.4,
        "language": 25.3
      }
    },
    "close": {
      "label": "last 3s close",
      "indices": [
        8,
        9,
        10
      ],
      "overall": 65.8,
      "modalities": {
        "visual": 66.7,
        "audio": 56.3,
        "language": 74.3
      }
    }
  },
  "dips": [
    {
      "timestep": 1,
      "start": 1.0,
      "end": 2.0,
      "overall_before": 28.4,
      "overall_after": 10.7,
      "overall_delta": -17.7,
      "lead_modality": "visual",
      "modality_deltas": {
        "visual": -27.1,
        "audio": -21.7,
        "language": -4.4
      }
    },
    {
      "timestep": 2,
      "start": 2.0,
      "end": 3.0,
      "overall_before": 10.7,
      "overall_after": 2.8,
      "overall_delta": -7.9,
      "lead_modality": "audio",
      "modality_deltas": {
        "visual": -8.2,
        "audio": -20.0,
        "language": 4.5
      }
    }
  ],
  "cta_window": {
    "timestep": 10,
    "start": 10.0,
    "end": 11.0,
    "overall": 100.0,
    "modalities": {
      "visual": 100.0,
      "audio": 100.0,
      "language": 100.0
    },
    "note": "Best local moment for payoff/CTA based on combined normalized activation."
  },
  "modality_balance": {
    "shares": {
      "visual": 13.5,
      "audio": 41.6,
      "language": 44.8
    },
    "dominant": "language",
    "verdict": "Language-heavy: this clip is carried most by language signal."
  },
  "parcel_evidence": {
    "top_rising": [
      {
        "parcel_index": 80,
        "parcel_name": "7Networks_LH_Default_Par_3",
        "delta": 0.5358
      },
      {
        "parcel_index": 182,
        "parcel_name": "7Networks_RH_Default_Par_2",
        "delta": 0.4878
      },
      {
        "parcel_index": 187,
        "parcel_name": "7Networks_RH_Default_Temp_4",
        "delta": 0.4848
      },
      {
        "parcel_index": 78,
        "parcel_name": "7Networks_LH_Default_Par_1",
        "delta": 0.4105
      },
      {
        "parcel_index": 73,
        "parcel_name": "7Networks_LH_Default_Temp_1",
        "delta": 0.4084
      }
    ],
    "top_falling": [
      {
        "parcel_index": 115,
        "parcel_name": "7Networks_RH_SomMot_1",
        "delta": -0.1718
      },
      {
        "parcel_index": 15,
        "parcel_name": "7Networks_LH_SomMot_2",
        "delta": -0.1716
      },
      {
        "parcel_index": 14,
        "parcel_name": "7Networks_LH_SomMot_1",
        "delta": -0.1226
      },
      {
        "parcel_index": 116,
        "parcel_name": "7Networks_RH_SomMot_2",
        "delta": -0.1046
      },
      {
        "parcel_index": 166,
        "parcel_name": "7Networks_RH_Cont_Par_3",
        "delta": -0.0878
      }
    ],
    "usage_note": "Use parcel labels as supporting atlas evidence only; do not translate them into precise named brain regions without a separate translation layer."
  },
  "event_context": {
    "available": false,
    "shape": null,
    "columns": [],
    "sample_records": [],
    "usage_note": "No Tribe event dataframe was saved for this result; do not claim event-row-specific causes."
  },
  "notes": [
    "Scores are normalized within this clip and should be read as relative timing signals, not universal retention percentages.",
    "This analysis is deterministic and does not use an LLM. Feed llm_context into an LLM to generate polished human-facing coaching."
  ]
}
```

Now write the markdown analysis.
