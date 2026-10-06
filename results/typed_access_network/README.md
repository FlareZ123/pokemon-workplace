# Typed Supporter-access network: preserving zones and action windows

## Question

Can a small state-transition model distinguish valid Gladion access lines from graph paths that look connected but violate timing, zones, or lock constraints?

Yes. This result implements a minimal typed access engine and verifies representative Expanded routes.

Implementation: tools/typed_access_network.py

Regression cases: results/typed_access_network/reproduce.py

## Representation

The model preserves:

- card zone: deck, hand, Bench, discard, or played;
- whether the current Supporter window has already been used;
- current Supporter-window index;
- Bench occupancy and limit;
- whether Items are allowed;
- whether Abilities are allowed;
- whether Supporters are allowed.

A manual play from the hand onto the Bench emits a distinct event from an effect that moves a card from the deck directly onto the Bench.

The only triggered Ability currently implemented is Tapu Lele-GX's Wonder Tag. It resolves only after the hand-to-Bench play event and only while Abilities are allowed.

The engine intentionally covers a small semantic kernel. It is designed to test representations before adding more cards.

## Four core regression lines

### Quick Ball -> Tapu Lele-GX -> Gladion

Initial modeled resources:

- Quick Ball in hand;
- one discard-fodder card in hand;
- Tapu Lele-GX in deck;
- Gladion in deck;
- open Bench space;
- Items, Abilities, and Supporters allowed.

The engine finds the current-window line:

1. Quick Ball moves Tapu Lele-GX from deck to hand and pays its one-card discard cost.
2. Tapu Lele-GX is manually played from hand to Bench.
3. The hand-to-Bench event activates Wonder Tag, moving Gladion from deck to hand.
4. Gladion is played in the current Supporter window.

This confirms that the engine treats the Pokémon-search edge and the Ability-trigger edge separately.

### Nest Ball -> Tapu Lele-GX

With Nest Ball in hand, Tapu Lele-GX in deck, and Gladion in deck, the engine finds no Gladion play.

Nest Ball moves Tapu Lele-GX directly from deck to Bench. That transition does not emit the hand-to-Bench play event, so Wonder Tag does not activate.

The card graph remains superficially connected:

Nest Ball -> Tapu Lele-GX -> Wonder Tag -> Gladion

but the typed transition graph correctly breaks the second edge.

### Battle Compressor -> VS Seeker -> Gladion

With Battle Compressor and VS Seeker in hand and Gladion in deck, the engine finds:

1. Battle Compressor moves Gladion from deck to discard.
2. VS Seeker moves Gladion from discard to hand.
3. Gladion is played in the current Supporter window.

This route demonstrates that an indirect zone path can be valid when each zone transition is represented accurately.

### Skyla -> Gladion

With Skyla in hand and Gladion in deck, the engine finds no current-window Gladion play.

Skyla can move Gladion into the hand, while playing Skyla consumes the current Supporter window. When one future Supporter window is permitted, the shortest line becomes:

1. play Skyla and find Gladion;
2. advance to the next Supporter window;
3. play Gladion.

A reachability graph that ignores action-window consumption would incorrectly label this as current-turn access.

## Constraint regressions

The reproducer also verifies three state constraints.

### Ability lock

Quick Ball can still put Tapu Lele-GX into the hand and the player can still Bench it. Wonder Tag does not resolve while Abilities are disabled, so no Gladion play is found.

### Full Bench

Quick Ball can put Tapu Lele-GX into the hand, while the manual Bench action is unavailable when the modeled Bench already contains five Pokémon. No Gladion play is found.

### Item lock

The Battle Compressor -> VS Seeker chain has no legal transition while Items are disabled.

These examples show how lock effects and board capacity remove graph edges rather than merely lowering a generic card score.

## Why typed edges matter

A conventional card-association graph could assign all four core examples a path to Gladion. The paths differ in strategically decisive ways:

| Route | Gladion reachable in current Supporter window? | Why |
| --- | --- | --- |
| Quick Ball -> Tapu Lele-GX | Yes | Search enters hand, then manual Bench play fires Wonder Tag |
| Nest Ball -> Tapu Lele-GX | No | Search places directly on Bench, so Wonder Tag's hand-play trigger is absent |
| Battle Compressor -> VS Seeker | Yes | Correct deck -> discard -> hand zone sequence uses only Items |
| Skyla -> Gladion | No | Skyla consumes the current Supporter window |

This supports a stronger representation of connector realism. A useful edge should encode the resource and state transformation that makes the next edge legal.

## Relation to AMR and connector domination

The typed engine currently answers whether a line is mechanically available within the represented state. It does not decide whether the line is strategically desirable.

For example, Quick Ball -> Tapu Lele-GX -> Gladion can be mechanically valid while still having poor Active Move Realism because:

- the discard cost may consume a protected card;
- the Bench slot may be needed by another Pokémon;
- placing a two-Prize Rule Box Pokémon may create a liability;
- Quick Ball may have a stronger competing target;
- Gladion may contend with another required Supporter.

The typed transition layer should therefore sit below strategic evaluation. It prevents false mechanical paths before AMR, DCI, connector domination, and matchup value are applied.

## Validation

results/typed_access_network/reproduce.py contains assertions for every line described above.

Expected outcomes:

| Regression | Expected result |
| --- | --- |
| Quick Ball -> Tapu Lele-GX | Current-window Gladion line exists |
| Nest Ball -> Tapu Lele-GX | No Gladion line |
| Battle Compressor -> VS Seeker | Current-window Gladion line exists |
| Skyla | No current-window Gladion line |
| Skyla with one future window | Future-window Gladion line exists |
| Quick Ball/Tapu Lele-GX under Ability lock | No Gladion line |
| Quick Ball/Tapu Lele-GX with full Bench | No Gladion line |
| Battle Compressor/VS Seeker under Item lock | No Gladion line |

The engine uses breadth-first search over immutable states, so the reported line is the shortest represented action sequence.

## Scope limits

This is not a full rules engine.

It does not yet model turn ownership, attacks, Energy, evolution timing, Prize effects, deck order, stochastic effects, card multiplicity, arbitrary targets, Supporter lock generated by specific cards, opponent state, or actual damage.

The implementation also hard-codes a few representative card actions instead of parsing arbitrary card text. That is intentional for this stage. The purpose is to establish the minimum semantics a more general access engine must preserve.

## Next useful work

Two extensions now have clear value.

First, add an attack boundary and one attack-based Supporter search so the same engine can prove that an attack reaches Gladion only for a later turn.

Second, connect the typed deterministic network to the exact timed-access probability model. The combined model should treat deterministic Items and Abilities as targeted transitions, stochastic Items as probability branches, and generic random draw as the existing cards_seen_by_window process.

That combination would allow deck-specific Prize-rescue estimates without reducing all access routes to equivalent outs.
