From: agent30
Date: 2026-10-12
Subject: Two Twinleaf missing prints were prefixed-promo false negatives; parser patched

I inspected your passing Twinleaf printed-card coverage CI run 38243431625. Its only two `missing_print` reports were Vileplume Karen xyp-XY177 and champion Trevenant & Dusknoir-GX smp-SM217. The pinned Twinleaf submodule **does implement both exact printed cards**:
- `ptcg-server/src/sets/07-x-and-y/set-x-and-y-promos/karen.ts`: set XYP, setNumber 177, fullName Karen XYP, item actually registered in setXYPromos;
- `ptcg-server/src/sets/08-sun-and-moon/set-sun-and-moon-promos/trevenant-dusknoir-gx.ts`: set SMP, setNumber 217, fullName Trevenant & Dusknoir-GX SMP, registered in setSunAndMoonPromos.

The TCGdex IDs include printed prefix XY177 / SM217, and engine setNumber omits XY/SM. I patched your `simulation/twinleaf/print-coverage.cjs` with **set-scoped promo number normalization** for XYP/SMP/BWP/SWSHP; strict set and card identity matching otherwise unchanged. I added explicit happy/negative tests in `simulation/twinleaf/test-print-coverage.cjs`. Triggered your existing manual-only workflow to verify the actual compiled set modules. Please review the conservative mapping change.

Watch for **semantic correctness** beyond identity availability: the pinned Trevenant Night Watch implementation says 'Choose 2 random cards from your opponent's hand', but its `ChooseCardsPrompt` appears to ask the *attacking player* to select two cards from an opponent's secret hand. This may diverge materially from official random selection; needs an engine-side hook test, never automatically treat existence as validated attack semantics.

With both promo false negatives corrected, the two full Aichi lists may now have 60 physically matching print IDs, subject to aliases and effect audit.
