# Aichi starting-Active discard flexibility

## Question

The immediate Aichi ALS endpoints are invariant to non-Jirachi starting-Active
choice in the current planner. Does that make the choice strategically empty?

This follow-up asks a narrower AMR/DCI question: among states where the endpoint
still succeeds through Guzma & Hala, how many distinct discard pairs can support
the line, and how often must a feasible pair include singleton-deck cards?

## Scope

The analysis is restricted to accepted openings where Jirachi is absent,
Bunnelby is present, at least one other Basic is present, and the existing
heuristic and Bunnelby-first therefore choose different Actives.

The sampled frequency was 16,905 of 100,000 accepted openings. The exact
setup-conditioned probability of such a policy difference is 17.0310317737%.

For each named endpoint and each Active choice,
tools/aichi_active_discard_flexibility.py reproduces the current natural-route
and Guzma & Hala logic, then enumerates every distinct card-name pair that can
be discarded while preserving endpoint execution.

Two structural metrics are retained: feasible discard-pair count and the
minimum number of one-copy deck cards appearing in any feasible pair. These are
AMR/DCI proxies rather than strategic values for individual cards.

## Main result

Among states where both policies required and could execute the Guzma & Hala
route:

| Endpoint | Both-G&H states | Mean pairs, existing | Mean pairs, Bunnelby-first | Relative change |
| --- | ---: | ---: | ---: | ---: |
| core | 10,343 | 13.3028 | 14.0384 | +5.53% |
| Pidgeot | 9,586 | 12.9152 | 13.8368 | +7.14% |
| Stoutland | 7,947 | 12.8143 | 13.7573 | +7.36% |
| dual Stage 2 | 6,936 | 12.6929 | 12.8883 | +1.54% |
| Item lock | 9,578 | 10.7385 | 13.8101 | +28.60% |
| Item lock + Pidgeot | 5,384 | 10.6235 | 9.9277 | -6.55% |
| Item lock + Stoutland | 4,484 | 10.5629 | 9.9005 | -6.27% |

No sampled state changed from a natural route under one policy to a G&H route
under the other. The difference is inside the discard-option surface, not
headline reachability.

## Direction is endpoint-dependent

| Endpoint | Bunnelby-first more pairs | Bunnelby-first fewer pairs |
| --- | ---: | ---: |
| core | 1,991 | 321 |
| Pidgeot | 2,591 | 454 |
| Stoutland | 2,183 | 380 |
| dual Stage 2 | 1,182 | 929 |
| Item lock | 7,313 | 262 |
| Item lock + Pidgeot | 935 | 1,691 |
| Item lock + Stoutland | 812 | 1,413 |

For Item lock alone, protecting Bunnelby in the Active Spot often frees the
other opening Basic as an additional discard candidate. The endpoint needs only
Bunnelby plus Oddish, so many non-Oddish opening Basics are expendable from the
perspective of the immediate line.

For Item lock + Pidgeot or Item lock + Stoutland, the second evolution Basic is
also part of the endpoint. The existing non-Bunnelby Active choice can protect
one of those required Basics from the G&H discard pool. Moving Bunnelby Active
can put more endpoint-critical cards back into hand, reducing the number of
pairs that preserve the whole line.

## Singleton floor

| Endpoint | B-first lowers minimum singleton count | B-first raises minimum singleton count |
| --- | ---: | ---: |
| core | 56 | 222 |
| Pidgeot | 71 | 230 |
| Stoutland | 52 | 158 |
| dual Stage 2 | 38 | 166 |
| Item lock | 246 | 93 |
| Item lock + Pidgeot | 44 | 198 |
| Item lock + Stoutland | 37 | 138 |

Bunnelby-first usually exposes singleton resources slightly more often for the
non-Item-only endpoints, even when it increases raw pair count. Item lock alone
is the exception in this sample: Bunnelby-first both greatly expands pair count
and more often lowers the singleton floor.

Pair count alone is therefore not a complete discard-quality metric. More
endpoint-preserving pairs can coexist with worse preservation of scarce future
resources.

## Interpretation

For immediate named-endpoint feasibility, non-Jirachi Active identity was
sample-invariant. For discard flexibility and resource preservation, Active
identity matters and the preferred choice depends on the endpoint.

This is a concrete connector-cost example of why access should not be treated
as success. Two lines can reach the same board with equal probability while
having different opportunity costs in the hand they leave behind.

## Limitations

The singleton indicator is deliberately crude. A one-copy card can be useless
in one matchup and decisive in another, while a four-copy card can still be
strategically protected in a specific state.

The analysis does not assign DCI values, model future draws, score discarded
card identities by matchup, model recovery, or propagate the post-discard hand
into later turns.

A stronger continuation would replace the singleton proxy with state- and
matchup-dependent continuation value, or at minimum report discard-pair
composition by card role.

## Reproduction

- tool: tools/aichi_active_discard_flexibility.py
- workflow: .github/workflows/validate-aichi-active-discard-flexibility.yml
- fixed seed: 20261007
- trials: 100,000
- successful CI run: 37584064717
