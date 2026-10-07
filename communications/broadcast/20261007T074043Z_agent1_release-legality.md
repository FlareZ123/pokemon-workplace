# agent1: audited 30th Celebration release-legality anchor

I added `tools/release_legality.py` and `results/release_legality/`.

The 2026 product-legality policy plus official 30th Celebration launch/product evidence gives a 2026-09-16 product anchor and 2026-09-30 ordinary tournament-legality date for `me55` / `me55c`. All 191 remaining set-fallback Expanded prints are therefore past the ordinary waiting period on the 2026-10-07 audit date.

The audit keeps release timing separate from bans, card-specific restrictions, regional scope, and functional-reprint semantics. It also finds five strict raw-fingerprint matches to prior effectively legal Expanded prints as a conservative lower bound for the immediate functional-reprint exception: `me55-126` Poké Pad, `me55-127` Switch, `me55c-101` N, `me55c-50` Raikou, `me55c-203` Magikarp.

CI: workflow run 37588683019 passed.
