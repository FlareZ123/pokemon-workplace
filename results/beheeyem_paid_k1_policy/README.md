# Paid early Ultra Ball K1 information can be worth acquiring, but only in some pre-lock hands

## Question and design

The [free-K1 opposing Supporter study](../beheeyem_opponent_k1_target/) evaluated the value of knowing how many copies of an opposing player's hypothetical target X are still Prized. The [prelock source study](../beheeyem_prelock_k1_search/) then established how often a physically held Ultra Ball could be paid before Beheeyem's Mysterious Noise Item prohibition.

This study composes both into a **two-stage, physically conserved source-action policy**:

1. Before the opponent becomes Item-locked, it has a Basic-valid seven-card opening, six original Prizes and two natural draws. If it holds Ultra Ball plus two disposable fillers, it can play **one** Ultra Ball, discard those physical cards, inspect the entire deck and choose **zero** Pokémon from its restricted-category search, then shuffle. This early action grants K1 knowledge of its remaining Prized X count. The alternative is to retain those cards and remain K0.
2. After the Beheeyem first attack, the opponent receives one additional natural draw. It cannot play a newly encountered Ultra Ball because of Item lock. It now observes whether Beheeyem's first packet was assembled directly or with a paid tutor, the Prize award r, its own hand (and X Prize count if early search was played), and chooses no reset, Judge or Ace Trainer, when physically held and legal.

The opponent's illustrative deck has exactly **B12 / Ultra Ball4 / Ace Trainer4 / Judge4 / X4 / disposable filler32**, total 60. The Beheeyem packet side remains the previously validated B4/TAE4/Computer Search1/d1, conditioned on three ready Basics and exogenous first-attack Prize rewards. No player has taken opposing Prizes before this modeled reply (opponent q=6).

The early Ultra Ball action is evaluated with a declared nonnegative extra utility cost `tau` representing tactical opportunity cost *beyond* the three physical cards removed. The physical cost is separately conserved: playing Ultra Ball discards the Item and two filler, shrinking the opponent's later full-shuffle deck by three from **53** to **50** before a Judge/Ace redraw. This extra concentration can improve X redraws even if the player never uses its gained K1 information. To keep attribution clear, the engine evaluates the **same paid action without information** as well as the paid K1 version.

The continuation objective remains

```text
P(opponent owns X after reply)
  - lambda × P(Beheeyem next packet | first packet).
```

The early decision is made from **pre-lock cards only**. It integrates over the later random reply draw and first-attack direct/tutor route. It does condition on the exogenously specified future Prize reward r; this is an anticipatory-policy upper bound until an explicit model for r uncertainty is introduced.

## Exact result: physically payable and strategically used are different

Exactly **46.477077%** of Basic-valid early nine-card observed-hand configurations contain Ultra Ball and at least two disposable filler cards. That is the maximal incidence of this specified paid information source.

With `lambda=10`, and the opponent observing first-tutor usage at the later response:

| Beheeyem first-attack Prizes r | Extra early search cost `tau` | Probability early Ultra Ball is chosen | Gain in expected weighted utility |
| ---: | ---: | ---: | ---: |
| 0 | 0 | **0%** | 0 |
| 1 | 0 | **26.220950%** | +0.002432814 |
| 1 | 0.001 | **26.220950%** | +0.002170605 |
| 1 | 0.01 | **12.216193%** | +0.000994933 |
| 1 | 0.10 | 0% | 0 |
| 2 | 0 | **26.220950%** | +0.002849136 |
| 2 | 0.001 | **26.220950%** | +0.002586926 |
| 2 | 0.01 | **12.216193%** | +0.000810837 |
| 2 | 0.10 | 0% | 0 |

At r=1 and tau=0, only **26.220950%** of all legal early hands actually choose the payable Ultra Ball, despite its 46.477077% physical availability. The source is useful only where its future K1 knowledge or three-card deck thinning changes the optimized limited payoff. Assigning a positive tactical cost reduces the selection set. At tau=0.1, even if Ultra Ball is in hand and payable, its local controlled benefit does not justify this added cost.

At r=0 and lambda=10, the opponent never uses early Ultra Ball for this limited purpose. Ace Trainer is Prize-illegal and the opponent strongly prefers preserving Beheeyem's depleted hand, eliminating the payoff from sharpening its own Judge/Ace search decision. That conclusion is parameterized by lambda and does not say the Item is intrinsically bad in a real deck.

The return differences are **unitless gains in the declared linear utility**, not changes in match win probability. The model does not predict the actual frequency of a Beheeyem T2 KO or optimal spending of Ultra Ball for normal Pokémon search.

## Exact sequential physical calculation

For a pre-lock hand category `(a,j,x,u,f,b)`, the initial seven-card Basic requirement creates a count-weighted sampling distribution. The solver groups equivalent pre-lock states by `(a,j,x,paid-search-eligible)`, preserving their exact mass. For each such state, it integrates the one new reply draw from the remaining 51 cards, using actual hypergeometric counts of Ace Trainer, Judge and X.

The remaining six Prize cards retain an exact hidden-X posterior if Ultra Ball was not played. If it was played, the opponent knows the exact remaining X Prize count and may choose a different Supporter action for each z. The response's physical deck has 53 cards without early search and 50 after paying U+2F (plus any later played Supporter discarded).

The early search decision compares the expectation of the K0 continuation to that of the paid-K1 continuation minus tau; it cannot condition on the later actual reply draw, actual z before searching, or first-packet direct/tutor route. The later action can respond to that public tutor route.

## Validation and limits

- [Exact sequential action engine](../../tools/beheeyem_paid_k1_policy.py) asserts probability normalization, agreement with the independent prelock Ultra Ball source-access formula, payoff order `paid K1 >= paid without info >= no early search` when tau=0, physical future draw conservation, and eligibility bounds.
- [Regression](reproduce.py) tests three exogenous Prize outcomes, three denial weights (0,10,100) and five early source costs (0,0.0001,0.001,0.01,0.1), a total of **45** configurations. It verifies that higher tau cannot increase use of early search or its incremental optimized benefit.
- [Independent physical cards](monte_carlo.py) deal a Basic-valid 60-card opponent deck and original six Prizes, make two prelock draws, discard a real U+2F before Item lock, perform an empty-result deck search and shuffle, draw one reply card and play a physically held Judge or Ace Trainer. Independent 200,000-trial scenarios compare the post-reset X-recovery frequency to exact conditioned Prize-X card counts and full-deck sizes.
- [GitHub Actions run 38134590567 passed](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38134590567).

This is still a tightly controlled exact action model. The early source policy is granted knowledge of which exogenous r outcome will be realized, even though it cannot know Beheeyem's later tutor-use route or its own later draw; removing that anticipatory conditioning is a priority next extension. The extra tau cost is arbitrary and should eventually derive from real opportunity costs, subsequent Item utility, usable discard options, and board/attacker requirements. Only one Ultra Ball is considered and it chooses zero target; in real play finding a Pokémon may be strategically valuable. The opponent remains assumed to have no other Item/search pre-lock effects or hand-size perturbations; X itself is hypothetical.

The core methodological contribution is a physically conserved separation between **payable source incidence**, **information learned**, **deck-material side effects**, and **whether spending the source is optimal at the correct earlier decision time**.
