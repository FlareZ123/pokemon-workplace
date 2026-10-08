# Typed full-hand reset transition profiles

## Question

The full-hand reset catalog identifies 15 canonical legal Expanded families, but a list of names is still too weak for sequencing.

Can those effects be compiled into a small typed transition layer that preserves the timing distinctions exposed by the pre-reset research?

Implementation: `tools/compile_reset_transition_profiles.py`  
Regression: `results/reset_transition_profiles/reproduce.py`

## Result

The compiler converts all 15 catalog families into transition profiles with these fields:

- source kind;
- draw count;
- source gate;
- Bench-slot requirement;
- Supporter cost;
- once-per-game GX/VSTAR resource;
- first-turn semantics;
- turn termination;
- whether the fresh hand remains actionable during the same turn;
- top-versus-bottom draw source;
- deck-position sensitivity.

The current distribution is:

| Property | Count |
| --- | ---: |
| Trainer / Supporter reset families | 5 |
| Ability reset families | 6 |
| Attack reset families | 4 |
| Ends the turn | 5 |
| Fresh hand actionable in the same turn | 10 |
| Consumes Supporter window | 5 |
| Consumes VSTAR Power | 1 |
| Consumes GX attack | 1 |
| First-turn-only | 1 |
| Going-first first-turn exception | 3 |
| Requires hand-to-Bench entry | 1 |
| Explicitly deck-position-sensitive | 1 |
| Can choose top or bottom draw source | 1 |

## Profile examples

### Dedenne-GX, Dedechange

- source: Ability;
- gate: play from hand to Bench;
- requires Bench space;
- draw 6;
- does not consume Supporter;
- fresh hand remains actionable in the same turn.

This is the Harto reset source that motivated the initial sequencing work.

### Squawkabilly ex, Squawk and Seize

- source: in-play Ability;
- first-turn-only;
- draw 6;
- does not end the turn;
- fresh hand remains actionable.

The timing gate is structurally different from Dedechange even though both discard the hand and draw six.

### Hisuian Zoroark VSTAR, Phantom Star

- source: in-play Ability;
- draw 7;
- consumes the once-per-game VSTAR Power;
- fresh hand remains actionable.

A planner that ignores the global VSTAR budget can overvalue the reset even when its hand transition looks excellent.

### Zamazenta V, Regal Stance

- source: in-play Ability;
- draw 5;
- ends the turn.

The fresh hand cannot be converted into more ordinary same-turn actions.

### Rayquaza-GX, Tempest-GX

- source: attack;
- draw 10;
- consumes the once-per-game GX attack;
- the attack ends the turn.

Its very large draw count therefore comes with two timing costs that a generic "draw 10" edge would erase.

### Ingo & Emmet

- source: Supporter;
- draw 5;
- explicitly looks at the top card;
- can draw the five cards from the top or bottom.

This profile is the clearest catalog-level example of why deck-position belief must remain separate from deck-composition belief.

## State-machine use

The profile layer is designed to be consumed by a future planner.

A legal action generator can first filter by:

- source gate;
- Bench capacity;
- first-turn state;
- Supporter availability;
- VSTAR/GX budget;
- attack legality.

The transition evaluator can then apply:

- full-hand discard;
- draw count and direction;
- turn termination;
- post-reset same-turn actionability.

This is substantially stronger than a scalar reset strength or raw draw-count ranking.

## Relationship to AMR and connector models

The profile fields make several previously qualitative AMR effects explicit.

Two effects with the same draw count can have different realistic availability because one needs a Bench slot or first-turn timing.

Two effects with different draw counts can reverse strategic value because one ends the turn or spends a once-per-game resource.

The same pre-reset Quick Ball line can also differ depending on whether the reset leaves a same-turn action window for the K1-informed fresh hand.

## Validation

The regression recompiles the legality-grounded reset catalog and asserts:

- exactly 15 typed profiles;
- source-kind split 5 / 6 / 4;
- five turn-ending families;
- ten same-turn-actionable fresh hands;
- five Supporter consumers;
- one VSTAR consumer;
- one GX consumer;
- one first-turn-only family;
- three going-first exception families;
- one hand-to-Bench / Bench-slot family;
- one top-or-bottom position-sensitive family.

It also pins representative profiles for Dedenne-GX, Squawkabilly ex, Hisuian Zoroark VSTAR, Zamazenta V, Rayquaza-GX, and Ingo & Emmet.

## Limits

This compiler covers only the literal `Discard your hand and draw N cards` catalog.

It does not yet infer:

- Energy requirements for attacks;
- Ability suppression channels;
- exact Pokémon evolution requirements;
- Supporter first-turn base rules beyond card-specific exception text;
- same-name once-per-turn Ability restrictions;
- hand replacement wordings that shuffle or bottom-deck instead of discarding.

Those belong in later profile layers.

## Next work

The strongest continuation is to compile all full-hand replacement effects, then normalize them into one transition interface with a `hand_destination` field such as discard, deck, bottom-deck, or mixed.

That would let the planner compare destructive resets with hand-preserving redraws using one state-transition vocabulary.
