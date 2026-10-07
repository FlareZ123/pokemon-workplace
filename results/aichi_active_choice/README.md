# Aichi Vileplume starting-Active choice

## Question

Does the starting Active choice materially change first-turn reachability of the
named Aichi Vileplume ALS endpoints in the current simulator?

The prior planner used a simple heuristic: choose Jirachi Active if it is in the
accepted opening hand; otherwise choose the first non-Bunnelby Basic if one
exists; otherwise choose Bunnelby. That heuristic was inherited rather than
justified.

## Timing constraint

Starting Active selection happens during setup, before Prize cards are set and
before the first-turn draw. A real policy therefore cannot condition its Active
choice on the sampled Prize configuration, first-turn draw, or later deck
information.

This result compares two legal opening-hand-only policies and also uses an
information-privileged per-endpoint oracle only as an upper bound.

## Methods

tools/aichi_active_choice.py samples exactly the same accepted opening, Prize
cards, first-turn draw, and Stellar Wish top-five window for every Active choice.

It compares the existing Jirachi-first planner heuristic, a Jirachi-first then
Bunnelby-first heuristic, and an endpoint-specific oracle allowed to choose any
Basic actually present in the opening after seeing the full sampled state.

The oracle is deliberately stronger than a legal setup policy. If even this
oracle cannot improve an endpoint, hidden downstream information is not hiding
an Active-choice gain inside the current model.

tools/aichi_active_invariance.py then compares every distinct opening Basic
state by state. It separates openings with Jirachi from multi-Basic openings
without Jirachi.

The exact fraction of accepted seven-card openings where the two legal
heuristics differ is 17.0310317737%. The numerator requires no Jirachi, at
least one of the two Bunnelby, and at least one of the other eleven ordinary
Basics. The denominator conditions on the 14-Basic list producing an accepted
opening.

## Result 1: endpoint reachability is unchanged

A 200,000-state paired run with seed 20261007 produced:

| Endpoint | Existing heuristic | Bunnelby-first | Hidden-state oracle |
| --- | ---: | ---: | ---: |
| core | 70.6515% | 70.6515% | 70.6515% |
| Pidgeot | 60.1970% | 60.1970% | 60.1970% |
| Stoutland | 49.2450% | 49.2450% | 49.2450% |
| dual Stage 2 | 42.4150% | 42.4150% | 42.4150% |
| Item lock | 36.7480% | 36.7480% | 36.7480% |
| Item lock + Pidgeot | 23.8485% | 23.8485% | 23.8485% |
| Item lock + Stoutland | 19.6740% | 19.6740% | 19.6740% |

The hidden-state oracle gained exactly zero successes over the existing
heuristic on every endpoint in this run.

## Result 2: non-Jirachi Active identity is statewise invariant in the audit

The 100,000-state invariance run contained 48,240 accepted openings with at
least two distinct Basic choices and no Jirachi, plus 10,662 accepted openings
where Jirachi competed with at least one other Basic.

Across the 48,240 non-Jirachi multi-Basic states, zero sampled states had an
endpoint disagreement between any starting-Basic choices, for all seven
endpoints.

This is stronger than the aggregate equality above. Within the sampled support,
choosing Bunnelby, Pidgey, Oddish, Lillipup, or a utility Basic changed physical
setup position but did not change immediate named-endpoint feasibility under the
current planner.

## Result 3: Jirachi is weakly dominant for these endpoints in the audit

When Jirachi competed with another Basic, choosing Jirachi produced endpoint
gains and no sampled losses:

| Endpoint | Jirachi-only gains | Share of 10,662 Jirachi-choice states | Jirachi losses |
| --- | ---: | ---: | ---: |
| core | 2,148 | 20.1463% | 0 |
| Pidgeot | 1,841 | 17.2669% | 0 |
| Stoutland | 1,457 | 13.6654% | 0 |
| dual Stage 2 | 1,255 | 11.7708% | 0 |
| Item lock | 1,186 | 11.1236% | 0 |
| Item lock + Pidgeot | 745 | 6.9874% | 0 |
| Item lock + Stoutland | 618 | 5.7963% | 0 |

This supports the planner's current Jirachi-first rule for immediate ALS
feasibility.

## Why the negative result is plausible

The current Aichi planner explicitly normalizes the two Bunnelby geometries. If
Bunnelby starts Active, Jet Energy can be attached to it and still provides the
Colorless Energy needed to attack. If another Basic starts Active, Bunnelby is
established before Jet Energy is attached; Jet promotes Bunnelby and the former
Active becomes a Benched resource.

The endpoint Basic allocator adds the Active Basic back into the pool of
available setup Basics. Guzma & Hala discard pairs are exhaustively enumerated,
so the planner can preserve whichever immediate pieces are needed whenever a
viable pair exists.

Jirachi is different because starting it Active enables Stellar Wish. That adds
real access without removing any modeled endpoint capability, explaining the
one-sided Jirachi result.

## Interpretation

For this simulator and these immediate endpoints, starting-Active selection is
not the missing policy variable previously suspected. The existing
Jirachi-first heuristic already reaches the sampled endpoint ceiling, and
non-Jirachi starting Basics are interchangeable for endpoint feasibility.

This is a useful negative result because it prevents spending optimization
effort on an apparently important setup choice that the current representation
already collapses.

It does not show that starting Active is strategically irrelevant in real
games. The current endpoint model does not value future retreat or promotion
requirements, which utility Pokemon occupies the Bench, opponent gust or
targeting, damage and Prize exposure, later Active-dependent locks,
matchup-specific preservation of singleton Basics, graded DCI, future value of
Guzma & Hala discards, or multi-turn board geometry. Those omitted effects can
break the observed invariance.

## Reproduction

Primary code:

- tools/aichi_active_choice.py
- tools/aichi_active_invariance.py
- results/aichi_active_choice/reproduce.py

CI:

- .github/workflows/validate-aichi-active-choice.yml
- 200,000-state paired run: workflow run 37583358295
- paired run plus 100,000-state invariance audit: workflow run 37583757122

The fixed seed is 20261007.
