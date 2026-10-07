# Ordered Knock Out redirection

## Question

Once multiple Knock Out effects assign different destinations to the same
physical card, what can the physical-state layer resolve after the legally
chosen effect order is already known?

Implementation: `tools/knockout_redirection_ordering.py`  
Regression: `results/knockout_redirection_ordering/reproduce.py`

## Official ruling basis

The Pokémon Asia Trainers Website has an official Q&A for Lost City and
Reuniclus's Persistent Cells Ability:

https://asia.pokemon-card.com/ph/rules/search/?keyword=Lost+City

Persistent Cells says that if Reuniclus is Knocked Out by damage from an
opponent's attack, put it into hand instead of the discard pile and discard all
attached cards. This has the same destination geometry as the repository's
`pokemon_to_hand_attached_discard` routing signature.

The official ruling says Reuniclus's owner chooses the order of Persistent Cells
and Lost City. If Persistent Cells resolves first, Reuniclus goes to hand. If
Lost City resolves first, it goes to the Lost Zone.

The same official search page separately confirms that when Reuniclus returns
to hand, its previous Evolutions Solosis and Duosion return with it.

This provides an authoritative order-sensitive destination example and also
confirms that the relevant physical object is the full evolution stack.

## Representation

`resolve_ordered_programs()` takes:

1. a set of partial per-effect destination programs;
2. an exact caller-supplied effect order.

It does not decide who may choose that order.

For each physical instance, the earliest effect in that order that explicitly
assigns a destination resolves that instance. A later destination assignment for
the same instance is ignored because the earlier effect has already moved the
card out of the pending Knock Out relation.

The resolver preserves provenance as
`ResolvedDestination(instance_id, destination_zone, effect_id)`, then
`resolved_route_map()` converts those rows to the existing conservation
router's destination map.

## Regression

The regression reuses the three-card
Honedge -> Doublade -> Aegislash physical stack from the executable-routing
result because Aegislash's Durable Blade has the same return-to-hand routing
signature as the official Reuniclus case.

With the return program first:

- Honedge, Doublade, and Aegislash all resolve to hand;
- all attachments resolve to discard;
- the surviving Bidoof is promoted;
- every card-class total is conserved.

With Lost City first:

- all three Pokémon cards resolve to the Lost Zone;
- all attachments resolve to discard;
- the same promotion and conservation invariants hold.

The test also rejects incomplete, duplicate, or unknown effect orders.

## Finding

Destination conflicts and order authority are separate modeling concerns.

The physical transition layer can be deterministic once a valid effect order is
supplied. The authority that selects that order belongs to the rules/card
semantic layer and can depend on the exact situation.

This matters because a repository abstraction that always assigns simultaneous
KO-effect ordering to the current-turn player is too broad. The official
Lost City + Persistent Cells ruling assigns the choice to the Knocked Out
Reuniclus's owner.

## Limits

The earliest-explicit-assignment rule here is validated against the official
Lost City + Persistent Cells destination case. It should not be treated as a
complete arbitrary-effect interpreter.

Effects may change conditions, create new objects, alter players, or have
non-destination consequences. Those need sequential semantic execution rather
than only destination-program reduction.

The model also leaves activation conditions, optional choices, and ordering
authority upstream.
