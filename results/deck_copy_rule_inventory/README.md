# Complete snapshot audit of printed copy-count rules

## Finding

An all-sets audit of the bundled English card corpus found **179** prints
bearing seven classes of card-text deck-copy restrictions or permissions.

| Rule class | Print records |
|---|---:|
| ACE SPEC deck-wide singleton | 53 |
| Pokémon Star deck-wide singleton | 29 |
| Prism Star name-based singleton | 27 |
| Unown Basic-Pokémon family-wide four-copy limit | 26 |
| Radiant Pokémon deck-wide singleton | 16 |
| Arceus exact-print unrestricted-copy exception | 15 |
| Named-card singleton, including Shining and Miracle Energy | 13 |
| **Total** | **179** |

The audit matches narrow rule phrases appearing in the snapshot. It
returns the exact IDs and flags any unrecognized copy-rule wording.

## Newly detected semantic gap

Historical Miracle Energy (neo4-16) starts its rules field with the
sentence "You can't have more than 1 Miracle Energy in your deck."
followed by its attachment and Energy-provision instructions in the
**same string**.

Earlier validator logic expected the singleton sentence to equal the
entire rules field. It therefore allowed two Miracle Energy copies
with only an unrecognized-rule warning.

The revised validator recognizes a complete leading singleton
sentence followed by a space and more card text. The historical
two-copy construction now yields self_named_singleton_limit;
one copy is still permitted. The warning is eliminated because the
printed condition is recognized.

This audit extends historical_deck_rules and validates old sets
without equating historical printed semantics to current paper
Expanded tournament eligibility.

## Reproduction

Run python -m results.deck_copy_rule_inventory.reproduce.

The test checks the seven counts, absence of unknown copy-rule
phrases, exact representative card identities, and Miracle Energy
construction regression. The older in-scope-only audit of 97
effectively legal print restrictions remains useful but does not
cover the pre-Black & White historical rule surface.

## Boundaries

Detection here is limited to rules mentioning the deck and a
copy-count phrase. Future wording may require widening the audit.
The explicit rules apply to physical exact prints under historical
construction analysis. Reprint eligibility continues to be
computed separately.
