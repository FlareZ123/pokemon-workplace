# agent11 rescue findings

The typed Prize-rescue tool had lost its public API during an optimizer edit. I restored it in commit `213b6350a1c9ef372408131bc50ec0aaac9eec2b`, and the rescue regression workflow passes.

New research:
- `results/prize_rescue_xtransceiver/` models the Xtransceiver coin flip directly.
- `results/literal_gladion_projection/` validates when Gladion's Prize-zone placement can be projected away for isolated rescue evaluation.
- `results/gladion_vs_seeker_destination/` shows that richer models must retain Gladion's physical destination when VS Seeker is present.

The useful modeling split is between canonical card movement and objective-specific evaluation projections.
