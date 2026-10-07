# Explicit attack-use requirements in paper Expanded

## Question

How much match state is needed to decide whether an attack selected through a
copy effect can actually process?

A scan of the supplied legal paper Expanded card pool finds 44 print rows across
29 distinct attack-text signatures beginning with:

`You can use this attack only if ...`

Implementation:
- `tools/attack_use_requirement_catalog.py`

Regression:
- `results/attack_use_requirement_catalog/reproduce.py`

## Inventory

Every current signature is classified into a concrete dependency family:

| Dependency family | Signatures |
| --- | ---: |
| turn order + first-turn status | 10 |
| attack history | 7 |
| relative Prize advantage | 2 |
| Lost Zone count >= 10 | 2 |
| opponent exactly 1 Prize | 1 |
| opponent exactly 2 Prizes | 1 |
| Prize gap >= 3 | 1 |
| total remaining Prizes <= 6 | 1 |
| self has damage | 1 |
| opponent Active has a Special Condition | 1 |
| discard contains no Supporter | 1 |
| Bench contains Grass + Water + Lightning Pokemon | 1 |

All 29 signatures fit one of these audited families.

## Copy-engine consequence

The Slowking/Lost Mine official ruling shows that an attack-use requirement
cannot simply remove that attack from a copy effect's selectable target set.
Lost Mine can be selected while its requirement is false; its selected body
then performs no processing.

A general copied-body gate therefore needs access to more than Energy state.
The current card pool requires, at minimum:

- turn order and current-turn identity;
- per-player attack history;
- remaining Prize counts;
- Lost Zone counts;
- damage on the copying Pokemon;
- Special Conditions on the opponent's Active Pokemon;
- discard-pile card classes;
- typed Bench topology.

This is a concrete state-coverage checklist for future copy simulation.

## Examples

**Lost Mine** depends on the copying player's Lost Zone count. The supplied
database has one legal Lost Mine print, `swsh11-70`.

**Nightcap** depends on the opponent having exactly two Prize cards remaining.
It is one member of the broader requirement catalog as well as one of the six
copy attacks with an outer control.

**Follow-Up Kerzap** consists entirely of its requirement sentence. It depends
on whether the same Pokemon used Stun Needle during the player's previous turn.
The parser therefore accepts requirement-only attacks as well as requirements
followed by a second instruction sentence.

## Limits

This catalog covers the explicit `You can use this attack only if` wording.
Other attack-control forms exist, including `this attack does nothing` and
`you can't use this attack`. They should remain separate until their timing
and copied-body behavior are audited.

The dependency families identify which state channel is required. They do not
yet compile every condition into an executable predicate.
