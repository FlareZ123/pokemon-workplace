# Two conditional engines across one five-slot Bench: Ancient Wisdom, Giovanni's Exile, Lunar Cycle

## Question

If two conditional Ability engines require eight named Pokémon in total and therefore need seven simultaneous Bench slots, can a player realize both engines' effects during one turn while never exceeding the **ordinary five-slot Bench limit**?

**Yes.** A particular legal-paper-Expanded sequence uses Regigigas's Ancient Wisdom, Giovanni's Exile, Lunatone's Lunar Cycle, and Solrock's Sun Energy. The first engine's effect is resolved before two required Pokémon leave play. The second engine enters and resolves afterward.

This provides a concrete counterexample to interpreting a simultaneous prerequisite union as the number of slots required to **use both engines at different times**.

Implementation: `tools/regigigas_lunatone_temporal_multiplex.py`. The program maintains a materialized card-identity ledger, one Supporter window, three different Ability-use flags, precise Bench occupancy after each play, and legal off-board destinations.

## Exact Expanded card-text anchors

- **Regigigas** `swsh10-130`, *Ancient Wisdom*: once per turn with Regirock, Regice, Registeel, Regieleki, and Regidrago in play, attach up to three Energy cards from the discard pile to one Pokémon.
- **Giovanni's Exile** `sm10-174`: discard up to two undamaged Benched Pokémon and their attached cards. It is a Supporter, limited to the normal one Supporter per turn.
- **Lunatone** `me1-74`, *Lunar Cycle*: with Solrock in play, discard one Basic Fighting Energy from hand to draw three cards; maximum one Lunar Cycle per turn.
- **Solrock** `pgo-39`, *Sun Energy*: once per turn, attach one Psychic Energy from discard to a Lunatone.

Each named card has a legal Expanded print in the supplied repository database. The cited Giovanni's Exile print is marked Expanded legal. The 60-card demonstration also uses Basic Grass, Psychic, Fighting, and Water Energy, which do not have the same four-copy rule as non-Basic Energy.

## Controlled starting physical state

The fixture contains precisely 60 physical card copies across zones, including six Prize cards. Its contents are intentionally artificial to keep the sequence deterministic:

| Zone | Contents relevant to the example |
| --- | --- |
| Active | Regigigas |
| Bench (5) | Regirock, Regice, Registeel, Regieleki, Regidrago |
| Hand | Giovanni's Exile, Lunatone, Solrock, Basic Fighting Energy |
| Discard | 3 Basic Grass Energy, 1 Basic Psychic Energy |
| Deck | 40 Basic Water Energy |
| Prize cards | 6 Basic Water Energy |

The card count is `6 + 4 + 4 + 40 + 6 = 60`. All six Regi Pokémon already exist in play at the start of the examined turn. This is a turn-sequence witness rather than a claim that such an opening board is readily assembled, or that the illustrative Energy ratios are competitively useful.

The state assumes no Ability or Trainer lock, an unused Supporter window, no damage on the two Bench targets, and a turn on which Supporter play is allowed.

## Line A: Ancient Wisdom, then cleanup, then the new engine

1. Use **Ancient Wisdom** while the complete Regi group is in play. Materialize and attach three Basic Grass Energy from discard to the Active Regigigas.
2. Play **Giovanni's Exile** as the turn's Supporter, discarding the undamaged Benched Regirock and Regice with all attached cards. The Bench drops from five to three occupants. Ancient Wisdom's previously attached Energy remains on Regigigas.
3. Play **Lunatone** and **Solrock** from hand onto the Bench, one at a time. The occupancy becomes four, then five.
4. Use Solrock's **Sun Energy** to attach the Basic Psychic Energy from discard to Lunatone.
5. Use Lunatone's **Lunar Cycle**, discarding a Basic Fighting Energy card from hand and drawing three Basic Water Energy cards from the controlled deck.

The final board has Regigigas Active, three remaining named Regi Pokémon, Lunatone, and Solrock. It occupies precisely five Bench slots.

The result includes **three Grass Energy attached to Regigigas**, **one Psychic Energy attached to Lunatone**, and **three cards drawn with Lunar Cycle**. Giovanni's Exile, the two removed Pokémon, and Lunar Cycle's Fighting Energy are in the discard pile. Six Prize cards remain face down in the Prize zone.

Regigigas's complete named condition is no longer satisfied. Its earlier Ability use still contributed persistent material.

## Line B: Giovanni's Exile first

If Giovanni's Exile discards the two named Regi partners before Ancient Wisdom is used, the full named guard is lost.

The program verifies that Ancient Wisdom then cannot attach the three Grass Energy, which remain in discard. The player can still Bench Lunatone and Solrock, attach Psychic Energy with Sun Energy, and draw three cards using Lunar Cycle.

| Measured final state | Ancient Wisdom first | Giovanni's Exile first |
| --- | ---: | ---: |
| Basic Grass Energy added to Regigigas | 3 | 0 |
| Psychic Energy added to Lunatone | 1 | 1 |
| Cards drawn by Lunar Cycle | 3 | 3 |
| Peak Bench occupancy | 5 | 5 |
| Supporters played | 1 | 1 |
| Prize cards taken | 0 | 0 |

Thus the actions' relative order changes usable Energy acceleration while keeping the same final five-slot Bench topology.

## Why this matters for optimization

The [joint named-guard capacity result](../bench_joint_named_guard_capacity/) correctly proves that Ancient Wisdom's six required names and Lunar Cycle's two required names need seven Bench positions **if all eight are simultaneous**. This tested legal sequence instead **time-multiplexes** the condition sets:

`Ancient Wisdom -> retained Energy -> Giovanni's Exile -> free two slots -> Lunatone+Solrock -> Sun Energy -> Lunar Cycle`

The Supporter cleanup resource and order of actions replace the need for a persistent seven-slot Bench. This can be represented as a resource-constrained schedule with a conditional-effect deadline, a chosen Bench-release transition, and subsequent named-prerequisite reconstruction.

Such a route cannot be inferred from a static graph of simultaneously available Abilities. It requires preserving physical attachments, chosen discard targets, hand payments, Supporter usage, and changing Bench occupancy.

## Testing

Run `python tools/regigigas_lunatone_temporal_multiplex.py --self-test`.

Five tests establish:

1. the 60-card fixture and absence of the second named guard at the start;
2. the complete legal action order, attached cards, draw payment, supporter movement, bench occupancy, and exact total-card conservation;
3. inability to use Ancient Wisdom after prematurely removing its required partners;
4. rejection of Bench overflow, second Supporter use, duplicated targets, and Active selection for the Giovanni's Exile targets;
5. one-use restrictions for Ancient Wisdom, Sun Energy, and Lunar Cycle.

Run the script without flags to print an exact final-state comparison.

[GitHub Actions run 37921465934](https://github.com/FlareZ123/pokemon-workplace/actions/runs/37921465934) passed all five tests and the executable demonstration.

## Limits

No opening-hand consistency, Prize likelihood, resource-access probability, opponent response, damage, attack, matchup utility, or tournament win rate is modeled. The physical sample is a feasible turn configuration, with all required pieces deliberately supplied. The callback uses only the specific known Basic Energy interactions and known named Ability texts.

A complete action planner would also enforce Supporter play-time eligibility, relevant card-specific Ability suppression, other trainer-use history, and any replacement effects for discarding Pokémon. These are assumed favorable in the controlled example.

The result establishes an important distinction: **simultaneous setup occupancy** can exceed the **maximum occupancy needed by a sequential, effect-retaining plan**.
