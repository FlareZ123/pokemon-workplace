# Experimental Mew Battle VIP Pass 4: exact-print headless baseline and limits

## Physical deck transformation

The tournament-supported [2026 Aichi fifth-place Mew VMAX / Genesect V deck](../../decks/mew-genesect/) runs three Battle VIP Pass (`swsh8-225`) and two Special Red Card (`me4-82`). The [existing one-card experimental 60-card variant](../../decks/mew-genesect-vip4-aichi-counterfactual/) increases VIP Pass to four and reduces Special Red Card to one. All 59 other physical print selections remain unchanged.

[`simulation/twinleaf/candidate-deck-loader.cjs`](../../../simulation/twinleaf/candidate-deck-loader.cjs) takes the already strictly print-mapped 60-card tournament list, finds the exact implemented full names of these two proven print categories, substitutes one card, and preserves the original list without mutation. Its [standalone source-to-engine regression](../../../simulation/twinleaf/test-candidate-deck-loader.cjs) passed in [manual CI 38295103438](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38295103438). The original remains a published tournament deck; `mew_genesect_vip4` is an experimental variant.

- Published baseline physical multiset SHA-256: `1927c70acb90db7015547945fe43b3482f878fe655b656cee8e8de109c16b92f`.
- VIP4 variant physical multiset SHA-256: `4c9ebc594b152bb59d82a31d02b320b7b7192c5551bc99d84296040a87bf3b03`.
- Headless experiment pin: Twinleaf `3348ebdc898f175a2ed8f999133cd13d1afd01f5`, `SimpleTacticsAi` native priority, live RNG isolated from speculative policy RNG, research uniform shuffle hook, 350 actions/25 seconds per game.
- Exact experimental seeds: `20261012`, `20261013`; both orientations per seed. The [manual workflow](../../../.github/workflows/twinleaf-manual-matchup.yml) offers a bounded chooser for these deck IDs.

## Four complete headless game observations

| Seed | Seat 1 deck | Seat 2 deck | Winning deck | Finish turn |
| --- | --- | --- | --- | ---: |
| 20261012 | Published Mew | VIP4 Mew | Published Mew | 32 |
| 20261012 | VIP4 Mew | Published Mew | VIP4 Mew | 28 |
| 20261013 | Published Mew | VIP4 Mew | Published Mew | 54 |
| 20261013 | VIP4 Mew | Published Mew | VIP4 Mew | 54 |

All four games finished with no error, draw or cap. The deck-score aggregate was published Mew two wins, VIP4 Mew two wins. **Player seat 1 won every game**, despite decks swapping seats. That pattern raises additional policy and seat-comparability concerns with such a tiny sample.

More fundamentally, the per-seat `cards_played` and `abilities` counters collected by the instrumentation show:

- **Zero Battle VIP Pass plays** across all four games and both deck orientations. The key setup Item whose quantity changed was never actually activated in these native-bot traces.
- **Zero Fusion Strike System Ability activations**, despite Mew/Genesect being the selected archetype and Genesect V appearing on both boards. The full reason may include hand-size thresholds, available actions, and stadium-based Ability suppression; this dataset does not isolate which.
- Two of the losing seats played Special Red Card, but this cannot establish the marginal value of either copy.

Thus, the headless mirror demonstrates that the exact physical variant can be loaded and played in a full native engine game. **It does not meaningfully discriminate the advantage of one additional first-turn Battle VIP Pass**, and the 2–2 score should not decide which deck is stronger.

## Stronger relevant existing evidence

The independent [Mew VIP opening access model](../../mew_genesect_vip_opening/) assesses a narrowly defined first-turn access endpoint with the two source quantities, without asking an unskilled full-game policy to use the cards. That targeted calculation is the more informative evidence at present. Its constraints and omitted opponent disruption still matter; a stronger policy and diverse full-game opponent field are necessary before claiming the variant improves match wins.

Next steps: test whether a player can correctly execute a Battle VIP Pass turn-one line in the native engine and develop a prompt/decision policy that actually deploys the Item, relevant search costs and Fusion Strike System when beneficial. Keep any engine implementation correction separate from the native source code and maintain one reviewed policy version per comparison.

Evidence type: source-verified 60-card print transformation, source-derived restricted access calculation, and exact headless engine traces. No validated competitive win-rate inference.
