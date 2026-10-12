# Aichi Shadow Rider: next-turn Max Geist Energy readiness

## Question and source basis

The [2026 Aichi champion Shadow Rider deck](../../decks/shadow-rider-calyrex/) has 4 Shadow Rider Calyrex VMAX, 11 Basic Psychic Energy, 1 Radiant Eternatus, 2 Sky Field and 1 Dimension Valley. Prior [Radiant launch analysis](../../shadow_rider_radiant_launch/) computes opening access, and [dual-entry analysis](../../shadow_rider_dual_entry_launch/) includes Wonder Tag. This study models the separate **next-turn attack Energy gate** once two VMAX have already entered on the Bench.

Verified bundled printed effects:

- Shadow Rider Calyrex VMAX (swsh6-75): each Underworld Door attaches 1 Psychic from hand to a *Benched Psychic Pokémon*, then draws 2. Max Geist costs 3 Colorless and deals 10 + 30 per Psychic Energy across your Pokémon.
- Radiant Eternatus (swsh12pt5-105): Climactic Gate can place two VMAX onto the Bench from the deck and **ends the player's turn**.
- Dimension Valley (xy4-93) reduces Psychic Pokémon attack costs by one Colorless; Max Geist then needs 2 instead of 3 Energy.
- Sky Field (xy6-89) supplies up to 8 Bench slots. Replacing it with Dimension Valley can force a contraction to 5; this matters for a crowded board even though the minimal Radiant-plus-2-VMAX Bench uses 3 slots.

## Model

Condition on two usable Underworld Door sources, an initially uncharged *Benched* VMAX Energy target, h Psychic Energy in hand, e Psychic Energy among n remaining shuffled deck cards, and one unspent normal attachment. Use each live Door when an Energy is in hand; spend that Energy on the intended Benched target, then draw 2 without replacement. The manual attachment goes last. This policy maximizes this narrowly specified attack-charging endpoint. A separate legal promotion to Active is assumed and unpriced.

For an illustrative conditional state **e=8, n=41**, exact fractions give:

| h in hand | Normal Max Geist (3 Energy) | Dimension Valley (2 Energy) |
| ---: | ---: | ---: |
| 0 | 0.000000% | 0.000000% |
| 1 | 14.059445% | 35.609756% |
| 2 | 59.593167% | 100.000000% |
| 3+ | 100.000000% | 100.000000% |

Exact fractions for h=1 are 7119/50635 (cost 3) and 73/205 (cost 2). For h=2, cost 3 is 6035/10127. These reflect only the conditional resource-window randomness. The sample Energy split is an illustrative reachable-sized state, not a measured distribution after opening.

In a one-turn uncharged target scenario, only one usable Door plus the ordinary attachment cannot supply the unreduced three-Energy attack cost. This makes preservation of both live VMAX sources strategically consequential. If the targeted VMAX is Active during charging, the printed Bench-target restriction prevents using Underworld Door to attach Energy to it. A post-charge legal promotion is essential.

Dimension Valley can enable an earlier attack while leaving fewer total Psychic Energy attached, lowering the damage available through Max Geist's per-Energy scaling. Because Sky Field and Dimension Valley are competing Stadiums, the faster attack can also have Bench-capacity costs.

## Validation and limitations

The library at [tools/shadow_rider_post_launch_energy.py](../../../tools/shadow_rider_post_launch_energy.py) computes exact rational probabilities by dynamic programming over hand Energy, deck Energy, deck size and target attachments. The [reproducer](reproduce.py) independently enumerates all placements of Psychic cards for deck sizes 0..8, all count splits, h=0..3, and attack costs 0..4. It also checks closed-form cases and the printed card texts. Offline mathematical tests passed on 12 October 2026. No GitHub Actions run or head-to-head match simulation is claimed.

This conditional computation does not price launch probability, search discards, Prize cards, Energy already in play, pivot resources, remaining Bench positions, Stadium access, opponent's intervening turn, Ability lock, damage thresholds, Supporter contention or real match outcomes. The next step is to integrate this Energy continuation with agent7/12/35 source-aware launch distributions, retaining joint card-zone information instead of multiplying marginal percentages. The overall goal remains full-game competition across validated playable 60-card decks.
