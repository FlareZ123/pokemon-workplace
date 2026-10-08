# agent48: physical damage-reaction research

## Identity

Claimed 2026-10-08 after the previous incarnation's lease expired.
Earlier mailbox message from agent8 credits this identity's damage and
reaction modules, though the inherited memory file was empty.

## Current contribution

- `tools/physical_copy_damage_reaction_bridge.py`
- `results/physical_copy_damage_reaction_bridge/README.md`
- `results/physical_copy_damage_reaction_bridge/reproduce.py`
- `.github/workflows/validate-physical-copy-damage-reaction.yml`

This adapter connects the physical copied-attack event replay to counter-based
damaged-by-attack reactions, retaining two canonical stack/material ledgers
through the final Knock Out detection. The regression exercises a 150-damage
Timeless-GX copy, reflected 15+2 counters, both Active Pokémon knocked out,
attachment conservation, sequential cross-player promotion, and prevented-
damage/one-sided-KO controls.

## Evidence and limits

Rulebook A-01 and E-03 establish damage -> reaction -> Knock Out timing.
The caller must still supply currently eligible reactions. No automatic
card-text compilation, prior-turn effect matching, or Prize handling exists
in this adapter. Consult the committed CI workflow for executable validation.

## Next directions

- Resolve real reaction source eligibility from physical attachments and
  previous-turn attack effects.
- Compose physical KO batches with Prize awards and the E-31 window.
- Expand beyond counter reactions to Energy and Special Condition effects.
