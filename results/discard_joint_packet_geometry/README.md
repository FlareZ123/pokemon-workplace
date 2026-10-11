# Typed discards change two-piece packet acquisition in ways target density misses

## Research question

A typical Beheeyem continuation needs at least one Beheeyem evolution card and at least one Triple Acceleration Energy (TAE) in the right zones, plus a legally mature board and valid actions. The detailed [packet recurrence solver](../beheeyem_packet_recurrence/) models the actual card movement, tutors, Prizes and Item locks. This smaller study isolates an exact structural component: **finding at least one card of each of two distinct required categories in one n-card draw**.

How does discarding three cards before a future reshuffle change that probability when the discard payment uses filler, one of the attackers, one TAE, or a combination?

## Exact two-category inclusion-exclusion

Suppose N future draw-population cards contain B cards of category B, T cards of distinct category T, and N-B-T filler cards. Draw n uniformly without replacement.

```text
P(B >= 1 AND T >= 1)
  = 1
    - C(N-B,n)/C(N,n)
    - C(N-T,n)/C(N,n)
    + C(N-B-T,n)/C(N,n).
```

If an earlier action discards m physical cards of which b are B and t are T, the new population is `(N-m,B-b,T-t)`, with `m-b-t` filler removed. The change is exactly the new inclusion-exclusion probability minus the original.

**Removing only filler weakly increases the joint packet-hit probability.** This follows by coupling the before/after draws to a common random permutation of all original cards and deleting m non-target fillers. The first n surviving cards contain at least as many B and T cards as the first n cards before deletion, for every permutation. Any event requiring at least one of each is preserved whenever it originally succeeded.

The guarantee fails when discards consume required components. Counts need to be tracked **by needed role**, since joint feasibility can collapse even as the total density of cards labeled "useful" increases.

## Practical-scale numerical example, B4/T4 in 53 future draw cards

The following probabilities describe **simultaneous access to both distinct types**, assuming a fixed draw quota and no search, paid tutor, Prize risk or board constraints.

| Draw quota | Baseline | Discard 3 filler | Discard 1 B + 2 filler | Discard 1 B + 1 T + 1 filler | Discard 2 B + 1 filler |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 4 | 6.170238% | **6.886670%** | 5.280069% | 4.047330% | 3.597916% |
| 6 | 13.655279% | **15.121096%** | 11.848201% | 9.279679% | 8.252758% |

At six draws, discarding three filler cards improves the chance of both pieces by **1.465817 percentage points**. Using one required packet copy as part of the same literal three-card payment instead leaves **11.848201%** joint acquisition, or **1.807079 points worse than baseline**. Losing one copy of each required type lowers it to **9.279679%**.

That is a 5.841417-percentage-point gap between spending three filler cards and spending one B, one T, and one filler for the same three-card payment. It provides a concrete example of how an action's discard targets can dominate its abstract deck-thinning benefit.

## Misleading aggregate "useful-card density"

Consider an exactly ten-card deck with one B, one T and eight filler cards. A two-card draw finds both pieces with probability **1/45 = 2.222222%**. Discard the unique B and five filler, leaving four cards: zero B, one T and three filler.

The aggregate density of B or T cards **increases** from 2/10 = 20% to 1/4 = 25%, yet the chance of drawing both components becomes **zero**, since B is no longer available. Thus even a strictly higher density of broadly tagged "relevant" cards can coexist with complete failure of a conjunctive objective.

This is a simple exact counterexample to evaluating an associativity or deck-thinning action using a single all-useful-cards concentration metric. A realistic optimizer needs to preserve required functional categories and the possibility of retrieving a missing component.

## Evidence and limitations

- [Exact two-category packet kernel](../../tools/discard_joint_packet_probability.py) computes inclusion-exclusion as Fractions with physically validated typed discard counts and verifies filler-only monotonicity.
- [Exhaustive independent regression](reproduce.py) checks **199,536** legal small configurations (N=3..20, B/T disjoint, m up to four, draws up to six) including **21,490** filler-only discard cases. It checks every probability lies within zero and one, the all-filler guarantee, and the aggregate-density counterexample.
- [Independent physical shuffle experiment](monte_carlo.py) constructs actual fifty-card post-discard populations with B/T/filler and tests three 200,000-trial outcomes (all-filler payment, one B discarded, one B plus one T discarded) against the exact six-card packet probability.
- [GitHub Actions run 38135211721 passed](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38135211721).

This study deliberately isolates raw n-card packet access. Actual Beheeyem Mysterious Noise cannot be modeled as an unrestricted n-card draw: it requires an evolution-ready Elgyem, legal TAE timing, attacks that shuffle Pokémon and attachments, possible tutor cost/payment, Prized copies, Item locks and opponent response actions. These important constraints remain in the specialized [recurrence](../beheeyem_packet_recurrence/) and its extensions.

## General insight

In card-search optimization, the event being maximized is often **conjunctive**. Its probability can fall when an apparently improved overall useful-card concentration hides the destruction of a necessary resource category. When modeling discard cost, distinguish removal of strategically disposable fillers, redundant targets and indispensable singleton resources; then value downstream reachable action sequences rather than a one-dimensional density.
