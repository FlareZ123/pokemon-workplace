# Orthogonal gust restrictions make Serena and Counter Catcher incomparable

## Question

Suppose a paper Expanded deck already has one Boss's Orders and must decide
between a second gust resource: Serena or Counter Catcher. Serena targets only
opposing Pokemon V in its gust mode, while Counter Catcher chooses any opposing
Benched Pokemon but only when the player has more Prize cards remaining than
the opponent. Which card adds more tactical value?

This study integrates the [typed Serena target model](../target_restricted_gust_minimax/)
with the [Prize-gated Counter Catcher model](../counter_catcher_prize_timing/),
using exactly the same bounded endgame geometry.

## Model and caveats

Opponent Pokemon have public types N1/N2/N3 (non-V, worth 1/2/3 Prizes) or
V2/V3 (Pokemon V-family, worth 2/3). A three-Prize N3 can represent a
TAG TEAM Pokemon-GX. There are 2..6 opponent Pokemon and at least six
total potentially obtainable Prizes. All are single-attack KOs, and the
defender selects each replacement Active adversarially.

The player begins with six Prize cards remaining. The opponent has a fixed
remaining count of 1..5, used to evaluate Counter Catcher's exact
`own_remaining > opponent_remaining` permission after each KO.

Compare initially available gust inventories:

- Boss + Boss: unrestricted upper benchmark.
- Boss + Serena: the second gust can target only Benched V2/V3.
- Boss + Counter Catcher: the second gust can target any Bench occupant
  while its Prize inequality permits.

All cards are assumed to be available when their represented gust action is
needed. Boss and Serena are both Supporters in real play; the model uses at
most one meaningful gust per attack turn, so these two cards never need to
be played on the same turn. Counter is an Item, whose possible same-turn
synergy with another Supporter is outside this experiment. The Supporter and
Item lock restrictions, Serena's alternative draw mode, discard costs, and
the opponent's changing Prize count are also excluded.

This is a structural 1,212-board census, rather than a real-game frequency
distribution or an unconditional card ranking.

## Census: which second card wins?

For each of the 1,212 typed boards and five opposing Prize counts, compute
the exact adversarial-promotion minimum number of attacks to win.

| Opponent Prizes remaining | Boss + Counter faster | Boss + Serena faster | Equal |
| ---: | ---: | ---: | ---: |
| 1 | 126 | 0 | 1,086 |
| 2 | 126 | 0 | 1,086 |
| 3 | 126 | 0 | 1,086 |
| 4 | **114** | **32** | 1,066 |
| 5 | **114** | **32** | 1,066 |

At opponent counts 1..3, Counter Catcher's timing gate imposes no loss
relative to Boss + Boss in this board family. Serena can be worse where
crucial targets are non-V.

At opponent counts 4..5, the two choices are **strictly incomparable**:
114 board classes favor Boss + Counter, while another 32 favor
Boss + Serena. The total physical target type and Prize-threshold geometry
jointly determine the ordering.

Distribution of `attacks(Boss + Counter) - attacks(Boss + Serena)`:

| Opponent Prizes | -2 attacks | -1 attack | No difference | +1 attack |
| ---: | ---: | ---: | ---: | ---: |
| 1..3 (each) | 10 | 116 | 1,086 | 0 |
| 4..5 (each) | 10 | 104 | 1,066 | 32 |

The total attack counts over all 1,212 boards are 2,946 for Boss + Boss,
3,082 for Boss + Serena, and either 2,946 (opponent Prizes 1..3) or 2,990
(opponent Prizes 4..5) for Boss + Counter. These totals are unweighted
structural sums and cannot be interpreted as expected tournament turns.

## Witness 1: Counter beats Serena when the target type is wrong

Opponent has four Prizes left. Its Active is N1 (one Prize) and Bench has
two N3 (three-Prize, non-V) Pokemon.

- Boss + Counter takes the two Benched N3 for **six Prizes in two attacks**:
  Counter is used first and Boss remains available.
- Boss + Serena needs **three attacks** against adversarial promotion:
  Serena cannot choose either N3.

There are no V-family targets on this board; the difference is pure target
eligibility, with the Counter threshold still open for its first use.

## Witness 2: Serena beats Counter after the Prize gate expires

Opponent has four Prizes left. Its Active is N2 (two Prizes) and its Bench
has N1 / N2 / V2 (one / two / two Prizes).

- The optimal play with Boss + Serena takes the natural Active N2 KO first,
  then uses Boss and Serena on the two remaining two-Prize Bench targets.
  **Three attacks** take six Prizes.
- Taking the natural first KO reduces our Prize count from six to four,
  tying the opponent. Counter Catcher is now ineligible, leaving only one
  unconditional Boss. A best-defending promotion forces **four attacks**
  with Boss + Counter.

The opponent has a V-family target Serena can choose, precisely when the
Counter resource cannot be used.

This is a pure deadline-versus-target-scope reversal. It establishes that
neither card's gust mode globally dominates the other's at these Prize counts
under the stated assumptions.

## Why a single gust metric fails

Serena's target scope and Counter's Prize eligibility act on different
state dimensions. A one-number `gust power` rating cannot preserve their
relative ordering across all board states. Useful tactical evaluation must
track *both* the eligible targets and the remaining execution window,
including the defending player's next-Active choice.

This comparison also shows why a search graph that treats both as interchangeable
gust nodes can overestimate the expected path to a six-Prize win.

## Reproduction and verification

- `tools/gust_source_incomparability.py` carries both restrictions in one
  finite-state minimax.
- `results/gust_source_incomparability/reproduce.py` independently checks
  victory feasibility at fixed attack deadlines with all defender promotions.
- The regression covers **18,180 initial board/inventory/opponent-Prize
  scenarios** (1,212 boards × three inventories × five Prize counts).
- It additionally cross-checks Boss + Serena against the typed-only model,
  non-V cases against the previous Boss + Counter solver, all aggregate
  distributions, and the two opposite-direction witnesses.

## Next question

A more realistic card choice would include Serena's **draw mode** and the
different Item/Supporter action budgets. A draw or discard effect may be
valuable even when Serena's gust target set is empty. The exact comparison
should also account for opponent Prize changes, locks, search paths,
discard payment, target HP, and actual matchups.
