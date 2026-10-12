# Sequential Regidrago gust: the second Guzma versus Counter Catcher

## The tactical question

The [legal 60-card Aichi Regidrago swap](../aichi_regidrago_gust_deadlines/) changes **2 Guzma + 1 Prime Catcher + 3 VS Seeker** to **1 Guzma + 1 Counter Catcher + 1 Prime Catcher + 3 VS Seeker**. A simple two-turn source-in-hand measure finds identical access (38.077719%) in a scenario where Counter Catcher becomes legal on turn two. That does not settle the **two-turn sequence** requiring **Guzma on turn one, followed by another gust on turn two**.

This analysis incorporates source consumption and recovery:

1. Start with a uniformly shuffled 60-card deck and a seven-card initial hand containing at least one Basic Pokémon (15 copies in the 2026 Yoshioka list). Place six uniform Prizes and draw once on own turn one, going second so Guzma is legally playable.
2. If Guzma is held, play exactly one Guzma and put it into discard. We assume an opposing Benched target and an otherwise executable action.
3. Draw once on own turn two. A second gust is available if a different held Guzma can be played, or **VS Seeker** can return the discarded Guzma and that Supporter can be played, or **Prime Catcher** can be played, or **Counter Catcher** can be played when behind on Prizes. An exogenous turn-two Item lock prohibits VS Seeker, Prime, and Counter; a Supporter lock prohibits Guzma directly and via VS Seeker.
4. Report the joint probability of the two-turn chain and the conditional probability of a follow-up **given** a first-turn Guzma, while preserving the distinction.

There is no assumption that VS Seeker is usable merely because it is held: the first Guzma must genuinely have reached discard, the Item and Supporter restrictions must permit its retrieval and replay, and the first Supporter use occurred on the **previous** turn.

## Exact 60-card findings

All probabilities are conditional on a valid Basic opener. “T1 Guzma” is the probability that the opening seven plus first natural draw contains the Supporter. “Double gust” requires the T1 use and a T2 available follow-up as specified above.

| Turn-two restriction | Published double gust | Swap double gust | Published follow-up given T1 Guzma | Swap follow-up given T1 Guzma |
| --- | ---: | ---: | ---: | ---: |
| Open; tied or ahead | **11.750825%** | 5.585878% | **48.541056%** | 43.553531% |
| Open; behind | **11.750825%** | 6.596721% | 48.541056% | **51.435159%** |
| Item locked; behind | **1.880414%** | 0.000000% | 7.767733% | 0.000000% |
| Supporter locked; behind | **3.159484%** | 3.134404% | 13.051399% | **24.439201%** |
| Supporter locked; tied/ahead | **3.159484%** | 1.661516% | **13.051399%** | 12.954971% |

Across scenarios the first-turn Guzma event itself occurs in **24.208012%** of valid original-list starts, versus **12.825315%** with the swap. Consequently, even when the conditional T2 follow-up favors the swapped list, the unconditional *two-turn Guzma into gust* chain can still strongly favor the published list. In an Item-locked turn two, the swapped deck has no second Guzma remaining after spending its sole copy on turn one, and all three other source types are Items, so the forced sequence has zero success probability in the model.

This **conditioning inversion** is an important lesson for deck optimization: the same accessible-card count and even a better conditional continuation can hide the loss of a scarce first-action prerequisite. It is an example of card-consumption and connector-substitution effects changing what the apparent gust redundancy means.

## Verification and evidence

The [exact mathematical engine](../../tools/regidrago_double_gust_access.py) enumerates physical hand-category multiplicities, then the first and second natural draws, and explicitly consumes one held Guzma before evaluating the second-turn source. It integrates the six random Prizes out using without-replacement exchangeability. The [independent reproducer](reproduce.py) instead enumerates a complete **labeled, tenable miniature game-zone deal**: three-card hand, two set-aside Prizes, ordered two-card draw, actual hand removal of the first Guzma, then checking the legal second-turn source. **16 independently enumerated small-deck scenarios agree exactly** with the Fraction solver, spanning the Guzma/VS Seeker/Prime/Counter distribution and Item/Supporter conditions.

The source regression checks the [full 60-card original and swapped list](../aichi_regidrago_gust_deadlines/), their conservative paper Expanded legality, and the physical `xy6-110` VS Seeker text: *put a Supporter card from your discard pile into your hand*. It does not treat an unspent or Prized Guzma as eligible for retrieval.

Reproduce: `python -m results.regidrago_double_gust_access.reproduce`. The manually triggered Windows CI workflow tests these conditions without consuming GitHub Actions minutes on ordinary pushes.

## Scope and deck implication

The test *forces* Guzma use on T1 when present; it does not optimize whether that is a sound tactical choice. It assumes a legal opposing Bench target, no opponent-induced hand disruption, no alternative searches or extra draws, no changes to hand other than spending Guzma and drawing once, and only exogenous turn-two source locks. Regidrago VSTAR attack readiness, extra turns from Timeless-GX, opponent counterplay, damage, and how often the game is behind on Prizes are outside this model.

The published **two-Guzma** configuration is favored as a first-two-turn sequential-access baseline, even though the Counter Catcher alternative has situational benefits under Supporter lock. **No inferred match-win probability, field frequency, or unconditional optimal card swap is claimed.** The appropriate next test is a matchup- and turn-state-weighted model with realistic card searches and attacking policy.
