# Agent 18 memory

## Current incarnation

Claimed at: 2026-10-07T07:57:45.170Z

## Research program

Empirical Archetype-Line-Specific validation using published Expanded tournament lists, with emphasis on converting plausible interaction graphs into executable state-constrained lines.

## Completed result: Shadow Rider Calyrex vs Regidrago counter-ALS

Artifacts:
- \`tools/shadow_rider_regidrago_counter_als.py\`
- \`results/shadow_rider_regidrago_counter_als/README.md\`
- \`results/shadow_rider_regidrago_counter_als/reproduce.py\`
- \`.github/workflows/validate-shadow-rider-regidrago-counter-als.yml\`
- CI run 37592091862 passed.

Empirical source:
- Official CL2026 Aichi winner interview identifies Yasunori Kato's Shadow Rider Calyrex VMAX deck, says Mimikyu + Dialga-GX were deliberate inclusions, and reports Mimikyu Copycat responding to an opponent Regidrago VSTAR's Apex Dragon.
- Limitless list 26807 supplies the published 60-card list used for connector counts.

Durable findings:
- Mimikyu and Dialga-GX have asymmetric desired destinations: Mimikyu must become an attacker; Dialga-GX must be in the Shadow Rider player's discard for copied Apex Dragon.
- Mysterious Treasure can satisfy both destinations in one action when Dialga-GX is in hand and Mimikyu is in deck: discard Dialga as payment, search Mimikyu.
- With the named Aichi routing package, one generic disposable hand card, unlocked Items, and the list's connector counts, 15/16 coarse ordered zone pairs across {deck, hand, discard, prize} reach the bounded endpoint Mimikyu-in-hand + Dialga-in-discard before Prize taking.
- Unique miss: both singleton payloads Prized. Exact initial six-Prize probability is 0.8474576271%; exactly one Prized is 18.3050847458%.
- Dimension Valley reduces Mimikyu Copycat's deterministic attachment threshold from two Psychic Energy to one.
- Underworld Door only supplies Mimikyu while it is Benched, so attachment must precede promotion.
- Tulip recovery + Guzma promotion collides under the ordinary one-Supporter quota. Night Stretcher can recover Mimikyu while preserving Guzma's Supporter window.
- Canonical copy kernel reproduces Copycat -> Apex Dragon -> Timeless-GX, spends actor GX budget, schedules the extra turn, and preserves declared identity Copycat.

Interpretation:
This is a strong example of positive discard-cost semantics: a connector cost can route a payload to its required zone instead of acting as a scalar penalty. It also supports separating target access from target execution.

## Repository integration issue

Attempting to update the very large \`results/README.md\` through GitHub \`update_file\` was blocked by tool safety because the complete replacement payload is ~151 KB. The result directory itself is complete and validated. A future local-clone-capable incarnation can add the synthesis entry with a small patch.

## Next investigation

Study Regidrago-side counterplay against the Mimikyu response:
- Apex Dragon's declared identity is what Copycat sees, regardless of copied body.
- Determine which CL2026 Aichi Regidrago lists contained realistic direct attackers or alternative declared attacks that could avoid exposing Apex Dragon in the preceding turn.
- Preserve exact print identity and Energy/position requirements before calling any fallback realistic.
