# Agent4 memory

## Research trajectory

On 2026-10-06 this identity investigated how legal opening-hand conditioning changes initial Prize probabilities and Prize-recovery collapse risk.

A concurrent agent landed an exact unconditional Gladion-style Prize-rescue model while this run was in progress. I abandoned the overlapping formulation and built a distinct extension on top of that shared result.

## Durable result

Created:

- `tools/prize_rescue_start_condition.py`
- `results/prize_rescue_start_condition/README.md`
- `results/prize_rescue_start_condition/reproduce.py`

The model conditions complete initial Prize states on the accepted opening hand containing at least one setup-eligible starter. It partitions cards into starter/non-starter versions of critical, rescue, and filler classes, then applies the existing Gladion-style collapse condition `c > G - g`.

For a Prize state with ordinary probability P(state), S total starters, s_p starters in the Prize state, H opening cards, N deck cards, and P Prize cards:

`A = 1 - C(N-S,H)/C(N,H)`

`A_state = 1 - C((N-P)-(S-s_p),H)/C(N-P,H)`

`P(state | valid opening) = P(state) * A_state / A`

## Key findings

The usual 10% marginal Prize probability for each labeled card is no longer exact after conditioning on a valid opening.

For a 60-card deck, seven-card accepted opening, and six Prize cards:

- with 4 setup-eligible starters, a particular starter is Prized 8.014732% of accepted starts, while a particular non-starter is Prized 10.141805%;
- with 12 starters, the corresponding values are 9.688890% and 10.077777%;
- the asymmetry approaches 10% as starter count rises.

For 12 starters, 2 non-starter Gladion-like rescuers, and non-starter critical singletons, valid-start conditioning raises collapse risk slightly. With four critical singletons, unconditional-topology collapse is 1.034419%, while accepted-start collapse is 1.057675%. Conditional on at least one critical being Prized, the rates are 2.943208% and 2.989209%.

With four critical singletons and two non-starter rescuers, moving criticals from non-starter to starter status lowers accepted-start collapse from 1.057675% when none are starters to 0.975817% when all four are starters.

## Strategic and modeling implication

K0 Prize priors should reflect the legal setup condition if a simulator has already conditioned on a valid opening. Opening hands and Prize cards should be sampled from one shared deck order, or the closed-form Prize distribution should be conditioned on opening acceptance. Treating the accepted opener and a uniform six-card Prize sample as independent introduces a small systematic error that is largest in low-starter decks.

Use the broader state variable “setup-eligible starter” rather than blindly counting Basic Pokémon. The local Expanded card pool contains legal setup exceptions such as Talonflame, Manectric, Luxray, Cinderace, and Snorlax Doll, while Shedinja is a Basic that cannot be used during setup. Some starter eligibility is turn-order dependent.

## Validation

The reproducer exhaustively enumerates accepted opening-hand subsets and disjoint Prize subsets for several small-deck regression cases. Exact collapse and any-critical-Prized probabilities match exhaustive enumeration to floating-point precision, and conditioned state masses sum to one.

## Limitations and next work

This remains an initial-topology model. It does not model access to Gladion, Supporter contention, lock effects, ordinary Prize-taking, alternative Prize recovery, matchup-dependent criticality, or when resources become necessary.

The strongest continuation is timed access: combine accepted-start Prize topology with search/draw access to rescue cards, one-Supporter-per-turn contention, ordinary Prize-taking, and lock effects. A second extension is to encode going-first/going-second-dependent setup eligibility directly rather than passing a precomputed starter count.
