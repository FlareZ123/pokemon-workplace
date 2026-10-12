# Exhaustive two-type Super Rod/Crispin continuation frontier

This extends the [physical Trifrost witness](README.md) from one matched state to every distinct **hand/deck/discard count configuration** of the published Aichi list's four Basic Grass and two Basic Fire Energy.

## Model assumptions

Both Basic types have at least one copy in hand before the player chooses which Basic to attach to an Active Regidrago VSTAR already holding one DDE. The player also has a second DDE, Super Rod, and Crispin available for the following turn. Apex Dragon copies Kyurem Trifrost and discards the attached DDE and chosen Basic. The opponent leaves the Regidrago in play, and the next turn can legally draw a card. Before the next attack, at most one Super Rod shuffles up to three Basic Energy from discard into deck, Crispin searches two different Basic types and attaches one, and the one normal Energy attachment uses the second held DDE. No additional discard outlet, Energy accelerator, draw/search, lock, Stadium change, or intervention is permitted.

The goal is **next-Apex Energy readiness**. Both Basic Grass and Fire individually complete the attack's Grass/Grass/Fire cost when paired with DDE's two flexible Energy units.

## Exact necessary and sufficient condition

For a particular Basic type `t`, let `d_t` and `x_t` be its pre-choice copies in deck and discard. If type `c` is chosen as the attached/discarded Basic for Trifrost, then:

`next Apex ready <=> d_Grass + x_Grass + [c=Grass] >= 1 AND d_Fire + x_Fire + [c=Fire] >= 1`.

**Necessity:** Crispin's attach route requires a Grass and a Fire in the deck. Super Rod can only shuffle Basic Energy already in discard. The chosen payment adds exactly one copy of its type to discard, leaving no way to supply an initially inaccessible type that was neither chosen nor already outside the hand.

**Sufficiency:** Super Rod can shuffle up to three Basic cards. If necessary, shuffle one Grass and one Fire from the discard pile into deck (two cards is within the limit), leaving at least one of each type searchable. Crispin attaches either Basic to Regidrago, and the held second DDE manually attaches for a legal Apex Dragon cost.

## Complete Aichi partition table

Of the possible `(hand, deck, discard)` counts for a Basic type, require at least one copy in hand. For `n` total cards of that type, there are `n(n+1)/2` distinct such count triples.

| Choice outcome | Number of distinct Aichi type-count partitions |
| --- | ---: |
| Both Grass and Fire payments have a ready route | **18** |
| Only paying **Fire** has a ready route | **9** |
| Only paying **Grass** has a ready route | **2** |
| Neither payment has a ready route | **1** |
| **Total** | **30** |

For general positive copy counts `G,F`, let `A=G(G+1)/2` and `B=F(F+1)/2`. The four category counts are, respectively, `(A-1)(B-1)`, `A-1`, `B-1`, and `1`. Here `A=10`, `B=3`.

A Fire-only case has **every Fire in hand** and at least one Grass in deck or discard. A Grass-only case reverses the type roles. Both fail when *every Basic of both types is in hand*. Cases where both succeed have at least one Basic of each type already accessible outside the hand.

**Counting caveat:** The 30 configurations are counted once each, ignoring the very different probabilities of drawing their physical copies, Prize placement, timing, Supporter access, and opponent responses. The 9 versus 2 result is a **type-configuration count**, not a 9:2 frequency ratio or a win-rate estimate.

## Verification

The [partition calculator](../../../tools/aichi_regidrago_super_rod_partition_frontier.py) independently enumerates all allowable Super Rod Basic returns (up to three) and both Crispin attachment roles for all **60** Aichi payment/configuration combinations. It proves agreement with the logical condition. The [reproducer](partition_reproduce.py) verifies the actual published list's four Grass/two Fire count and the four outcome categories.

The general closed-form formula is checked against exhaustive partition enumeration for **36** further copy-count pairs with `G,F` each ranging from one through six. Run `python -m results.tests.aichi_regidrago_super_rod_bridge.partition_reproduce`.

In actual play, tools such as Quick Ball and Mysterious Treasure can discard otherwise stranded Basic Energy from hand before Super Rod. Earlier discarded Energy or prior prize-recovery decisions also change the boundary. The rule is a precise restricted-action model that can be embedded in a larger deck policy, with those alternatives explicitly represented.
