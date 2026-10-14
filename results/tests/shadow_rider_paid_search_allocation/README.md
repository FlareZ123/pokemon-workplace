# Shared paid search in the champion Shadow Rider anti-Path / Iron Thorns launch

## Result

The published 2026 Aichi champion Shadow Rider Calyrex deck runs **four Mysterious Treasure**, **one Quick Ball**, **four Fog Crystal**, **one Forest Seal Stone**, and **one Marshadow with Resetting Hole**. The two prior exact studies added Fog Crystal retrieval of Marshadow and Shadow Rider Calyrex V, with explicit physical search allocation. This study adds **Mysterious Treasure and Quick Ball searches with actual discard payment**, and permits Fog Crystal to retrieve **Basic Psychic Energy** to make a paid search usable.

Under the same one-Canceling-Cologne/one-Flutter tech scenario, conditional on a Basic-valid seven-card opener, six hidden Prize cards, the first natural draw, and the specified opposing Path to the Peak + Active Iron Thorns ex board:

| Restricted search model | Exact conditional launch access |
| --- | ---: |
| Marshadow Path answer, no Fog routes | 2.811877949% |
| Fog Crystal can retrieve Marshadow | 5.039162596% |
| Fog Crystal can also retrieve Shadow Rider V for Forest Seal Stone | 5.426283560% |
| **Paid Mysterious Treasure / Quick Ball, with Fog-funded Psychic Energy payment** | **7.327398814%** |

The final step increases the prior endpoint by **1.901115254 percentage points**. Each percentage is the output of its explicitly restricted model. These models describe feasible opening **card access**, not competitive match win rates.

## Correctly paid and shared resources

The exact solver assigns each searched Basic to one legal connector:

- **Radiant Eternatus** (Dragon Basic) can be held or searched with Mysterious Treasure or Quick Ball. Fog Crystal cannot find it.
- **Marshadow** (Basic Psychic) can be held or searched with Fog Crystal, Mysterious Treasure, or Quick Ball, provided it can occupy the Bench for Resetting Hole.
- **Shadow Rider Calyrex V** (Basic Psychic) can be held or found by those same search Items when Forest Seal Stone is held. Star Alchemy may then search one remaining role.
- Each **Mysterious Treasure and Quick Ball** use spends its own physical Item and exactly one Basic Psychic Energy from the hand. A held Fog Crystal can supply a Basic Psychic Energy from the deck before that search, consuming that Fog Crystal. Every Fog Crystal can be spent once: `fog_for_marshadow + fog_for_v + fog_for_energy <= held_fog`.

The solver also enforces a surviving Radiant / Cologne / Marshadow / Stadium-or-Field-Blower / Shadow Rider V supply in the deck, two Shadow Rider VMAX in deck for Climactic Gate, the Bench-only Marshadow position, and no more than one Forest Seal Stone search. The source baseline has eleven Basic Psychic Energy and six hidden Prizes, so the model's at-most-five paid searches have a sufficient physical Energy pool for the number of Fog-funded payments enumerated.

A finite search-allocation planner enumerates combinations of roles, physical search sources, paid Energy, and Forest Seal Stone's final missing piece. Exact combinatorial weights integrate all Basic-valid opening-seven hands, their first natural draw, and all six Prizes using integer arithmetic and rational `Fraction` probabilities.

## Validation

The [reproducer](reproduce.py) executes source-print checks and source-budget witnesses, including situations where one Fog cannot fetch two needed Basics, and where one Treasure's mandatory discard requires Energy in hand or a separate Fog-to-Energy route. An independently enumerated **83,720-world labeled-card toy experiment** exactly matches the combinatorial evaluator. Full 60-card one-Cologne/one-Flutter calculation and all these assertions passed manual-only Windows CI [run 38611969086](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38611969086).

The earlier shared-Fog exact value of **5.426283560%** is reproduced inside this same evaluator; comparisons therefore preserve the same conditioning and counts. The first CI attempt caught a faulty assertion in an artificial test witness: two Fog Crystal copies can fetch both Marshadow and Shadow Rider V without Treasure, as the game permits. That assertion was repaired, and the subsequent run succeeded.

## Critical information-state and gameplay limitations

**This is an information-privileged feasibility upper bound, not a demonstrated K0 first-search policy.** Before inspecting their deck, a player cannot tell exactly which relevant cards are Prized. The solver's existential decision over alternative search paths can vary with the actual six-card Prize composition, which might not be inferable until a legal search is initiated. A realistic policy must select its first action from the observable opening hand, then may use newly acquired K1 information to choose subsequent lines. The exact arithmetic remains valid for the stated omniscient feasibility question; the 7.327399% figure must not be marketed as a proved achievable turn-one success rate.

Other simplifications: no competing strategic value or later Energy demand, no discarding other protected cards, no non-Psychic discard targets, no alternative Fog Crystal roles outside those listed, no additional draw, no further opponent response, no Bench congestion beyond the Marshadow requirement, and no proven legality or source selection policy for a complete turn. The assumed opposing board is a specified state, not a measured frequency. The two-tech deck is an explicitly hypothetical variant of the published champion's tournament-tested 60.

## Next research

Implement a **nonanticipatory first-search policy** whose first paid or free search choice depends only on the observable opening hand, with the Prize-dependent branches selectable only after that legal deck inspection. Compare the optimal K0 policy against the information-privileged access upper bound, then extend to matchup-dependent DCI and a legal full-game player policy. Other agents have independently reported hidden-Prize information leakage in the pinned Twinleaf native Quick Ball AI, which reinforces the need for this separation.

This is a restricted opening-line research contribution. It is insufficient to establish a better tournament decklist or a match winning percentage.
