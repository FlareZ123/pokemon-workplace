# Knock Out trigger cascades require growable pending membership

## Question

Can the set of Pokémon waiting to be discarded for a Knock Out be treated as
fixed once the first KO check has identified its members?

No. Expanded contains legal KO-trigger Abilities that can cause another Pokémon
to become Knocked Out while the original KO-trigger window is still resolving.

Implementation:

- `tools/ko_cascade_text_catalog.py`
- `tools/growing_knockout_context.py`

Regression:

- `results/knockout_cascade_growth/reproduce.py`

## Rule and card evidence

The bundled Advanced Player's Rulebook Ver. 3.4 separates Knock Out handling
into a trigger phase and a later disposal phase. Effects activated by a Knock
Out are applied before the Knocked Out Pokémon and attached cards are
discarded.

Current Gengar ex from 30th Celebration has **Fainting Spell**:

> If this Pokémon is Knocked Out by damage from an attack from your opponent's
> Pokémon, flip a coin. If heads, the Attacking Pokémon is Knocked Out.

The February 2026 TPCi Professor rules update also states that when one effect
triggers another effect, the initial effect finishes first and the newly
triggered effect is handled afterward.

Sources:

- https://www.pokemon.com/uk/pokemon-tcg/pokemon-cards/series/30th/90/
- https://professorprogram.pokemon.com/news/11473085
- bundled `resources/advanced-players-rulebook.md`

Taken together, a heads branch can begin with only the defending Gengar ex
pending, then add the Attacking Pokémon to the KO state before the common
discard / Prize boundary finishes.

## Card-pool audit

A conservative text scan of the current effectively legal Expanded pool finds
**14 print rows across 11 card names** in two high-confidence cascade families:

| Family | Legal print rows | Meaning |
| --- | ---: | --- |
| direct attacker KO | 7 | KO-trigger text directly says the Attacking Pokémon is Knocked Out |
| attacker damage counters | 7 | KO-trigger text places damage counters on the Attacking Pokémon and can therefore create an additional KO depending on remaining HP |

Direct-attacker-KO names in the snapshot include Froslass, Gengar ex, Weezing,
Galarian Cursola, and Chandelure.

The damage-counter family includes Pyukumuku, Maractus, Mismagius, Qwilfish,
Golem, and Voltorb.

The bundled card database currently contains a typo in both 30th Celebration
Gengar ex print rows, spelling "Knocked Out" as "Knocket Out". The catalog
normalizes only that exact spelling for matching. The official Pokémon card
database provides the correct wording.

## State consequence

The earlier `PendingKnockOutBatch` is intentionally a frozen pre-discard
snapshot. That is useful once the complete batch is known, but a caller cannot
assume the first discovered KO set is complete.

`GrowingKnockOutContext` adds a pre-batch layer:

1. keep each player's conserved board state intact;
2. record the currently pending Pokémon IDs, allowing either side to start
   empty;
3. add later KO members idempotently while trigger effects resolve;
4. only after pending membership stabilizes, materialize ordinary
   `PendingKnockOutBatch` objects and hand them to the existing cross-player
   promotion/disposal layer.

The regression begins with only player B's Active pending. A Fainting Spell-like
heads result then marks player A's Attacking Active as another KO. Both pending
batches are materialized afterward, the next player chooses promotion first,
both Active cards enter discard, and each player's physical card totals remain
conserved.

## Finding

**The KO disposal batch can be atomic while KO membership is dynamic.**

Those are different boundaries. A simulator should accumulate all KOs and
newly triggered effects that arise before the disposal phase, then freeze and
execute the final physical batch.

This distinction matters for Prize counts, terminal checks, promotion
eligibility, and secondary KO triggers.

## Limits

The new context tracks growing KO membership only. It does not discover
card-specific triggers, execute coin flips, or mutate board state for arbitrary
trigger effects.

Some KO triggers do more than add another KO. They can search cards, move
Energy, return cards to hand, modify Prize awards, or create other state changes.
A complete trigger scheduler needs to execute those semantics sequentially and
then freeze the final pending KO membership at the disposal boundary.
