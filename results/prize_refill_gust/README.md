# Prize taking is a draw engine for the next gust

## Question

Our earlier `stochastic_gust_draw` model drew exactly one new card before each attacker turn and treated Prize cards only as an endgame score. But a Pokémon Knock Out also puts taken Prize cards into the winner's hand. Can taking a three-Prize Knock Out supply the Boss's Orders needed to complete a second gust KO?

## Evidence and model

Advanced Player's Rulebook G describes a seven-card opening hand and six face-down Prize cards; D resolves the Prize-taking process after a Knock Out; H describes drawing and deck search. The shared `human_concepts.md` proposes K0/K1 as a distinction between not yet having searched the deck versus inferring which cards are Prized after deck search.

`tools/prize_refill_gust.py` starts with a uniformly randomized **60-card abstract deck** containing K Boss's Orders-like Supporters and 60-K inert filler cards, for K between zero and four. It enumerates the exact joint hypergeometric distribution of the seven-card starting hand, six Prizes, and 47 remaining deck cards.

The source board is the previous one-hit KO, adversarial-promotion six-Prize scenario. Each attacker turn begins with exactly **one natural draw**. The player chooses to attack the current Active or spend one available Boss token to select an opposing Benched target. On a KO of a target worth r Prizes, the player randomly takes r of their remaining facedown Prize cards, and **any Boss cards in those Prizes enter the player's hand** for future turns.

Key constraints: the current player is assumed to have completed an initial deck inspection, reaching **K1** knowledge of how many gust copies are Prized, while their exact face-down Prize locations remain random. We model the attack plan conditional on a previously established opposing board; we do not enforce opening-hand Basic selection/mulligans or compute the chance of establishing that board. An opponent chooses worst-case promotions after each KO. The opponent knows the distribution of the Prize cards just drawn but in the default mode does not know their exact identities; its other information is modeled more strongly than in real play. No non-Boss Supporters, search, energy payment, opposing damage or new Bench entries are included.

The counterfactual `recover_prize_cards=False` removes the ability to use Boss copies drawn from Prizes while leaving the other state transitions unchanged. It is a comparison kernel, not real Pokémon TCG rules.

## Four-target endgame witness

Opposing Active: **1 Prize**. Bench: **1, 3 and 3 Prizes**.

A two-attack win requires gusting and KOing the two three-Prize targets on consecutive turns. The first KO also yields **three Prize cards**, so the player may find another Boss there.

Across all opening 7-card hands, Prize placements and deck draws, the exact expected number of attacker turns is:

| Boss copies in 60 | With Prize-to-hand refill | If Prize refill is suppressed |
| ---: | ---: | ---: |
| 0 | 4 | 4 |
| 1 | 4 | 4 |
| 2 | 1387/354 = 3.918079 | 2333/590 = 3.954237 |
| 3 | 2233/590 = 3.784746 | 13259/3422 = 3.874635 |
| 4 | 588821/162545 = 3.622511 | 122593/32509 = 3.771048 |

The first two copies alone cannot guarantee an early double-gust route because they can be in the opening hand, draw pile or Prize cards. With four total Boss copies, recovering gusts through earned Prizes reduces expected attack count by about **0.149** in this stylized endgame.

## Exact probability of a two-attack finish

For the two-attack line, let K be the number of Boss copies in the 60-card deck. The seven-card hand plus the first natural draw expose eight uniformly sampled cards. Let H be the number of Boss copies among those eight.

- If H is zero, the player cannot gust a three-Prize Bench target on attack one.
- If H is two or more, both gusts are already held.
- If H is exactly one, the second must appear in the second turn's natural draw **or one of the three Prizes** taken after the first three-Prize KO.

There are 52 unknown cards after the first eight are seen. With Prize refill, the second Boss is found among four more exposed cards: three Prize cards and one deck draw. Without Prize refill, only the next natural draw can help.

The exact two-turn success probabilities are:

| Boss copies | With Prize refill | Without Prize refill |
| ---: | ---: | ---: |
| 0 or 1 | 0% | 0% |
| 2 | 2/59 = 3.3898% | 6/295 = 2.0339% |
| 3 | 774/8555 = 9.0473% | 96/1711 = 5.6108% |
| 4 | 78542/487635 = 16.1067% | 3354/32509 = 10.3171% |

The four-copy scenario's two-attack opportunity is approximately **56% more likely** when Prize-card recovery is modeled. This is conditional on the board and opening-deal abstraction described above.

## Validation and reproducibility

`results/prize_refill_gust/reproduce.py` validates:

1. Each joint hand/Prize/deck partition distribution sums to exactly one.
2. All ten expected attack-count fractions in the table.
3. An **independent sequential enumeration** of opening hands, first draw, three Prize cards and second draw, matching the closed-form two-turn probabilities for K=0..4.
4. **5,110 exact cross-kernel comparisons**: on every one of 146 one-hit board classes and every legal opening zone partition for K=0..4, disabling Prize-refill reduces to `tools/stochastic_gust_draw.py`.

All calculations use `fractions.Fraction` and have no sampling error.

Run from repo root: `python results/prize_refill_gust/reproduce.py`.

## Interpretation and next steps

One successful high-Prize knockout can generate the card needed for a follow-up gust. Models that treat Prizes only as a scalar score underestimate this positive draw feedback, particularly when few gust copies are in hand at the first attack.

This does not establish an optimal Boss count for real Expanded. Mulligan-conditioned opening hands, Pokémon/Supporter search, the normal first-turn Supporter restriction when playing first, additional Prize effects, other Supporter plays and opponent disruption matter. A next experiment can incorporate actual search-item paths and compare K0 versus K1 information by maintaining a belief over unseen Prize composition rather than handing the player the exact remaining count.
