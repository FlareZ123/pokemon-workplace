# Experimental Regidrago deck swap: Path to the Peak instead of Parallel City

## Precise deckbuilding proposal

Take the full, verified **2026 Aichi 10th-place Haruku Yoshioka Regidrago VSTAR 60** and make exactly one alteration:

`-1 Parallel City (xy8-145) +1 Path to the Peak (swsh6-148)`

The resulting [complete, print-resolved 60-card candidate](regidrago_path_swap_60.json) keeps the same 20 Pokémon, 30 Trainers and 10 Energy, including its Prime Catcher ACE SPEC. The new Stadium is recorded as **Expanded: Legal** in the bundled print snapshot. The [reproducer](reproduce.py) proves the exact one-card difference, preserves every other named quantity, verifies print categories/legality, and checks the effect interactions below.

This is an **experimental proposed matchup swap**. It has not been played head-to-head in a validated simulator and has no measured win-rate advantage over the event list. The actual published list retained Parallel City.

## Matched full-deck Ability suppression envelope

Count all copies of Pokémon with a printed Ability in the two real Aichi lists. For a card with an Ability, apply two actual rules: Psychic Pokémon survive Wobbuffet Bide Barricade; Pokémon **with a Rule Box in play** lose Abilities under Path to the Peak. The overlap must be unioned, never added.

| Simultaneous condition | Own Regidrago printed Ability copies suppressed / 11 | Opposing champion Shadow Rider printed Ability copies suppressed / 11 |
| --- | ---: | ---: |
| Neither lock | 0 | 0 |
| Active Wobbuffet only | 7 | 1 |
| Path to the Peak only | **8** | **10** |
| Active Wobbuffet and Path | **9** | **10** |

The additional suppression from Wobbuffet when Path is active hits only one extra own non-Rule-Box Ability bearer, **Kyurem Plasma Bane**. It adds zero opposing suppression in this particular champion list. Thus there is no static opponent Ability-coverage advantage from simultaneously maintaining the two locks once Path is active, even though the combined lock constrains one more own Ability.

The important target is Shadow Rider Calyrex VMAX **Underworld Door**, a Psychic Pokémon VMAX whose Rule Box means Path turns its in-play Ability off. Wobbuffet alone leaves all four copies of Underworld Door untouched. The Path swap therefore addresses a concrete weakness in Wobbuffet's Psychic-selective lock.

These are **card-copy-level potential effect counts**, conditional on locks actually in force and qualifying Pokémon occupying zones to which the lock applies. Path to the Peak only suppresses Rule Box Pokémon **in play**; a potential hand-triggered Ability cannot automatically be inferred suppressed just because the card has a Rule Box in the deck. There is no implication that 11 Abilities on either side are simultaneously active or useable.

## The free-retreat sequencing conflict

Regidrago's Psychic **Latias ex Skyliner** ordinarily gives the Basic Wobbuffet zero Retreat Cost. Wobbuffet has a printed two-Colorless Retreat Cost. Under Active Wobbuffet alone, Latias's Psychic typing exempts Skyliner.

Path to the Peak switches off Rule-Box Latias ex even though it is Psychic. **If Path is already active, Skyliner cannot pay the free Wobbuffet retreat**, unless a separate effect overrides the problem. Because retreating is an action and Stadium play can happen afterward in the same turn, one feasible ordering is:

1. Put Wobbuffet Active and Latias ex on the Bench and have a legitimate replacement Bench target.
2. Retreat Wobbuffet for free while Skyliner is working and the single normal retreat has not been used.
3. Play Path to the Peak *after* the Wobbuffet leaves Active.

This ordering ends with **Path-only lock** and an Active Regidrago replacement. Playing Path before retreat blocks this particular zero-cost mobility channel. It is a state-dependent argument, conditional on the needed cards being accessible and on the opponent not imposing separate restrictions. The combination **Wobbuffet Active + Path active** has greater self-inhibition than Path alone.

## Counterplay and opportunity cost

The champion Shadow Rider list has **two Sky Field**, **one Dimension Valley**, **one Field Blower** and **one non-Rule-Box Psychic Marshadow with Resetting Hole**. Every one of these named channels can potentially remove or replace the Stadium when available and playable. Psychic Marshadow's Ability is immune to Wobbuffet's Psychic exception; as a non-Rule-Box Pokémon it also survives Path. If it is Benched and allowed to use Resetting Hole, it can discard Path and itself. These are exact card-text counteraction channels; actual access and permission are not assumed.

The swap also forgoes **Parallel City's Bench-contraction direction** and its alternative attack-damage modifier. Against a deck benefiting from a large Bench, that opportunity cost could exceed the value of temporarily suppressing Rule-Box Abilities. The opponent can use an alternative Stadium on their turn unless prevented. Wobbuffet plus Path is not a permanent lock, and the published deck's own Marshadow may remove Path to reopen its VSTAR and draw Abilities.

## Priority for honest validation

A full evaluation should measure Path residence time, probabilities of opponent Stadium or Marshadow access, ordering constraints when Wobbuffet starts Active, own Regidrago Legacy Star denial, Prize tempo and forced Bench contraction opportunities under the original Parallel City. These dependencies are especially important against the champion. No real-game superiority conclusion follows from static lock coverage alone.
