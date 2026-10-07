# Knock Out effect topology witnesses

## Question

Should all effects associated with a Knock Out be sent through the same ordering
and zone-routing layer?

Official rulings give strong evidence that they should remain separated by what
the effect actually does.

## Four ruling witnesses

### Team Plasma Weezing plus Lost City

Team Plasma Weezing's Aftermath discards the top 3 cards of the opponent's deck
when Weezing is Knocked Out by attack damage.

Lost City sends a Knocked Out Pokemon to the Lost Zone instead of the discard
pile.

The official Japanese FAQ says Aftermath is processed first and Weezing is put
in the Lost Zone afterward, regardless of the coin result in the Japanese card's
effect wording.

### Team Plasma Weezing plus Rescue Scarf

Rescue Scarf returns the attached Pokemon to the hand when it is Knocked Out by
attack damage.

The official FAQ says Aftermath mills the opponent's deck first, then Rescue
Scarf returns Weezing to the hand.

FAQ ID 8897:
https://www.pokemon-card.com/rules/faq/details.php?id=8897

### Team Plasma Weezing plus Reversal Trigger

Reversal Trigger searches the deck for any card when its attached Team Plasma
Pokemon is Knocked Out by attack damage.

The official FAQ says Weezing's owner chooses whether to resolve Aftermath or
Reversal Trigger first.

### Reuniclus plus Lost City

Reuniclus's Persistent Cells sends Reuniclus to the hand instead of the discard
pile. Lost City instead sends it to the Lost Zone.

The official FAQ says Reuniclus's owner chooses which effect resolves first.
The first destination effect to move Reuniclus determines whether it reaches the
hand or Lost Zone.

## Representation consequence

These witnesses support three distinct modeling responsibilities.

A non-destination KO effect can perform work such as milling or searching.
A destination effect assigns where a physical Pokemon instance goes instead of
ordinary discard. Ordering rules decide which eligible effect is processed
first when the outcome can vary.

The current repository already has a physical destination-program layer in the
KO redirection work. These rulings are evidence for keeping non-destination
effects outside that layer.

For the witnessed Weezing cases, the destination-moving effects occur only
after Aftermath has done its non-destination work. For Reversal Trigger, both
effects do non-destination work and the owner can choose their order. For
Reuniclus plus Lost City, both effects compete over the same physical
destination and the owner can choose their order.

## Important limit

The four rulings do not prove a universal type-level precedence rule such as
"every non-destination effect always precedes every destination effect."

They establish concrete topologies that a simulator must reproduce. Broader
precedence should come from a current general rule or additional rulings.

This is especially important after the 2025 ordering-rule migration. A legacy
card-specific ruling can remain useful when its exact topology is outside the
changed generic scope, while a ruling that merely instantiates a changed
generic rule may be superseded.

## Practical simulator boundary

The safe architecture is to keep:

- KO trigger eligibility;
- non-destination effect execution;
- destination-program conflict resolution;
- physical zone movement;

as separate concepts with explicit evidence for any ordering relation between
them.

That prevents a destination router from erasing an earlier side effect and
prevents a generic ordering heuristic from overriding a specific destination
conflict ruling.
