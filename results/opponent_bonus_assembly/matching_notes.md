# Multi-requirement assembly by physical one-use matching

The earlier two-demand [capacity correction](flexible_capacity_notes.md) is
a special case of a more general resource-allocation problem.

## Exact physical model

A card class specifies its physical copy count, the subset of strategic
requirements it may satisfy, and whether those copies count as ordinary
Basic starting Pokémon. Each card may be assigned to at most **one**
requirement. All requirements must receive separate physical cards.

For a particular sample, form a bipartite graph between the physical cards
and required strategic goals. Hall's marriage theorem says a complete
assignment exists exactly when, for every nonempty subset S of goals, the
number of observed physical cards eligible for at least one goal in S is at
least the cardinality of S. The
[matching kernel](../../tools/opponent_bonus_matching.py) tests every subset.

The probability engine marginalizes Prize positions and avoids enumerating
individual ordered cards. Let H be opening size, m the number of bonus draws,
s=H+m and B the total ordinary Basic starters. An observed union of s cards,
with b observed Basics, has conditional probability

    P(union | valid Basic opening)
      = [C(s,H)-C(s-b,H)] / C(s,H)
        * P(union as uniform s-card sample)
        / [1-C(N-B,H)/C(N,H)].

The initial H-card opener, conditional on a fixed s-card union, is a
uniform H-subset of that union. The probability its opener contains a Basic
is exactly the first factor. Uniform Prize assignment makes the m later
bonus cards an exchangeable subset of the N-H cards excluded from the hand.
Grouped class-count vectors have uniform-sample mass

    product_j C(n_j,x_j) / C(N,s).

Summing these exact rational weights over the class-count vectors satisfying
Hall's condition yields the one-use assembly probability. The identical
enumeration using only group-presence conditions gives simultaneous
coverage and exactly reproduces the previous inclusion-exclusion kernel.

## Three independent requirements

Illustrative 60-card deck: seven-card opening, six Prizes, twelve unrelated
ordinary Basics, two cards each exclusive to goals A, B and C, two flexible
cards eligible for any single goal, and forty filler cards. The flexible
cards have output capacity one.

| Model of the same physical card pool | Joint completion in accepted opening |
| --- | ---: |
| Treat each flexible copy as simultaneously satisfying A, B and C | 21.438835% |
| Match each physical card to at most one distinct requirement | 2.451991% |
| Overstatement | 18.986843 percentage points |

This illustrates how assigning one flexible card to every available graph
edge can severely overestimate executable joint goals.

## Verification and limitations

[matching_reproduce.py](matching_reproduce.py) validates the general
implementation against an independent recursive search that assigns
labeled physical cards to distinct goals, with explicit enumeration of
accepted opening hands, Prize subsets, and bonus selections in two small
three-goal decks. It also proves the general Hall solution equals the
two-demand closed-form capacity correction, and its simultaneous variant
equals the earlier inclusion-exclusion model. The GitHub Actions workflow
runs all these tests.

Actual Expanded plays can be more constrained: a card's search target
may be Prized, it may consume a Supporter, require discards, or be denied
by a lock. Some effects also generate multiple outputs from one card, which
requires per-action output bundles or richer transition semantics rather
than assigning every card a universal capacity of one. This model isolates
physical one-output assignment under a well-defined legal-start condition.
