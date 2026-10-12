# Mega Scrafty reactive counter-stack resource frontier

## Purpose and status

A **source-validated static frontier**, not evidence of competitive win rate, for an Active Mega Scrafty ex (Ascended Heroes `me2pt5-135`) damaged by an opposing Pokémon's attack. The bounded snapshot is *after* the attack's outside-damage effects and *before* the damaged-by-attack reaction window and Knock Out removal, so a removed reaction source cannot trigger. The attacker is assumed to receive the resulting damage counters without prevention, and damage must be positive.

## Exactly verified printed sources

- Mega Scrafty ex `me2pt5-135`, Counterattacking Crest, **5 counters**, only while its Ability functions and it remains Active.
- Spiritomb `me1-87`, Spiteful Swirl, **1 counter for each functioning copy** while the player's Active Pokémon is Darkness; up to four separate Spiritomb can use Bench spaces.
- Spiky Energy `sv9-159`, **2 counters for each physically attached copy**, up to four deck copies; the associated Pokémon must still be Active when reaction eligibility is checked.
- Punk Helmet `me2-92`, **4 counters**, requires Darkness Active Pokémon and functioning attached Tool.
- Deluxe Bomb `sv7-134`, **12 counters**, an **ACE SPEC**, uses the same single Tool slot as Punk Helmet and discards itself when its counters are successfully placed.

All five source prints pass the supplied card pool's Expanded set flags and the repository's effective per-print legality gate as of **2026-10-12**. The reproducer checks exact source text fragments, relevant Pokémon Stage, attack cost, Tool class and ACE SPEC class to detect data drift.

## Exact deterministic frontier

With one Active Mega Scrafty, four Benched Spiritomb, and four Spiky Energy on the Active:

| Tool | Counter total | HP-equivalent | Consequence |
| --- | ---: | ---: | --- |
| Punk Helmet | 21 | 210 | Reusable while attached and source alive |
| Deluxe Bomb | **29** | **290** | Single ACE SPEC, consumed after actual placement |

The maximum changes to **20 counters under Ability lock**, **17 under Tool-effect suppression**, and **8 under both** (with Spiky Energy still functional). Counter placement prevention and removal of attached Spiky Energy before the post-damage reaction window are distinct threats outside the simplified lock switches.

For the Deluxe Bomb source and the two bounded resource axes (number of Spiritomb and number of Spiky Energy), the exact Pareto-minimal pairs to reflect at least a target amount are:

| Attacker remaining HP | Pareto-minimal (Spiritomb, Spiky) |
| --- | --- |
| 160 | (0, 0) |
| 220 | (0, 3), (1, 2), (3, 1) |
| 280 | (3, 4) |
| 290 | (4, 4) |
| 300 | impossible in this isolated stack |

Each solution above assumes the functioning Mega Scrafty Ability, Deluxe Bomb, and the specified set of other sources. These are counter-placement values, so Weakness and Resistance do not multiply them. The two explicit costs being minimized are Bench occupancy and Spiky Energy attachments, with ACE SPEC opportunity cost and other cards held fixed.

## Practical constraints and interpretation

Mega Scrafty is a **Stage 1 evolved from Scraggy**, so ordinary evolution needs a later turn. Four Spiky Energy require four separate hand attachments absent acceleration. Because Spiky supplies Colorless while Outlaw Leg costs two Darkness and one Colorless, attacking with a full four-Spiky stack also requires at least two Darkness attachments. Under ordinary evolution and one manual attachment per own turn, the *optimistic lower bounds* are **turn 4 for a 290-counter reaction** and **turn 6 for an Outlaw Leg attack**. Drawing, searching, Prizing, switching, attaching a Tool, protecting the bench and the opponent's counterplay may delay or prevent execution. Mega Scrafty also gives up three Prize cards if Knocked Out.

Only a reactive source snapshot is computed. A full Pokémon TCG engine must check copied attacks, damage prevention, opponent identity, step-5 source removal, dynamic Ability/Tool lock, Energy removal, and cumulative HP before applying a stack. Actual win probability, matchups, access consistency, ACE SPEC opportunity cost, and defender survival are **unmeasured**. This result is a reproducible interaction upper bound, not a proposed best decklist.

## Reproduction

Run `python results/reactive_counter_stack_frontier/reproduce.py` from the repository root. It validates source cards, exact frontiers for all counter thresholds 0 through 30 and all three Tool choices, and lock counterfactuals. Windows CI workflow: `.github/workflows/validate-reactive-counter-stack-frontier.yml`.

Related prior research: [physical_copy_damage_reaction_bridge](../physical_copy_damage_reaction_bridge/), [physical_energy_backlash_reactions](../physical_energy_backlash_reactions/), [optional_overkill_reflection](../optional_overkill_reflection/).

Rules: supplied Advanced Player's Rulebook sections A-01, E-03, C-07, E-12 and general Tool, Energy, and deck-building rules.
