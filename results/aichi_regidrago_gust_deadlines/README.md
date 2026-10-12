# Regidrago Guzma versus Counter Catcher: exact two-turn source deadlines

## Playable candidate and evidence

The [complete 60-card experimental decklist](regidrago_counter_catcher_60.txt) changes exactly one card in [Haruku Yoshioka's 2026 Aichi Open League 10th-place Regidrago](../competitive_deck_baselines/#2026-aichi-open-league-10th-place-regidrago-vstar): **-1 Guzma (sm3-115), +1 Counter Catcher (sv4-160)**. The original has **2 Guzma + 1 Prime Catcher**; the experiment has **1 Guzma + 1 Prime Catcher + 1 Counter Catcher**, with the same **15 Basic Pokémon** and **one ACE SPEC**. [The exact-print reproducer](reproduce.py) rebuilds and checks the candidate through the repository's October 12, 2026 Expanded legality adjudicator. This is a plausible control/disruption counterfactual, **not a demonstrated upgrade**.

The printed cards have different gates:

- **Guzma** (Supporter): gust, subject to Supporter-use eligibility.
- **Prime Catcher** (ACE SPEC Item): gust, subject to Item-use eligibility.
- **Counter Catcher** (Item): gust **only when its player has more Prize cards remaining than the opponent**.

Guzma and Prime Catcher also have own-Active switching effects; this access model assumes usable opposing Bench targets and does not attempt to optimize the resulting board.

## Exact first-two-turn access, conditional on valid opening

The [Fraction-valued engine](../../tools/aichi_regidrago_gust_deadlines.py) deals a uniformly random seven-card opening hand from the physical 60, conditions on containing at least one of the deck's 15 Basic Pokémon, sets aside six uniformly random Prizes, and observes one natural draw at the start of each of the player's first two turns.

We ask whether at least one of the named gust cards is **held and belongs to a presently legal source class** by the indicated deadline. First/second own-turn access can be enabled or disabled by separate exogenous Item and Supporter permissions and a first/second-turn Prize-behind state. An unplayable source can be retained until its gate opens. No extra draw, search, VS Seeker recursion, opponent hand interference, or opponent targets are simulated.

| Two own-turn permission scenario | Published P(source by T1) | Swap P(source by T1) | Published P(source by T2) | Swap P(source by T2) | Swap change at T2 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Open; never behind | 34.286559% | 24.208012% | 38.077719% | 27.123088% | **-10.954630 pp** |
| Open; behind on T2 | 34.286559% | 24.208012% | 38.077719% | 38.077719% | **0.000000 pp** |
| Item-locked on T2; behind T2 | 34.286559% | 24.208012% | 36.813999% | 25.665550% | **-11.148449 pp** |
| Supporter-locked on T2; behind T2 | 34.286559% | 24.208012% | 35.550279% | 36.813999% | **+1.263720 pp** |
| Item-locked on both; behind T2 | 24.208012% | 12.825315% | 27.123088% | 14.501751% | **-12.621337 pp** |
| Supporter-locked on both; behind T2 | 12.825315% | 12.825315% | 14.501751% | 27.123088% | **+12.621337 pp** |
| Going first (no Supporter T1); behind T2 | 12.825315% | 12.825315% | 38.077719% | 38.077719% | **0.000000 pp** |
| Going first; Item-locked T2; behind T2 | 12.825315% | 12.825315% | 36.813999% | 25.665550% | **-11.148449 pp** |

**Interpretation:** The swap improves conditional natural access against sustained Supporter lock when behind, but sacrifices access under Item lock and ordinary tied/ahead boards. A delayed Supporter lock gives the variant only a small improvement because its sacrificed Guzma copy remains usable on turn one. Neither a lock's likelihood nor the probability of becoming behind on Prizes is estimated here.

The first-turn availability shown when Supporters are allowed represents going second, unless a special source permits another timing. In a game where the player goes first, playing a Supporter on the first turn is prohibited; the last two rows model that distinction. The “behind T2” condition is hypothetical and can be met after an opponent attacks, rather than presumed to exist at game setup.

## Method and independent verification

The exact solver enumerates the initial accepted hand as physical multivariate-hypergeometric classes: Basic, Guzma, Prime Catcher, Counter Catcher, filler. It then enumerates the first and second natural draws without replacement. The chance of the next drawn source is the same after marginalizing six uniformly random Prizes as if the card were drawn from the remaining 53-card post-opening pool (subject to enough deck cards for both turns). The solver evaluates allowed classes separately for each own turn.

As a special check, if **g** cards are continuously allowed and all are non-Basic, then conditional access through **k** draws has the closed form

`1 - ([C(60-g,7)-C(45-g,7)]/[C(60,7)-C(45,7)]) * C(53-g,k)/C(53,k)`.

The reproducer independently deals **labeled physical cards** into a three-card toy hand, random two-card Prize set, and ordered first/second draws from a ten-card toy deck. It checks **32 separate deck-and-lock configurations** against the exact rational engine. The toy oracle retains actual Prize selection, so it also independently checks the Prize marginalization. It verifies the actual 60-card candidate's category counts, Basic count, print texts, and deck legality via source files.

To reproduce from repository root: `python -m results.aichi_regidrago_gust_deadlines.reproduce`.

## What would change the recommendation

This is an exact natural-card-access boundary, with a deliberately limited policy. **VS Seeker** (three copies in both decks) can recover discarded Guzma, while **Prime Catcher** is a unique ACE SPEC and **Counter Catcher** has the behind-on-Prizes restriction. The model ignores all of those longer-term option values beyond a currently held named gust source. It also omits actual board targets, Item lock established by Vileplume or Budew, Supporter lock established by Stoutland, opposing effects, the evolving attacker, Active placement, and survival.

A rigorous competitive decision requires estimating the likelihood and timing of falling behind on Prizes versus facing the different locks, plus simulation or games against Shadow Rider, Vileplume, Mew/Genesect, Regidrago mirrors, and Iron Thorns. **Retain the published 2-Guzma version as the evidence-backed tournament baseline** until the proposed swap shows an advantage against a representative opponent field.

**Verification status:** [Windows GitHub Actions run 38247993886 passed](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38247993886) on October 12, 2026.
