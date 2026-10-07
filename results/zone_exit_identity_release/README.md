# Releasing preserved zone-exit identity

## Question

The stack zone-exit transition can deliberately keep returned Pokémon cards and
attachments materialized with preserve_identity=True. What ends that temporary
exact-identity lifetime?

This result composes the zone-exit transition with the identity-liveness gate.

Implementation: tools/zone_exit_identity_release.py
Regression: results/zone_exit_identity_release/reproduce.py

## Atomic release rule

release_zone_exit_identity_group first evaluates every preserved instance
against the liveness policy.

If any requested instance still has a blocker, the whole release is rejected
before the ledger changes. When every instance is safe, all requested instances
collapse back into exchangeable counts and card-class totals are rechecked.

Atomicity matters for callers that treat one preserved stack-and-attachments
batch as the output of a single enclosing effect. A failed release should not
silently erase some exact identities while leaving others live.

## Concrete regression

The witness starts with an Ivysaur object carrying a physical Bulbasaur ->
Ivysaur stack and a Muscle Band, plus a Benched Bidoof.

A Scoop Up Cyclone-style transition returns the complete stack and attachment to
hand with preserve_identity=True. The three exact returned IDs are:

- bulba-copy
- ivy-copy
- band-copy

An enclosing-effect reference then names ivy-copy. Group release is rejected
and every returned instance stays materialized.

After that reference is removed, the same group releases successfully:

- the three returned cards become exchangeable hand counts;
- Bidoof remains the only materialized in-play card;
- physical hand size stays 3;
- every card-class total remains conserved.

## Finding

The preserve_identity option now has a concrete completion path.

A useful lifecycle for ordinary zone exits is:

1. destroy board relations and move exact instances to resolved zones;
2. preserve those identities while the enclosing semantic layer still names
   them;
3. end the semantic references;
4. atomically collapse the group through the liveness gate.

This separates physical movement from representation cleanup and avoids guessing
at the moment of zone movement whether some later clause still needs exact
identity.

## Limits

The result handles one caller-supplied identity group. A future match-level
owner still needs to gather reference claims automatically from pending effects,
belief state, deck topology, Prize topology, and other exact-state subsystems.

Some effects may intentionally preserve identity beyond the current effect
because later game history distinguishes the card. Those histories should
appear as additional liveness references rather than special cases in the zone
exit transition.
