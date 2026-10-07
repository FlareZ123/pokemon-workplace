# Weakness and Resistance modifier surface

## Question

Does the current effectively legal paper-Expanded card pool use only multiplicative Weakness and subtractive Resistance?

Almost, but the bundled snapshot contains two literal exceptions.

Implementation: tools/type_modifier_catalog.py
Regression: results/type_modifier_catalog/reproduce.py

## Corpus result

Across effectively legal Pokemon prints in Expanded, the Weakness value fields are:

| Modifier | Entries |
| --- | ---: |
| x2 | 12,171 |
| +20 | 1 |

The Resistance value fields are:

| Modifier | Entries |
| --- | ---: |
| -20 | 1,769 |
| -30 | 1,515 |
| x2 | 1 |

The two exceptional records are:

- Uxie me55c-43, Psychic Weakness +20;
- Murkrow me55-93, Fighting Resistance x2.

The parser deliberately accepts multiplication, addition, and subtraction notation rather than silently coercing every Weakness to a multiplier and every Resistance to a subtraction.

## Representation consequence

The first damage-calculation kernel uses a multiplicative Weakness input and subtractive Resistance input. That is a conservative subset, not a complete representation of every literal modifier present in the card database.

The Uxie record gives a concrete reason to support an additive Weakness stage if a future executor wants full corpus coverage.

The Murkrow Resistance record is mechanically unusual enough that it should be verified before a simulator assigns semantics beyond the literal database field. Treating all Resistance as a negative integer would erase the anomaly and make it impossible to notice.

## Method

The catalog uses the repository's effective-legality policy, scans all legal Pokemon in Expanded-legal sets, parses every Weakness and Resistance value, and raises on any notation outside multiplication, addition, or subtraction.

This provides a regression tripwire for future card-data changes.

## Limits

This result inventories literal card-data fields. It does not independently verify the printed image or external errata for the two exceptional records.

It also does not model effects that remove Weakness or Resistance, alter them while in play, or cause attacks to ignore those calculation stages. Those remain state/effect layers above the printed combat profile.
