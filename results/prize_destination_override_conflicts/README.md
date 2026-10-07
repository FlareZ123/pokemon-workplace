# Competing destination overrides for taken Prize cards

## Question

Can the physical Prize-taking kernel compose replacement effects that redirect the same already-taken Prize card to different zones?

Yes, provided replacement applicability and chooser authority remain explicit. The bundled card pool gives a direct conflict, and an official Japanese Pokémon Card Q&A supplies the missing ordering rule for that exact pair.

Implementation: `tools/prize_destination_overrides.py`  
Regression: `results/prize_destination_override_conflicts/reproduce.py`

## Concrete Expanded witness

The bundled legal card pool contains two effects that can apply to the same Prize award:

- Barbaracle `swsh11-107`, **Lost Block**: the opponent puts Prize cards they would take in the Lost Zone instead of into their hand.
- Billowing Smoke `swsh3-158`: when the attached Pokémon is Knocked Out by damage from an opponent's attack, that player discards Prize cards they would take for that Knock Out instead of putting them into their hand.

The existing Prize-effect catalog recognizes these separately as `taken_prize_to_lost_zone` and `taken_prize_to_discard`.

## Authoritative ordering result

The Japanese Pokémon Card Trainers Website has an exact Q&A for Lost Block plus Billowing Smoke. It says the opponent taking the Prize chooses the effect order. If Lost Block is processed first, the Prize goes to the Lost Zone. If Billowing Smoke is processed first, the Prize is discarded.

A second official Q&A covers a two-Prize Pokémon V Knock Out and says the Prize-taking opponent looks at the two Prize cards and chooses, for each card individually, whether to put it in the Lost Zone or discard it.

Sources:

- https://www.pokemon-card.com/rules/faq/search.php?freeword=%E3%83%AF%E3%82%B6%E3%81%AE%E5%8A%B9%E6%9E%9C&page=52&regulation=all&regulation_header_search_item1=all
- https://www.pokemon-card.com/rules/faq/search.php?freeword=%E3%83%9D%E3%82%B1%E3%83%A2%E3%83%B3%E3%81%AE%E3%81%A9%E3%81%86%E3%81%90+%E3%83%88%E3%83%A9%E3%83%83%E3%82%B7%E3%83%A5+%E3%83%80%E3%83%A1%E3%83%BC%E3%82%B8+&page=3&regulation=all&regulation_faq_main_item1=all

## State boundary

The Advanced Player's Rulebook places Prize taking inside Knock Out resolution. The existing `prize_pending_take` kernel represents a selected Prize as already removed from the Prize zone and held in `prize_pending` before its final destination resolves.

The new layer treats `hand` as the ordinary destination when no replacement applies. If every applicable replacement names one zone, that zone is deterministic. If replacements name different zones, the state exposes a choice and waits for an upstream authority-aware caller to identify the chosen effect.

## Per-card decision granularity

The two-Prize official ruling matters architecturally. One global ordering choice for the entire Prize award would be too coarse.

The regression stages two exact physical Prize instances. It chooses Billowing Smoke for the first pending card and Lost Block for the second. The first moves to discard, the second moves to Lost Zone, and total physical card counts remain conserved.

This means the chooser decision belongs at the exact pending-card boundary after Prize identities can be observed.

## Regression

The regression checks:

- ordinary Prize taking: `prize_pending -> hand`;
- Lost Block alone: `prize_pending -> lost_zone`;
- Billowing Smoke alone: `prize_pending -> discard`;
- same-destination replacement effects compose directly;
- conflicting destinations remain pending until a legal effect choice is supplied;
- either official single-Prize branch can then execute;
- a two-Prize award can split destinations per exact card;
- all resolved branches preserve physical card-class totals.

## Correction history

The first implementation intentionally left the Lost Block plus Billowing Smoke conflict unresolved because a scan of the bundled Advanced Player's Rulebook did not expose a general replacement-precedence rule.

A later targeted search of the official Japanese Q&A found the exact interaction and falsified that provisional conclusion. The implementation was then changed from an unresolved-conflict terminal state to an explicit choice point.

This is a useful methodological example: absence from a general rulebook does not imply that a card-specific authoritative ruling is unavailable.

## Architectural implication

Destination replacement is a transition stage between an underlying event and physical movement. The event, ordinary destination, applicable replacements, chooser authority, per-card choice, and final conserved move are distinct state variables.

For this exact interaction, the prize-taking player owns the choice. That should remain evidence-backed metadata on the interaction instead of being generalized to every replacement conflict without further rules support.
