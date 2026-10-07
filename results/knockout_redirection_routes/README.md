# Executable Knock Out redirection routes

## Question

Can the four zone-redirection signatures currently recognized by
`tools/knockout_redirection_taxonomy.py` be translated into physical-card
destinations without duplicating the existing conservation and pending-KO
machinery?

Implementation: `tools/knockout_redirection_routes.py`  
Regression: `results/knockout_redirection_routes/reproduce.py`

## Result

Yes. The new translator emits only per-instance destination overrides for the
existing `discard_pending_with_zone_routes()` disposal transition. The
conservation kernel still owns physical identity, board detachment,
dematerialization, promotion legality, and copy-count invariants.

The four current signatures compile as follows:

| Routing signature | Pokémon stack | Attachments |
| --- | --- | --- |
| `pokemon_to_hand_attached_discard` | hand | discard |
| `pokemon_and_attached_to_lost_zone` | Lost Zone | Lost Zone |
| `pokemon_to_lost_zone_attached_discard` | Lost Zone | discard |
| `attached_energy_to_hand_default_discard` | discard | selected Energy to hand; other attachments discard |

Instances omitted from the override map use the router's normal discard
destination.

## Concrete card basis

The regression corresponds to the four exemplars used by the text taxonomy:

- `sm11-95` Aegislash, Durable Blade: the Knocked Out Pokémon returns to hand
  and attached cards are discarded.
- `sm8-121` Tyranitar-GX, Lost Out: the Knocked Out Pokémon and all attached
  cards go to the Lost Zone.
- `swsh11-161` Lost City: the Knocked Out Pokémon goes to the Lost Zone while
  attached cards are discarded.
- `sv10-55` Huntail, Diver's Catch: qualifying attached Basic Water Energy can
  go to hand instead of the discard pile.

The Advanced Player's Rulebook states that when an evolved Pokémon in play is
put into its player's hand or deck, its previous Evolutions go with it. The
translator therefore routes every physical Pokémon card in the evolution stack,
not only the top Stage card, for the hand-return signature.

## Regression geometry

One immutable pending KO state contains an evolved three-card
Honedge -> Doublade -> Aegislash stack with:

- two Basic Water Energy;
- one Double Colorless Energy;
- one Muscle Band;
- one surviving Benched Bidoof.

The same state is disposed four ways. Assertions verify the exact destination
of every card class, preservation of the surviving Bidoof instance, legal
promotion, and full copy-total conservation.

This exposes a useful representation boundary: a routing signature describes
which physical relations change destination, while the identity ledger and KO
disposal transition enforce conservation.

## Semantic boundary

The signature translator intentionally does not decide card-specific
eligibility predicates. For Huntail, the caller supplies the physical Energy
instances already identified as Basic Water Energy. The translator verifies
that selected IDs are Energy attachments on the Knocked Out Pokémon, then
routes them to hand.

That keeps text/card semantics separate from physical movement. A future
compiler can resolve predicates such as Basic Water, owner, damage-source, or
optional-effect activation before calling this layer.

## Finding

Knock Out redirection is naturally represented as a small destination program
over a pending physical KO batch.

This avoids separate hard-coded disposal implementations for Aegislash,
Tyranitar-GX, Lost City, Huntail, and future cards with the same routing
geometry. It also preserves lower Evolution cards correctly when a Pokémon
stack changes zones.

## Limits

The current signature set comes from the repository's literal text taxonomy and
is not claimed to cover every semantically equivalent historical wording.

Competing replacement effects, ordering between multiple simultaneous
redirections, ownership-sensitive destinations, direct transitions into new
board relations, and automatic derivation of card-specific eligibility
predicates remain open.
