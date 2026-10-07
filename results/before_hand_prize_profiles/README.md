# Typed Prize-origin before-hand trigger profiles

## Question

How many effectively legal Expanded cards in the bundled English card pool use the Prize-origin E-31 timing window, and do they share one executable behavior?

The audited pool contains five exact prints, split across three mechanical families.

Implementation: `tools/before_hand_prize_profiles.py`  
Regression: `results/before_hand_prize_profiles/reproduce.py`

## Coverage correction

The existing Prize-effect atom compiler recognized wording of the form:

`took this card / this Pokémon as a face-down Prize card ... before you put it into your hand`

Dream Ball and Greedy Dice instead say:

`if you took it as a face-down Prize card, before you put it into your hand`

That literal wording difference caused the live compiler to omit their `before_hand_prize_trigger` atom.

The compiler now accepts the narrow `it` variant as well. Named regressions cover Dream Ball and Greedy Dice alongside the previously recognized examples.

## Complete audited set

The five effectively legal exact prints are:

| Card | Print | Family | Self destination | Extra Prize |
| --- | --- | --- | --- | --- |
| Jirachi ◇ | `sm7-97` | self to Bench | in play | guaranteed |
| Chansey | `sv3pt5-113` | self to Bench | in play | coin heads |
| Dream Ball | `swsh7-146` | Item play | discard after use | none |
| Treasure Energy | `swsh7-165` | self attach | attached | none |
| Greedy Dice | `xy11-102` | Item play | discard after use | coin heads |

The catalog also records whether the trigger text explicitly says "during your turn", whether the card text itself requires an open Bench, and whether the card searches a Pokémon from the deck onto the Bench.

## Three execution families

Jirachi ◇ and Chansey move the taken Pokémon itself from the before-hand window into play. Their card text explicitly requires that the Bench is not full.

Treasure Energy moves the taken Special Energy itself from the before-hand window into an attachment relation.

Dream Ball and Greedy Dice are Items that become playable specifically inside this timing window. Their own card is therefore an action object rather than the payload placed onto the Bench. Once the Item finishes resolving, ordinary Item rules send it to discard.

This distinction matters for a state executor. Treating all five triggers as "redirect the pending Prize card" would misrepresent both Items.

## Secondary effects

The profile preserves the directly visible secondary structure needed by the next executor:

- Jirachi ◇ takes one additional Prize after entering the Bench;
- Chansey can take one additional Prize on heads after entering the Bench;
- Dream Ball searches a Pokémon from the deck directly onto the Bench;
- Greedy Dice can take one additional Prize on heads;
- Treasure Energy has no additional Prize-taking branch.

## Finding

The `before_hand_prize_trigger` atom identifies a timing family, while it is too coarse to identify one state transition.

A useful executable representation also needs the activation family, the pending card's destination, gating conditions, stochastic branches, and secondary zone effects.

## Limits

This is a conservative compiler for the five Prize-origin E-31 prints present in the bundled effectively legal English Expanded pool.

Top-deck E-31 cards such as Top Entry Pokémon and Nugget use the same rulebook timing language from a different source event. They are deliberately outside this Prize-origin result.

The profile records Dream Ball's Pokémon-to-Bench search without yet allocating an exact deck target. Existing typed-search infrastructure can supply that witness in a later composition step.

## Next work

Connect these profiles to `prize_pending_take.py`.

The direct self-movement families can use the pending card's existing materialized instance. The Item family needs a temporary resolving state before discard, plus typed execution of its secondary effect. Additional Prize awards should feed back into the Prize-selection and pending queue instead of being represented as an integer-only bonus.
