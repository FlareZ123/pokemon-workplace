# Aichi Regidrago: zero causal effect of a same-hand Basic attachment on Crispin deck stock

**Status:** rules-derived invariant, exact physical-card calculation, independent finite toy enumeration. This supersedes the tactical interpretation of the [earlier composition-conditioned study](../aichi_regidrago_crispin_post_trifrost/).

## The controlled counterfactual

The published tenth-place Aichi list contains four Grass Energy, two Fire Energy, four Double Dragon Energy, Regidrago VSTAR, Kyurem, and Crispin. Consider **one fixed game state** with both Grass and Fire in the same hand along with DDE. Compare the action of attaching held DDE plus held Grass to Regidrago versus attaching held DDE plus held Fire. Assume the selected pair is eventually discarded by Regidrago copying Kyurem's Trifrost and that no intervening effect changes deck composition.

The **deck and Prize identities are unchanged** by the choice. Both candidate Basic cards were already outside the deck, so Crispin's later *searchable deck inventory* is identical. The discarded and remaining hand card identities differ, which can matter for later manual attachments and recovery.

This is an exact causal statement conditional on the specified actions. It does not assert the complete resulting game states have equal value.

## Exact naturally conditioned paired probability

Require a Basic-valid seven-card opening and then the first natural draw, as in [the T1 natural exposure study](../aichi_regidrago_t1_natural_choice/). Condition further on **Regidrago V, DDE, at least one Grass and at least one Fire** being among those eight visible cards. The 60 contains four Regidrago V, eleven other Basics, four DDE, four Grass and two Fire. Six Prize cards are uniformly selected among the 52 cards outside the observed first-eight set.

Enumerate all 102 eligible physically categorized eight-card multisets weighted by their number of valid opening-seven placements. For each, calculate the exact probability that the *same* remaining 52-card population, after six Prizes, retains both Basic types in deck. That expectation is:

| Same observed hand and Prizes | Chance both Basic types remain in deck |
| --- | ---: |
| Attach held Grass, later Trifrost discards it | **84.716275938%** |
| Attach held Fire, later Trifrost discards it | **84.716275938%** |
| Difference for this deck-stock endpoint | **0 percentage points** |

The common exact probability is `33898500113/40014152815`. This result is conditional on early **natural** visibility of all four required materials; that event itself has probability `20692516/1505320575`, or **1.3746252%**, conditional on a valid opening. Search/draw/evolution actions are excluded from both models.

## Independent validation

`tools/aichi_regidrago_crispin_paired_causal.py` supplies an explicit per-hand, per-deck, per-Prize movement function `after_payment`. The [reproducer](reproduce.py) checks both action branches in **137 miniature physical deck configurations** by enumerating each Basic-valid opening subset, random Prize subset, and subsequent natural draw. Its oracle calculates the remaining deck from physical positions before executing either payment.

Run from repository root: `python -m results.tests.aichi_regidrago_crispin_paired_causal.reproduce`.

## Practical correction

The source deck contains twice as many Grass as Fire, and earlier work rightly found differing future Crispin stock probabilities **after conditioning on different cards already outside the deck**. Comparing these conditional distributions cannot justify a same-hand attachment policy because it changes the starting information state. The correct comparison requires the same hand, Prize identities, board resources, opponent and search conditions for both actions.

An advanced policy can still prefer to retain one Basic Energy over another for a **later hand attachment**, recovery or discard-resource reason. That is a different continuation objective requiring explicit multi-zone state transitions. No current evidence here measures actual win-rate advantage.

Source tournament list: https://limitlesstcg.com/decks/list/26816 .
