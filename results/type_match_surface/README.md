# Reachability of multiple matching Weakness/Resistance modifiers

## Question

The printed-type damage bridge conservatively rejects states where one attacking Pokemon simultaneously matches more than one printed Weakness or more than one printed Resistance. Does that unresolved case occur among current effectively legal printed type combinations?

No, in the current bundled English paper-Expanded snapshot.

Implementation: `tools/type_match_surface.py`  
Regression: `results/type_match_surface/reproduce.py`

## Current surface

Across 12,504 effectively legal Pokemon profiles:

- 21 distinct printed attacker type sets occur;
- 16 Pokemon prints have more than one printed type;
- 2 Pokemon prints have more than one Weakness entry;
- 0 Pokemon prints have more than one Resistance entry.

The probe cross-products every observed printed attacker type set with every target profile's typed Weakness and Resistance entries.

It finds:

- 0 cases where an observed attacker type set matches more than one Weakness entry on the same target;
- 0 cases where an observed attacker type set matches more than one Resistance entry on the same target.

## Consequence

The conservative multi-match rejection in `profile_damage_context.py` does not block any interaction reachable from current printed attacker type sets and current printed target modifiers.

This makes the unresolved historical multi-match composition rule low urgency for the present snapshot. The guard remains useful because live type-changing effects could create attacker type combinations that are absent from printed cards, and future cards may expand the surface.

## Interpretation

The result is a reachability statement over printed card identities, not a universal rules claim.

It does not prove that simultaneous modifier matches can never occur after Abilities, attacks, Tools, Stadiums, or other effects alter type or Weakness/Resistance. Those live-state transformations remain outside this static scan.
