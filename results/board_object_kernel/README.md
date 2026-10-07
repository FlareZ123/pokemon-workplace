# Per-Pokémon board-object state

## Question

What state representation is needed when a Pokémon moves between the Active Spot and Bench while attached cards, damage, and other persistent state remain on that same Pokémon?

This result adds a deterministic board-object kernel for the part of the game where position changes while the Pokémon object persists.

Implementation: `tools/board_object_kernel.py`  
Regression: `results/board_object_kernel/reproduce.py`

## Rule-derived state semantics

The Advanced Player's Rulebook establishes several distinctions that a state engine must preserve.

For normal retreat:

- the Active Pokémon moves to the Bench and another Benched Pokémon becomes Active;
- retreat is normally limited to once per turn;
- enough attached Energy must be discarded to pay Retreat Cost;
- remaining Energy, attached Tools or Items, and damage counters stay with the Pokémon as it moves;
- Asleep, Paralyzed, and explicit retreat-denial effects can prevent the normal retreat action;
- moving the outgoing Active to the Bench removes its Special Conditions and attack-applied temporary effects.

For effect-based switching:

- the Active and a Benched Pokémon exchange positions;
- switching does not pay Retreat Cost;
- a Pokémon that cannot retreat can still be switched by an effect;
- the outgoing Active loses Special Conditions and effects such as a temporary attack prohibition.

For evolution:

- attached cards and damage counters remain;
- temporary attack effects and Special Conditions on an Active Pokémon clear when it evolves.

These mechanics imply that Active and Bench position should be a property of a persistent Pokémon object rather than the only representation of that object.

## Representation

`BoardPokemon` carries one in-play Pokémon object's persistent state:

- unique object identity;
- current top-card name and tags;
- physical Energy attachments, each with a board-level instance ID and optional database print ID;
- physical Tool attachment with the same identity separation;
- typed temporary attack and retreat locks from the existing lock kernel;
- damage counters;
- Special Conditions;
- a scalar retention value used only by the existing Bench-contraction model.

`BoardState` carries:

- the Active object's ID;
- ordered Bench object IDs;
- all in-play Pokémon objects;
- current Bench capacity;
- whether the normal retreat action has already been used this turn.

The validator requires Pokémon object IDs to be unique, requires every in-play object to occupy exactly one Active or Bench position, and requires every attached physical **instance ID** to be unique across the board. Database print IDs are allowed to repeat because a deck may contain several physical copies of one print.

## Finding 1: retreat and switching are different transitions

A temporary `can't retreat` state removes the normal retreat transition.

The same outgoing Active can still move to the Bench through `switch_active()`.

The regression begins with an Active Pokémon carrying:

- two Energy cards;
- Stealthy Hood;
- three damage counters;
- Poisoned;
- temporary attack lock;
- temporary retreat lock.

Normal retreat fails.

Effect-based switching succeeds. After switching:

- both Energy cards remain with the moved Pokémon;
- Stealthy Hood remains attached;
- all three damage counters remain;
- the temporary attack and retreat locks are cleared;
- Poisoned is cleared.

A planner that represents movement as one generic `Active -> Bench` edge cannot express this distinction correctly.

## Finding 2: Retreat Cost is paid by physical Energy cards

The kernel models attached Energy as physical cards with one or more supplied Energy units.

For an Active with:

- one Double Colorless Energy supplying two Colorless units;
- one Lightning Energy;
- one Fire Energy;

a Retreat Cost of one has three minimal physical payments:

- Double Colorless Energy alone;
- Lightning Energy alone;
- Fire Energy alone.

A Retreat Cost of two has two minimal payments:

- Double Colorless Energy alone;
- Lightning Energy plus Fire Energy.

This preserves the difference between Energy units and Energy cards. Paying with the multi-unit Special Energy discards that whole physical card.

The regression also rejects gratuitous additional Energy cards once a proper subset already satisfies the represented cost.

## Finding 3: the once-per-turn retreat budget follows the turn, not the Active identity

After one successful normal retreat, later effect-based switching can change the Active Pokémon again.

The normal retreat action remains spent for that turn.

After `next_turn()`, the retreat budget resets and another legal retreat can occur.

This prevents a position change from accidentally restoring a global once-per-turn action resource.

## Finding 4: Special Conditions can distinguish retreat from switching

An Asleep Active cannot use the modeled normal retreat action.

The same board can still resolve an effect-based switch.

This gives another concrete reason that a simulator should keep movement mechanism and Pokémon position separate.

## Finding 5: evolution mutates the same board object

`evolve()` changes the object's current top-card name and optional tags while preserving:

- attached Energy;
- attached Tool;
- damage counters;
- object identity.

It clears Special Conditions and the modeled temporary attack/retreat effects.

The object therefore remains the same strategic board resource while its current card identity changes.

## Finding 6: Bench contraction removes complete board objects

The existing maximum-retention Bench-capacity resolver is applied to Benched Pokémon objects.

When capacity contracts, the kernel removes the complete losing object rather than only decrementing a Bench count.

If that Pokémon carries Energy, a Tool, or damage, those states leave play with it.

The Active object is not part of the contraction choice.

This is the board-object counterpart to the unified-state result's requirement that capacity transitions synchronize with physical state.

## Finding 7: physical instance identity is distinct from print identity

The repository's card-identity layer uses `card_id` for a database print identity. A board state needs a different key for a physical copy.

The attachment records therefore use:

- `instance_id`: unique for the physical copy represented on this board;
- `print_id`: optional database print identity, which may be shared by several physical copies;
- `card_name`: human-readable/card-rule identity used by this scaffold.

The regression places two Double Colorless Energy cards with the same `print_id` on one Pokémon while giving them different `instance_id` values. The board validates successfully.

This distinction prevents an exact-print identifier from being accidentally treated as a unique physical-card identifier.

## Relationship to the unified state kernel

`results/unified_state_kernel/` established one authoritative mechanical state across card zones, Bench capacity, locks, Energy readiness, and Prize belief.

The board-object kernel addresses one boundary that the first prototype deliberately left abstract: state that belongs to a specific in-play Pokémon.

A larger engine can compose them by keeping:

1. per-zone multiplicities for exchangeable copies outside board topology;
2. physical instance IDs for materialized attachments and board-object identity for Pokémon in play;
3. typed transition permissions and action budgets;
4. specialized resource solvers such as the Energy kernel;
5. probabilistic beliefs over hidden physical states.

The critical requirement is that these layers share identities instead of maintaining contradictory copies of the same physical card or Pokémon.

## Validation

The deterministic reproducer checks:

- retreat denial from a temporary retreat lock;
- legal switching through that same retreat lock;
- preservation of Energy, Tool, and damage through switching;
- clearing of temporary effects and Special Conditions on the outgoing Active;
- minimal physical Energy-card payments for Retreat Costs one and two;
- a multi-unit Energy card paying a multi-unit Retreat Cost by itself;
- discard of the whole selected Energy card;
- persistence of the once-per-turn retreat budget through switching;
- reset of that budget on the next turn;
- Asleep blocking normal retreat while switching remains legal;
- evolution preserving attachments and damage while clearing temporary state;
- Bench contraction removing a complete low-retention Pokémon object;
- two physical Energy instances sharing one database print ID without identity collision.

## Limits

The kernel does not yet model attack execution, HP totals and Knock Outs, evolution stacks, retreat-cost modifiers, Energy-type-specific discard requirements, Special Energy attachment restrictions, Tool effects beyond their persistent identity, or opponent board state.

The Retreat Cost helper currently represents payment in generic Energy units. Effects that alter how a particular Energy card counts for a particular payment need an explicit payment profile.

The contraction helper uses a local scalar retention objective inherited from the existing Bench-capacity model. It is a mechanics scaffold rather than a claim that this scalar is a complete strategic value function.

The board stores one top-card name rather than a full evolution stack. Devolution therefore needs a richer persistent object representation.

## Next useful work

The new [../multicopy_zone_state/](../multicopy_zone_state/) result supplies the missing exchangeable-copy layer outside board topology. It keeps repeated copies as per-zone counts and materializes identity only when copies become mechanically distinguishable.

The next useful integration is therefore a conservation adapter between the two layers:

- decrement an exchangeable zone count when a card becomes a specific attachment or board object;
- allocate a unique physical `instance_id` at that materialization boundary;
- return the card to the correct zone count when it leaves the materialized board relation;
- preserve print/gameplay-class metadata separately from physical instance identity.

That adapter would let the unified state compose multiplicity and board topology without maintaining two contradictory authorities for the same card.
