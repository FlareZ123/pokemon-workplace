# Whole-stack zone-exit conservation

## Question

How should a simulator represent effects that remove a Pokémon from play by
putting it into a hand or deck?

The physical evolution stack must remain conserved. Attached cards also leave
their board relations, although their destination can differ from the
Pokémon's destination.

Implementation: `tools/stack_zone_exit_conservation.py`  
Regression: `results/stack_zone_exit_conservation/reproduce.py`

## Rule and card basis

The Advanced Player's Rulebook section C-02 states that when a Pokémon in play
is put into its player's hand or deck, its damage counters and effects are
removed. If the Pokémon is evolved, all previous Evolution cards go with it.

That rule makes a top-card-only move incorrect for evolved Pokémon.

Expanded card text then determines where attached cards go. Representative
Black & White onward examples from the provided card database are:

| Card | Database ID | Resolved physical routing |
| --- | --- | --- |
| Scoop Up Cyclone | `bw10-95` | Pokémon stack to hand; all attached cards to hand |
| Super Scoop Up | `bw1-103` | on heads, Pokémon stack to hand; all attached cards to hand |
| Cassius | `xy1-115` | Pokémon stack to deck; all attached cards to deck |
| AZ | `xy4-91` | Pokémon stack to hand; all attached cards to discard |
| Accelgor | `bw5-11` | Deck and Cover shuffles the attacking Pokémon stack and all attached cards into the deck |
| Flapple | `swsh2-22` | Apple Drop can shuffle a Stage 1 Pokémon stack and all attached cards into the deck |

The database marks each cited printing Expanded legal, and every cited set is
Black & White or later.

## Representation

`leave_play_with_conservation()` consumes a
`StackBoardMaterialState` and two resolved destinations:

- `pokemon_destination` applies to every physical Pokémon card in the
  evolution stack;
- `attachment_destination` applies to every attached physical card.

The transition removes the persistent board object, routes every materialized
card out of its board relation, validates the resulting board, and checks the
existing physical-card conservation invariant.

This creates one mechanical transition family for several card-text families.
Card semantics remain responsible for target legality, optionality, randomness,
and destination selection.

## Findings

### Previous Evolutions are part of the exit boundary

An evolved in-play object cannot move only its top card. If a Bulbasaur ->
Ivysaur object is scooped to hand, both physical Pokémon cards leave play.

The same applies to deck-return effects. Cassius or an appropriate self-shuffle
effect sends the complete physical stack to the deck.

### Attachment destination is independent

The Pokémon stack and attachments share a board-object exit event, while they
can resolve to different ordinary zones.

Scoop Up Cyclone uses hand for both groups. Cassius uses deck for both groups.
AZ uses hand for the Pokémon stack and discard for attachments.

A simulator that has only one destination field for the whole board object
cannot represent all three correctly.

### The board object ends

Damage, Special Conditions, evolution eligibility, and other in-play state
belong to the removed board object. Once the object leaves play, that object is
gone. A later play of one of those physical cards creates a new board object
under the existing materialization model.

### Active removal and Bench removal have different positional consequences

Removing a Benched Pokémon leaves the Active Pokémon unchanged.

Removing an Active Pokémon requires a legal promotion when another Pokémon
survives. If no Pokémon survives, the mechanical board becomes terminal
(`None`). Win/loss resolution remains a separate phase.

### Identity lifetime can be deferred

The default completed transition dematerializes off-board instances back into
exchangeable zone counts.

The optional `preserve_identity=True` mode keeps moved cards materialized in
their new ordinary zones. This supports an enclosing effect that still needs to
refer to a specific physical card before the engine decides it is safe to
compress that card back into an exchangeable class.

## Regression coverage

The deterministic regression validates:

- Scoop Up Cyclone style hand routing for a two-card evolution stack, Tool, and
  Special Energy;
- AZ style split routing between hand and discard;
- Cassius style deck routing;
- conservation of every represented card class;
- deferred dematerialization with board bindings cleared;
- Benched-Pokémon exit without promotion;
- Active-Pokémon exit with promotion;
- terminal removal of the final Pokémon;
- rejection of missing or invalid promotion choices;
- rejection of board-relation zones as exit destinations.

## Relationship to existing work

This result extends:

- `pokemon_stack_materialization/`, which materializes physical evolution
  stack members;
- `evolution_stack_binding/`, which preserves physical stack identity through
  evolution and devolution;
- `stack_knockout_conservation/`, which disposes complete stacks and
  attachments after Knock Out;
- `physical_state_conservation/`, which defines the shared conservation and
  identity-lifetime model.

The new seam covers voluntary or effect-driven zone exits outside ordinary
Knock Out disposal.

## Limits

The adapter receives already-resolved destinations. It does not parse card
text, flip coins, enforce Supporter or Item timing, evaluate target restrictions,
or resolve replacement-effect precedence.

It also applies one destination to all attachments. Per-instance attachment
redirection can be layered on later if a concrete effect requires mixed routing
during the same non-Knock-Out exit.

Opponent-owned targets and multi-Pokémon batch exits still need match-level
ownership and ordering semantics.

## Validation

Run:

`python results/stack_zone_exit_conservation/reproduce.py`

A dedicated GitHub Actions workflow validates the regression against the shared
repository.
