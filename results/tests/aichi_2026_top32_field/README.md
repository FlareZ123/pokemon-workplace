# Aichi Open League 2026: source-grounded top-32 opponent field and paired test plan

## Why this field matters

The **strongest possible paper Expanded deck** should be evaluated against varied competitive opponents. Ranking decks only by the May 10, 2026 Aichi final standings would overemphasize the champion and runner-up; the archetype makeup of successful finishers is materially different. [Limitless's event statistics](https://limitlesstcg.com/tournaments/566/statistics) report 926 event players but enumerate 32 **successful-finisher archetype classifications**. These 32 have selection bias and **must not be treated as the full entrant distribution, as representative registration shares, or as head-to-head win rates**.

The [frozen source-data snapshot](field.json) preserves the published categorical counts. A source-proxy link points to a particular project-verified 60-card deck, *not necessarily the exact list played by every finisher in that archetype*.

| Archetype in the successful top 32 | Finishers | Share of top 32 | Closest complete verified English-paper proxy |
| --- | ---: | ---: | --- |
| Regidrago | 11 | 34.375% | [10th-place Regidrago VSTAR](../../decks/regidrago-vstar/) |
| Mega Absol Box | 5 | 15.625% | [8th-place Mega Absol/Garbodor](../../decks/mega-absol-garbodor/), subtype proxy |
| Raichu Electrode Combo | 3 | 9.375% | [4th-place Raichu/Electrode](../../decks/raichu-electrode-aichi-2026/) |
| Iron Thorns | 3 | 9.375% | [English adaptation of 6th-place Japanese list](../../decks/iron_thorns_aichi_english/), explicitly modified |
| Snorlax Stall | 2 | 6.25% | **Missing validated English 60** |
| Shadow Rider Calyrex | 1 | 3.125% | [Champion's exact-name 60](../../decks/shadow-rider-calyrex/) |
| Vileplume Control | 1 | 3.125% | [Runner-up 60](../../decks/vileplume-control/) |
| Mew Genesect | 1 | 3.125% | [5th-place 60](../../decks/mew-genesect/) |
| Mega Lopunny | 1 | 3.125% | Missing |
| Raging Bolt | 1 | 3.125% | Missing |
| Lillie's Clefairy | 1 | 3.125% | Missing |
| Meloetta Donk | 1 | 3.125% | Missing |
| Dusknoir Chimecho | 1 | 3.125% | Missing |

The seven verified proxy categories cover **25 of the 32 top-32 finishes (78.125%)**, spanning seven of 13 source archetypes. Those percentages reflect *availability of a research proxy for an archetype*, **not** how faithfully one representative 60 models every deck under that label. Missing seven finishers include two Snorlax and one of each of five other archetypes.

## Reproducible and deliberately incomplete test plans

[Research-owned scheduler](../../tools/aichi_2026_field.py) provides two compatible test scenarios:

- **Observed successful-finish frequency:** for every candidate, schedule one seed per represented top-32 source finisher, using the currently available seven deck-proxy classes. This gives exactly **25 paired comparisons**, each replayed with the candidate and opponent switching seats, so **50 planned games per candidate**, including explicitly marked mirror controls. This is a high-performance *stress case*, not a population estimate.
- **Equal available archetype categories:** schedule one paired, seat-swapped comparison against each of the seven available proxies, so **14 planned games per candidate**. This reduces the influence of Regidrago's 11 top-32 finishes and is useful for diversity checks, but still omits six unimplemented archetypes.

The tool does not start Twinleaf, pretend cards have been implemented, or assign match outcomes. It emits exact proxy names, opponent class, orientation, shared pair seed, scenario, and mirror flag. Pairing controls initial PRNG state and seat assignment; it does not guarantee equivalent hidden cards or first turn. When actual games run, a verified engine pin, deck hashes, bot policy, card-effect semantics and missing-archetype policy must be recorded. Avoid aggregating unfinished matches into wins.

## Independent validation

[Reproducer](reproduce.py) independently transcribes all 13 source counts, checks 32 total and the precise 7/13 coverage, confirms every referenced proxy page exists, and validates deterministic ordering, 2-seat pairing, source-count frequency and mirror flags across 14 candidate/scenario schedules. Run `python results/tests/aichi_2026_top32_field/reproduce.py` from the repository root. [Manual Windows workflow](../../../.github/workflows/validate-agent2-aichi-opponent-field.yml) is the CI entry point; it does **not** execute computationally expensive game simulations.

## Unresolved research priority

The largest missing successful category is **Snorlax Stall (two top-32 placements, including third place)**. Its Japanese source list contains Player's Ceremony without an equivalent English print, requiring an explicitly legal, tested adaptation. The source's Regidrago, Mega Absol, Raichu, Iron Thorns, and Snorlax classes collectively occupy 24/32 positions, so testing counterplay into these styles deserves priority. A strong tournament champion that loses systematically to numerous Regidrago variants may be a poor varied-field choice. This remains a matchup **hypothesis** until the engine and game policies provide validated results.

Keep both the observed-top32 scenario and equal-archetype scenario as distinct lenses. Add more varied-fields from other tournaments over time and do not overfit to a single Japan event.
