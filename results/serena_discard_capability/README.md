# State-dependent discardability: extra Serena can become the optimal discard

## Question

The human research notes `resources/human_concepts.md` introduce Discard Capable Index (DCI), stressing that a nominally powerful card may become expendable when its tactical role is already fulfilled. Serena's first Supporter mode requires a discard of **at least one and at most three hand cards**, then draws until five remain in hand. Does strategically protecting extra Supporters from discard make this mode less effective?

## Experimental comparison

`tools/serena_draw_option.py` tracks three hand and draw-pile card categories: Boss's Orders, Serena, and inert filler. Every turn begins with one natural draw; a Supporter may gust (Boss any target, Serena Pokémon V only) or Serena may discard selected hand cards and draw until five. The player can make at most one Supporter play per turn. The opposing board uses one-hit KO targets worth one to three Prizes and adversarial opponent promotion, from `results/typed_gust_target_minimax/`.

The **unrestricted** draw policy follows Serena's actual card text by allowing up to three discarded cards from any category, as long as at least one is discarded. In particular, it can discard another Serena or a held Boss.

The **protected** counterfactual permits Serena's draw mode to discard only inert filler; Boss and additional Serena copies are treated as undiscardable. It is a useful test of an overly aggressive UDP assumption rather than an alternative rule.

Both models optimize target choices, Supporter usage, drawing, and discards. All tested draw piles have 20 cards, with 1 or 2 Boss copies and the balance filler. The initial hand contains either 2 or 3 Serena copies, zero Boss and zero filler. Prize taking does not supply future cards within this specific model.

## Full typed-board census

Across 582 structural boards from the existing one-/two-/three-Prize V-family model:

| Serena in hand | Boss in 20-card draw pile | Boards where allowing Serena discard improves attack count | Largest expected attacks saved |
| ---: | ---: | ---: | ---: |
| 2 | 1 | 52/582 | 1/20 |
| 2 | 2 | 65/582 | 13/190 |
| 3 | 1 | 114/582 | 1/10 |
| 3 | 2 | 128/582 | 27/190 |

These counts describe uniform tactical board classes, not the frequency of such hands or matches. The advantage occurs because an extra Serena can become redundant as a gust source, particularly against a board without Pokémon V targets, and discarding it makes the next Serena draw reach deeper.

## Exact example and closed-form validation

Opponent Active **three-Prize non-V**, Bench **one-Prize non-V and three-Prize non-V**. An attacker with two Serena copies but no Boss in hand has no legal target for Serena's gust mode. A Boss drawn before the next attack enables a two-attack finish.

After a natural filler draw, playing one Serena in draw mode leaves another Serena and the filler. If the player protects the remaining Serena, discarding filler only leaves one Serena in hand and draws four cards to reach five. If the player discards both the filler and the other Serena, the draw reaches five fresh cards.

For B Boss copies among an original 20-card draw pile:

- With **two Serena** held, filler-only discards expose six original deck cards through the second natural draw. The unrestricted policy can expose seven.
- With **three Serena** held, filler-only discards expose five, while discarding the two spare Serena permits seven.

The expected attack counts are exactly `2 + C(20-B,m)/C(20,m)`, with m the total deck cards exposed early enough to find Boss. These formulas agree with the solver for B=1 and B=2.

As a concrete example, with three Serena in hand and two Boss in the 20-card deck, the protected policy's expected attack count is `2 + C(18,5)/C(20,5) = 97/38 ≈ 2.552632`. The unrestricted policy yields `2 + C(18,7)/C(20,7) = 229/95 ≈ 2.410526`. The difference is `27/190 ≈ 0.142105` expected attacks.

## A useful boundary

Discarding tactically important cards should remain conditional. With **exactly one Serena and one Boss already held** and an otherwise identical 20-card draw-pile family, allowing Serena to discard Boss does not improve expected attack count over protecting Boss in any of the 582 board classes tested, for either one or two Boss copies left in deck.

Thus the advantage of allowing all legal discards comes from particular redundant-resource states. It is a context-sensitive discard decision, with card roles, remaining targets, and timing considered.

## Validation

`results/serena_discard_capability/reproduce.py` asserts the complete 2,328-case (582 boards × two Serena quantities × two Boss deck counts) comparison, exact counts above, four independently derived draw-position formulas, and that the discard action involving an extra Serena is accessible only under the unrestricted payment policy.

It additionally checks the one-Serena/one-Boss hand boundary across the same 582 boards for B=1,2.

Run: `python results/serena_discard_capability/reproduce.py`.

## Limits

This conditional tactical study has a compressed hand, guaranteed attacks and exact deck category counts. It omits search connectors, Prize-card draws, other Supporters, opponent interaction, detailed discard pile recovery, Item lock and arbitrary deck card types. It does not provide a scalar DCI for Serena. It supplies a checked example of how DCI is a state-dependent *action feasibility and future utility* property.
