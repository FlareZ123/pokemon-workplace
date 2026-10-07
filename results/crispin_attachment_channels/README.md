# Crispin attachment channels: effect attachment and normal attachment are independent

## Question

If a Supporter attaches an Energy by effect and puts another Energy into the hand, can the player still use the ordinary once-per-turn Energy attachment for the second card?

Yes. The local advanced manual explicitly states that Energy attachment from an effect is separate from the normal Energy attachment from hand. Crispin provides a concrete Expanded-legal line where this distinction creates an attack that would otherwise be one Energy short.

## Executable case

The reproducer uses Bagon `dv1-6`, whose Dragon Claw attack costs Fire + Water, and Crispin `sv7-133`. Crispin searches the deck for up to two Basic Energy cards of different types, places one in hand, and attaches the other to a Pokémon.

Starting from:

- Bagon Active with no Energy;
- Crispin in hand;
- Fire Energy and Water Energy in deck;
- the Supporter action unused;
- the normal Energy attachment unused;

the shortest represented setup is two actions:

1. play Crispin, attach one of Fire or Water by effect, and put the other into hand;
2. use the ordinary attachment to attach the Energy that Crispin put into hand.

The Energy kernel then verifies that the resulting attached units exactly satisfy Dragon Claw's `RW` cost.

## Why one attachment counter is wrong

A simulator with a single generic `attachments_this_turn` counter could incorrectly reject this line after Crispin attaches the first Energy. The rules require at least two channels:

- normal attachment from hand, normally available once per turn;
- attachments produced by card effects.

Those channels can interact with different action budgets. Crispin consumes the Supporter action and performs one effect attachment. It leaves the normal attachment available.

This also means that finding two Energy cards is insufficient as a model. The simulator must retain which card enters hand, which card is attached by the Supporter, and whether the independent normal attachment remains.

## Regressions

`results/crispin_attachment_channels/reproduce.py` checks the following.

| State | Dragon Claw ready through represented line? |
| --- | --- |
| Crispin + both Energy types + unused normal attachment | yes |
| normal attachment already spent | no |
| normal attachment disabled | no |
| Supporter action already spent | no |
| Supporters disabled | no |
| one required deck Energy type unavailable to the represented Crispin search | no |

The negative cases are useful because they isolate different resource failures while leaving much of the card graph unchanged.

## Card-pool validation

The reproducer reads the bundled database and confirms both prints are marked Expanded legal. It checks Bagon's Dragon Claw cost and Crispin's text for the two different Basic Energy types, one-to-hand instruction, and effect attachment.

## Relationship to the Energy action model

`tools/energy_action_budget.py` represents the final typed Energy condition. `tools/typed_energy_access.py` now includes explicit Crispin and manual Basic Energy transitions so the line is discovered through zones and action budgets rather than supplied to the solver as one precompiled route.

This strengthens the earlier result by showing that the distinction between effect attachment and normal attachment can be represented directly in a state search.

## Limits and next work

The current Crispin transition is deliberately targeted to this Fire + Water example. It requires both Energy cards to begin in the deck and does not enumerate partial Crispin searches or arbitrary Energy types. That keeps the regression small and auditable.

A stronger compiler should represent Energy cards by identity, type, and zone and instantiate search/attachment transitions from card semantics. It should also track turn windows so Supporter availability, normal attachment refresh, and attack availability change at the correct boundaries.
