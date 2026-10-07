# Physical state conservation synthesis

## Purpose

Several independent results now point to one shared state-modeling principle:

> A simulator should conserve physical card copies separately from the temporary
> relations those cards have to zones, Pokémon objects, and one another.

This synthesis collects the repository's identity, multiplicity, attachment,
evolution, movement, and Knock Out work into one model.

## Identity hierarchy

The current work needs four distinct identities.

1. **Print identity** (`print_id`): one database printing.
2. **Exchangeable card class** (`card_class`): the equivalence relation chosen
   for a particular count ledger.
3. **Physical card instance** (`instance_id`): one concrete copy after history
   or topology makes it non-exchangeable.
4. **Pokémon board object** (`pokemon_id` / `object_id`): one persistent
   in-play Pokémon object that can own an evolution stack and attachments.

Two physical cards can share a print ID. One Pokémon object can contain several
physical Pokémon-card instances in its evolution stack. Energy and Tool
instances attach to that object without becoming stack members.

Supporting results include
[card_identity_resolution/](../card_identity_resolution/),
[card_class_namespace/](../card_class_namespace/),
[multicopy_zone_state/](../multicopy_zone_state/), and
[pokemon_stack_materialization/](../pokemon_stack_materialization/).

## Conservation invariant

For each represented `card_class`:

`total copies = exchangeable zone counts + materialized physical instances`.

Every deterministic mechanics transition in this thread preserves that total.

The invariant is independent of where copies are. A card can move through hand,
deck, Prize cards, discard, Lost Zone, an in-play stack, or an attachment
relation while its physical-copy total remains constant.

A board can be locally valid while the same physical card is still counted in
hand. Likewise, a zone ledger can have the right total while an attachment has
no matching physical instance. The identity ledger therefore acts as the
conservation boundary between aggregate multiplicity and materialized topology.

## Materialization lifetime

A useful compression rule is:

- keep per-zone multiplicity while copies are exchangeable;
- materialize an `instance_id` when attachment topology, evolution history, or
  card-specific history distinguishes one copy;
- preserve that instance while the distinguishing relation matters;
- dematerialize when the relation/history ends and the card can safely rejoin an
  exchangeable zone count.

Examples:

- attaching Double Colorless Energy materializes one physical Energy copy;
- playing Bulbasaur materializes a Pokémon card bound to a persistent Pokémon
  object;
- evolving with Ivysaur adds another physical card to that same stack;
- moving an attached Energy to another Pokémon preserves the same instance;
- ordinary Knock Out disposal destroys board relations, so removed cards can
  usually dematerialize into their resolved zones.

Supporting results:
[energy_board_conservation/](../energy_board_conservation/),
[pokemon_stack_materialization/](../pokemon_stack_materialization/),
[devolution_materialization/](../devolution_materialization/),
[energy_movement_conservation/](../energy_movement_conservation/),
[stack_knockout_conservation/](../stack_knockout_conservation/), and
[stack_zone_exit_conservation/](../stack_zone_exit_conservation/).

## Physical transition classes

### Exchangeable zone move

No instance identity is needed when card-specific history is irrelevant.

### Materialization

One exchangeable count becomes one physical instance and acquires a board
relation, such as `hand -> attached` or `hand -> in_play`.

### Relation-preserving topology change

The instance remains materialized while its holder changes. Physical Energy
movement is the current example.

### Object-preserving stack change

The Pokémon board object persists while evolution appends a physical card or
devolution removes one.

### Object-ending ordinary zone exit

A hand or deck return ends the board object and moves every physical Pokémon
card in its evolution stack to the Pokémon's resolved destination. Attached
cards leave their attachment relations at the same boundary, although card text
can route them to a different ordinary zone.

[stack_zone_exit_conservation/](../stack_zone_exit_conservation/) validates
Scoop Up Cyclone style hand routing, Cassius style deck routing, and AZ style
split routing. It can also keep off-board instances materialized until an
enclosing effect no longer needs exact identity.

### Relation destruction with zone routing

A board relation ends and the removed physical instance enters a resolved
ordinary zone. Knock Out usually sends cards to discard, but the destination can
be changed by effects.

### Batch transition with a trigger window

Several physical relations can end simultaneously. The engine should first keep
a pre-discard snapshot for Knock Out triggers, then dispose the complete known
batch.

### Ordered decision after a simultaneous event

The physical event can be simultaneous while downstream choices are sequential.
When both Active Pokémon are Knocked Out, the player whose turn would be next
promotes first.

## Sequential Knock Out deletion is unsafe

[simultaneous_knockout_conservation/](../simultaneous_knockout_conservation/)
contains a concrete counterexample.

Suppose Active A and Benched B are Knocked Out at the same time while Benched C
survives. A sequential engine can incorrectly delete A, temporarily promote B,
then delete B and promote C.

That intermediate B promotion is illegal. B belongs to the same Knock Out batch.

The pending-batch representation instead:

1. identifies the complete KO set;
2. keeps those objects present for Knock Out-trigger effects;
3. disposes the complete batch;
4. derives promotion candidates only from survivors.

## Destination choice is separate from conservation

[knockout_zone_routing/](../knockout_zone_routing/) separates two questions:

1. Which physical copies are leaving board relations?
2. Which zone does each copy enter after effects resolve?

Expanded-legal Huntail `sv10-55` supplies a concrete counterexample to fixed
KO-to-discard semantics. Diver's Catch can route Basic Water Energy attached to
a qualifying Knocked Out Water Pokémon to hand instead. Other cards on that same
Pokémon can still follow ordinary discard disposal.

The conservation layer preserves copy totals. Card/effect semantics choose
destinations.

## Attachment legality can interrupt movement

[special_energy_move_conservation/](../special_energy_move_conservation/) shows
the same separation during Energy movement.

Expanded-legal Double Dragon Energy `xy6-97` can remain attached only to Dragon
Pokémon. When an effect moves it toward an incompatible Pokémon, the source
relation ends but the destination relation cannot form, so the physical card is
discarded instead.

The physical sequence is:

`source relation ends -> destination legality resolves -> new relation OR zone exit`.

## Promotion order is an information boundary

[cross_player_knockout_resolution/](../cross_player_knockout_resolution/)
extends the batch model across both players.

When both players need to promote after simultaneous Active Knock Outs, the
player whose turn would be next chooses first. The decision protocol is:

`next player chooses -> other player observes -> other player chooses`.

An unordered pair of promotions loses that information dependency even if the
final positions happen to match.

## Architectural consequence

A larger simulator should avoid giving several subsystems competing ownership of
the same physical facts.

A practical authority split is:

- **zone-count ledger:** exchangeable multiplicity;
- **identity ledger:** physical instances and relation type;
- **board objects:** Pokémon position, stack topology, attachments, damage, and
  temporary state;
- **typed effect semantics:** eligibility, restrictions, destinations, timing;
- **belief state:** uncertainty over hidden physical configurations;
- **action-budget state:** once-per-turn and other temporal resources.

Specialized solvers can read these authorities, but should not keep independent
copies that can drift out of synchronization.

## Remaining integration gaps

1. **Competing replacement/redirection effects.** Per-instance destination
   routing exists, but precedence among several applicable effects needs an
   explicit model.
2. **Canonical match-level phase composition.** Physical Knock Out disposal,
   Prize-pending information, promotion-pending state, and post-Knock-Out game
   resolution now have concrete adapters, while one shared match authority still
   needs to compose those phase boundaries consistently.
3. **Cross-player unified state.** Promotion order is currently a protocol over
   two player states rather than one canonical match object.
4. **Identity lifetime after recovery.** Zone-exit conservation can defer
   dematerialization, but a general policy still needs to decide when an
   enclosing effect has finished referring to an exact moved card and identity
   can safely collapse back into exchangeable counts.
5. **Board-kernel convergence.** `board_object_kernel.py` and the richer
   `board_position_state.py` / `board_position_kernel.py` still overlap.
   `attack_copy_physical_ko_bridge` now shows that copied attack damage and
   effect counters can run directly on the stack-bearing representation and
   feed a pending simultaneous-KO batch without a board conversion, but other
   specialized kernels still use the lightweight board.
6. **Card-text compilation.** Conservation consumes resolved semantics. A
   conservative compiler still needs to choose the correct transition family
   and constraints from card text.

## Traceability

Core detailed results:

- [multicopy_zone_state/](../multicopy_zone_state/)
- [energy_board_conservation/](../energy_board_conservation/)
- [materialization_board_binding/](../materialization_board_binding/)
- [pokemon_stack_materialization/](../pokemon_stack_materialization/)
- [devolution_materialization/](../devolution_materialization/)
- [board_attachment_conservation/](../board_attachment_conservation/)
- [energy_movement_conservation/](../energy_movement_conservation/)
- [special_energy_move_conservation/](../special_energy_move_conservation/)
- [stack_knockout_conservation/](../stack_knockout_conservation/)
- [stack_zone_exit_conservation/](../stack_zone_exit_conservation/)
- [simultaneous_knockout_conservation/](../simultaneous_knockout_conservation/)
- [knockout_zone_routing/](../knockout_zone_routing/)
- [cross_player_knockout_resolution/](../cross_player_knockout_resolution/)
- [attack_copy_physical_ko_bridge/](../attack_copy_physical_ko_bridge/)

This synthesis should be revised when any supporting mechanic is falsified or
superseded.
