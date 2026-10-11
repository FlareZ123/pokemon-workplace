# Declining the Supporter can reverse Prize-information value

## Motivation

The [opponent-weighted three-Supporter model](../supporter_opponent_weight_frontier/) required playing one of Iono, N, or Professor's Research. In real games a player can choose **not to use the Supporter**. That option preserves a useful card already in hand and may dominate an otherwise attractive draw action.

This extension makes **Pass** a fourth selectable action and re-evaluates the exact finite-action K0/K1 frontier. It is a controlled illustration of action cancellation and source opportunity costs, rather than a match-win prediction.

## Common endpoint and state

Our old deck contains D=46 cards, our P=6 remaining Prize cards are unrevealed, U=10 useful outs lie in these 52 unknown deck-plus-Prize cards, and our remaining old hand of H=5 cards includes R=1 known useful out. The opponent has 46 deck cards, six hidden remaining Prizes containing four unknown-zone outs, and an old hand of five including one known out.

Utility at weight lambda is **our probability of holding at least one target after the chosen action minus lambda times the opponent's probability of holding a target after their next normal draw**.

- Iono bottoms both hands and draws six on each side.
- N shuffles each hand into its player's deck and draws six.
- Professor's Research discards our hand and draws seven, leaving the opponent's hand alone.
- **Pass** uses no Supporter and preserves both old hands before the opponent's next normal draw. With the stipulated known out on each side, own and opponent readiness are both exactly one.

All assumptions from the earlier experiment about Supporter accessibility and excluded additional moves remain in place. Card text comes from paper-Expanded-scope prints Iono sv2-185, N bw3-92, and Professor's Research swsh1-178.

For this specific terminal payoff, **Pass dominates Research whenever our old hand already contains an interchangeable useful out**, because both leave the opponent's hand unchanged while passing guarantees own target retention. This says nothing about full-game card strength.

## Result: action cancellation moves the optimum

| Opponent-denial weight | Three forced Supporters: K1 information | Four options including Pass: K1 information |
| ---: | ---: | ---: |
| 0 | 0 pp | 0 pp |
| 0.1 | +0.085210477 pp | **0 pp** |
| 0.5 | +0.000162224 pp | **+1.109136964 pp** |
| 2 | 0 pp | 0 pp |

The **exact four-option global maximum** occurs at weight **374699/800316**, approximately **0.468188815418**, with information premium **207557493001/12375020344400** in probability units, or **+1.677229509323 percentage points**.

At that weight the K0-best actions **Iono and Pass tie**. If our own K1 deck search reveals the number K of outs remaining in our deck, the optimal adaptive choice is:

- **Pass for K=4 through K=8**.
- **Iono for K=9 or K=10**.

The new result has **38 exact candidate weight crossings**, including zero; all **37 intervening intervals** were checked for exact affine behavior. The earlier forced-three-option global maximum was +0.118469577 pp at weight approximately 0.101780177265. Introducing the freely available Pass option changes both the best objective and the observation premium, including its maximizing weight.

**Negative control:** If the old hand has R=0 known useful outs, Pass has zero own immediate target readiness while Research can draw seven and has the same opponent-readiness penalty. Research weakly dominates Pass. Five exact weight checks confirm that adding Pass then leaves the optimal fixed, optimal observed and observation-premium values unchanged.

## Reusable theoretical contribution

A new [generic rational weighted-action frontier](../../tools/action_information_weight_frontier.py) accepts finite states with exact priors and per-action intercepts and weight coefficients. It evaluates fixed and informed action envelopes, enumerates all rational pairwise crossing points and finds the global information-value maximum.

The global peak certification specifically requires **the weight coefficient of each action to be constant across hidden states**. If that coefficient itself changes with the hidden state, the information premium can grow without bound as weight increases; the engine rejects that unsupported global-peak extrapolation. Evaluation at a specified finite weight remains available for state-dependent coefficients.

The [four-option source model](../../tools/supporter_pass_option_frontier.py) composes this engine with previously verified card-text effects and opponent Prize marginalization.

## Validation

[The reproducer](reproduce.py) passes **2,787** exhaustive or seeded generic weighted-envelope configurations, checks the invalid state-dependent-cost counterexample, validates all 37 exact affine intervals, verifies the exact rational maximum and tests the R=0 negative control. The [Windows workflow](../../.github/workflows/validate-agent2-supporter-pass-option.yml) runs the script under Python 3.13.

The result conditions on target definitions, known hand contents and Supporter access. Actual game play includes attacks, abilities, extra searches, Supporter opportunity cost, Prize scoring and opponent decisions. This experiment identifies the sensitivity of an information-value claim to an omitted feasible action, and cautions against assigning intrinsic scalar value to learning deck composition before specifying the complete decision set.
