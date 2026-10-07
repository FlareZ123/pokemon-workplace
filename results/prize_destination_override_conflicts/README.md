# Competing destination overrides for taken Prize cards

## Question

Can the physical Prize-taking kernel safely compose replacement effects that redirect the same already-taken Prize card to different zones?

Only when the applicable replacement effects agree on the destination. When they disagree, the mechanical layer needs an explicit unresolved conflict instead of silently choosing one zone.

Implementation: `tools/prize_destination_overrides.py`  
Regression: `results/prize_destination_override_conflicts/reproduce.py`

## Concrete Expanded witness

The bundled legal card pool contains two effects that can apply to the same Prize award:

- Barbaracle `swsh11-107`, **Lost Block**: the opponent puts Prize cards they would take in the Lost Zone instead of into their hand.
- Billowing Smoke `swsh3-158`: when the attached Pokémon is Knocked Out by damage from an opponent's attack, that player discards Prize cards they would take for that Knock Out instead of putting them into their hand.

If the Billowing Smoke holder is Knocked Out while its controller has Lost Block active, the attacking opponent can have two explicit destination replacements applying to each Prize from that Knock Out: `lost_zone` and `discard`.

The existing Prize-effect catalog already recognizes these separately as `taken_prize_to_lost_zone` and `taken_prize_to_discard`. The new layer composes them against one exact `prize_pending` physical instance.

## State boundary

The Advanced Player's Rulebook places Prize taking inside the Knock Out process after Knock Out effects and physical disposal. The existing `prize_pending_take` kernel represents a selected Prize as already removed from the Prize zone and held in `prize_pending` before its final destination is resolved.

The new resolver therefore treats `hand` as the ordinary destination only when no replacement applies. It does not model ordinary hand entry as another competing replacement once an explicit override exists.

This distinction matters because the Prize has already been taken mechanically even when its final card destination becomes Lost Zone or discard.

## Resolution contract

`decide_prize_destination(...)` has three outcomes:

1. no applicable override: use the ordinary `hand` destination;
2. one or more applicable overrides that all name the same zone: resolve to that zone;
3. applicable overrides that name different zones: return an unresolved conflict and do not mutate physical state.

Applicability and ordering authority remain upstream semantic questions. The resolver intentionally does not infer a priority rule from the word `instead`.

## Regression

The regression checks one exact physical Prize instance through the existing conservation kernel:

- ordinary Prize taking moves `prize_pending -> hand`;
- Lost Block alone moves `prize_pending -> lost_zone`;
- Billowing Smoke alone moves `prize_pending -> discard`;
- multiple same-destination overrides compose safely;
- Lost Block plus Billowing Smoke reports the conflicting zones `discard` and `lost_zone` and leaves the exact Prize instance in `prize_pending`;
- every resolved branch preserves physical card-class totals.

## Rules-source limitation

A targeted scan of the bundled Advanced Player's Rulebook found several effect-specific `instead` rules and special conflict rules for particular mechanics, but did not identify a general rule assigning precedence between two card effects that replace the same destination with different zones.

That absence is not evidence that no authoritative ruling exists. The result therefore establishes the state representation and conflict detector while leaving this exact paper-rules outcome unresolved pending stronger authority.

## Architectural implication

Destination replacement should be a first-class transition stage between an event and physical movement. A simulator needs to distinguish the underlying event, the ordinary destination, applicable replacement programs, ordering or precedence authority, and the final conserved move. Collapsing those into one zone assignment can hide real conflicts or bake an unsupported ruling into state execution.
