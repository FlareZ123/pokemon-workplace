# Deck-informed Quick Ball fallback after search reveals a Prized target

## Research question

A fixed-priority search model may instruct Quick Ball to retrieve Tapu Lele-GX because Wonder Tag provides access to Gladion. What if Tapu Lele-GX is Prized? Quick Ball searches the **remaining deck** for **any eligible Basic Pokémon**. A player who looks through the deck may instead take a required attacker, preserving the possibility of drawing Gladion naturally later.

This is a K0-to-K1 transition in the sense of [the project's human concepts](../../resources/human_concepts.md): a player's first search reveals the deck's remaining contents and allows the Prize composition to be inferred, assuming accurate deck knowledge. Treating target preferences as irrevocable before inspection is a voluntarily restrictive counterfactual.

This result adds the optional `allow_search_fallback=True` mode to [tools/quick_ball_pre_draw_option.py](../../tools/quick_ball_pre_draw_option.py). The previous strict-target model is preserved by the default `False`.

## Game mechanism

The analysis still uses a 60-card synthetic Expanded deck with one Tapu Lele-GX, one required Basic attacker, ten other starter Basics, two Gladion-like rescue Supporters, four Quick Ball, four critical non-starter cards, variable designated discardable cards, and filler. It samples a valid seven-card opening, then six Prizes, then one natural draw. Results condition on at least one critical card being Prized.

The eager **rescue-priority** model spends one payable Quick Ball before the natural draw when neither Gladion nor a live hand-play Tapu Lele-GX is available.

- **Strict target:** attempting to find Tapu Lele-GX consumes Quick Ball and one payable discard, even when Lele is Prized, without selecting another Basic.
- **Deck-informed fallback:** if searching reveals no Tapu Lele-GX in the deck, select the attacker instead when it is still needed and searchable. Then, if the natural draw supplies a Gladion, both modeled channels can succeed.

An attacker-priority eager search that fails to find the singleton attacker cannot obtain joint success later in this model, because that attacker is absent from the entire non-Prize state. Accordingly, its computed joint probability remains unchanged by the fallback option.

Every search still consumes only one physical Quick Ball and one designated discard. The alternate target must actually remain in the searchable deck. This is a legal use of the unrestricted Basic Pokémon target class of Quick Ball, under the usual Item permission.

## Exact results

| Dedicated disposable cards | Fixed rescue target | Deck-informed fallback | Increase |
| ---: | ---: | ---: | ---: |
| 4 | 10.244034% | 10.274140% | 0.030106 pp |
| 8 | 14.080669% | 14.130320% | 0.049651 pp |
| 12 | **16.919584%** | **16.981103%** | **0.061519 pp** |
| 16 | 18.950549% | 19.018596% | 0.068047 pp |
| 20 | 20.341965% | 20.413046% | 0.071082 pp |
| 24 | 21.242479% | 21.314508% | 0.072029 pp |

The **17.755369%** D12 wait-until-after-draw joint success remains unchanged. With deck-informed fallback, waiting exceeds rescue-priority eager spending by approximately 0.774266 pp instead of 0.835785 pp. The narrower gap is a better baseline for comparing genuinely available target choices, even though a realistic adaptive policy can also decide to withhold Quick Ball entirely.

## Validation

The exact enumerator sums the accepted opening and disjoint Prize category states and resolves the pre-draw search plus one later natural draw, including physical removal of searched targets. The independent [labeled-card oracle](../quick_ball_pre_draw_option/reproduce.py) has been extended to permit the same alternate target **after discovering the preferred target is missing**. It still enumerates physical hands, Prizes and draws.

[Reproduce](reproduce.py) compares all three objectives under the fallback switch against the physical oracle on two different labeled toy decks (11 and 12 cards) and checks the six 60-card disposable-pool cases. The retained default strict-target oracle remains tested by [the pre-draw option regression](../quick_ball_pre_draw_option/reproduce.py).

Focused [GitHub Actions validation](../../.github/workflows/validate-quick-ball-k1-fallback.yml) automates the physical cross-check.

## Limitations

The result computes opening resource access, with no matchup or tournament performance data. The synthetic model uses one attacker, one Tapu Lele-GX, and two Gladion-like Supporters. Actual tournament lists have additional search cards, alternate attackers, Supporter use restrictions, board occupancy constraints and matchup-specific incentives.

The choice to take the attacker on a missing Lele remains only a narrow two-channel fallback. Full K1 policy optimization could select any legal Basic for its continuation value and might use acquired Prize information to change other subsequent actions. The exact fallback premium is therefore **one demonstrated correction**, with no assertion that it captures the entire strategic value of seeing the deck.
