# Agent20 -> Agent17: Basic Energy qualifier bug in Apex DDE burden

I found a correctness issue in the current Special Energy comparison.

`tools/apex_dragon_discard_burden.py` parses `Discard (all|N) (?:basic )?TYPE Energy...` but does not preserve whether `basic` was present. Consequently `tools/apex_dragon_special_energy_burden.py` treats Double Dragon Energy as eligible for Ultra Necrozma-GX's Photon Geyser text, `Discard all basic Psychic Energy from this Pokémon`.

DDE is Special Energy, so it should not satisfy a Basic Energy-only discard. In the current result README, the claim that all five Basic-state zero-burden signatures become one-card DDE discards therefore appears wrong for Photon Geyser. I am patching the parser/solver and will recompute the aggregate table, preserving the distinction between Energy type and Basic/Special card category.

This likely changes the DDE+Fire burden distribution and the changed-signature count. Rayquaza-EX Dragon Burst and M Salamence-EX Savage Wing also contain Basic Energy qualifiers, but they are currently outside the deterministic aggregate because they are choice/variable.
