# Aichi starting-Active named discard pressure

## Question

The Aichi starting-Active studies already show that two non-Jirachi Active
policies have the same modeled first-turn endpoint reachability while changing
the number and robustness of Guzma & Hala discard payments.

This result asks a more card-specific question: **which names actually become
unavoidable discard material, and which names merely enter or leave the set of
possible payments when Bunnelby is chosen Active?**

The distinction matters because the earlier singleton-floor statistic only asks
whether *some* feasible payment can avoid singletons. It does not identify a
singleton that appears in *every* feasible payment.

## Method

The sample matches the earlier Active-discard studies:

- 100,000 accepted openings;
- fixed seed 20261007;
- Jirachi absent;
- Bunnelby plus another Basic in the opening;
- existing non-Bunnelby-first Active heuristic compared with Bunnelby-first;
- only states where both policies require and can execute a successful
  Guzma & Hala route for the same endpoint.

For each endpoint-preserving family of card-name discard pairs:

- a **discardable name** appears in at least one feasible pair;
- a **forced name** appears in every feasible pair;
- a **forced singleton** is a forced name whose deck count is one;
- **newly exposed** means discardable under Bunnelby-first but not under the
  existing Active policy;
- **newly protected** means discardable under the existing policy but not under
  Bunnelby-first.

The implementation is `tools/aichi_named_discard_pressure.py`.

## Main result: singleton floors rarely mean forced singleton loss

| Endpoint | Comparable G&H states | Existing: states with forced singleton | Bunnelby-first: states with forced singleton |
| --- | ---: | ---: | ---: |
| core | 10,343 | 0 | 0 |
| Pidgeot | 9,586 | 0 | 0 |
| Stoutland | 7,947 | 0 | 0 |
| dual Stage 2 | 6,936 | 0 | 0 |
| Item lock | 9,578 | 0 | 0 |
| Item lock + Pidgeot | 5,384 | 1 | 0 |
| Item lock + Stoutland | 4,484 | 0 | 0 |

Across the 100,000-state sample, the only forced-singleton event occurs in one
Item-lock + Pidgeot state under the existing Active policy. That is
0.018574% of the 5,384 comparable states for that endpoint. Bunnelby-first has
zero forced-singleton states for every endpoint.

This sharply qualifies the earlier singleton-floor proxy. A feasible family can
have a minimum payment containing one or more singleton cards while still having
other payments that use different singletons. The minimum singleton count
therefore measures the cheapest singleton burden of one payment. It does not
measure whether a particular singleton must be sacrificed.

## Concrete forced-singleton witness

The unique sampled Item-lock + Pidgeot event had:

- opening: TM: Evolution, Tag Call, Lillipup, Budew, Mr. Mime, Bunnelby, Oddish;
- Prizes: Bunnelby, Artazon, Artazon, Gloom, Plumeria, TM: Evolution;
- draw: Pidgey;
- existing Active: Lillipup;
- Bunnelby-first Active: Bunnelby.

Under the existing policy the only endpoint-preserving G&H payment is
`Budew + Mr. Mime`, so both singleton names are forced.

Under Bunnelby-first the feasible family becomes:

- `Budew + Lillipup`;
- `Budew + Mr. Mime`;
- `Lillipup + Mr. Mime`.

No singleton name appears in every pair. The change in Active position therefore
removes a genuine two-singleton bottleneck in this state.

## The dominant effect is exposure geometry

Bunnelby-first mechanically removes the Active Bunnelby from the discard pool.
The number of comparable states where the name Bunnelby is newly protected is:

| Endpoint | Bunnelby newly protected | Share of comparable states |
| --- | ---: | ---: |
| core | 8,500 | 82.1812% |
| Pidgeot | 7,301 | 76.1632% |
| Stoutland | 6,034 | 75.9280% |
| dual Stage 2 | 5,353 | 77.1770% |
| Item lock | 3,136 | 32.7417% |
| Item lock + Pidgeot | 2,705 | 50.2415% |
| Item lock + Stoutland | 2,280 | 50.8475% |

The lower Item-lock-only share is expected from endpoint geometry: Bunnelby can
remain a feasible discard name under the existing policy more often when the
line has enough alternative Bunnelby access.

At the same time, Bunnelby-first returns the prior Active Basic to hand, making
that name newly discardable in many states. The most frequent newly exposed
names are endpoint-dependent:

| Endpoint | Most frequent newly exposed names |
| --- | --- |
| core | Pidgey 1,816; Lillipup 1,759; Oddish 1,680 |
| Pidgeot | Lillipup 1,625; Oddish 1,546; Pidgey 1,464 |
| Stoutland | Pidgey 1,383; Oddish 1,304; Lillipup 1,188 |
| dual Stage 2 | Oddish 1,086; Pidgey 1,007; Lillipup 975 |
| Item lock | Pidgey 1,683; Lillipup 1,635; Oddish 1,360 |
| Item lock + Pidgeot | Lillipup 435; Pidgey 250; Mr. Mime 248 |
| Item lock + Stoutland | Pidgey 378; Lillipup 227; Girafarig 213 |

For simple endpoints, choosing Bunnelby Active often trades away access to
discarding Bunnelby while adding the former Active Basic to the payment surface.
For combined endpoints, the former Active may itself be required for the board,
so the exposure effect becomes much narrower.

## Interpretation

The Active-choice effect is mostly **option-set reshaping**, not mandatory loss
of named singleton resources.

This helps separate three related discard concepts:

1. pair count measures how many payments exist;
2. protection cut measures how many names or physical cards must become UDP
   before every payment disappears;
3. forced-name pressure identifies resources already present in every payment.

The Aichi sample shows that these quantities can tell different stories.
Bunnelby-first can materially change pair count and robustness while leaving
forced-singleton pressure at zero.

Strategically, this means a DCI-aware planner should score the *set of available
payments* and the continuation value of the cards exposed by an Active choice.
A scalar penalty based only on whether a feasible pair contains a singleton can
overstate actual singleton sacrifice.

## Validation

A local reconstruction of the repository's exact state generator and
`route_flex` logic reproduced the published 100,000-state baseline exactly:

- 16,905 policy-difference openings;
- every comparable-state count;
- every mean feasible-pair count reported in
  `results/aichi_active_discard_flexibility/`.

The named-pressure analysis then ran on the same fixed seed and state sequence.
The committed tool is deterministic and can be rerun directly with Python.

## Limitations

This is still a local first-turn resource analysis. It does not assign
matchup-specific DCI, model recovery, propagate the surviving hand into later
turns, or value the board consequences of placing a particular Basic Active.

"Forced by name" treats duplicate copies as interchangeable and asks whether a
name occurs in every feasible payment. The existing physical-copy robustness
result remains the appropriate companion when individual copies matter.

The sample is tied to the published Aichi Vileplume list and the current
first-turn ALS model. It supports a representation claim about discard pressure,
not a universal recommendation to start Bunnelby.

## Reproduction

- tool: `tools/aichi_named_discard_pressure.py`
- reproducer: `results/aichi_named_discard_pressure/reproduce.py`
- trials: 100,000
- seed: 20261007
