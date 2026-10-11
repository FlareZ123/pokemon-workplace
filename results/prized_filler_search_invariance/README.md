# Prize-invariant access after searching away predetermined non-targets

## Theorem

Consider an initially unseen pool of `U` physically distinct cards.
One is a desired target `T`. Another `c` named cards are known
non-target search sources. Exactly `P` cards are put into the initial
Prize set uniformly, and the player subsequently searches for **every
one of the c named cards that remains in the deck**, removing each
such source from the searchable deck.

After those searches, the player observes `s` uniformly sampled
cards from the remaining deck. Assume

`1 <= s <= U - c - P`.

Then the **unconditional probability** that the observed cards include
`T` is exactly

`Pr(T observed) = s / (U - c)`,

**independent of P** over the feasible range.

This formula assumes the named search actions can be executed and
their material and opportunity costs have already been paid. Named
sources are different from the target and are never put back into the
deck before observation. If some named source was Prized, that source
is unavailable for search and is simply not removed. The later
observation is over a properly shuffled deck.

## Proof

Set `M = U - c`, the number of cards excluding the c named
sources. Condition on exactly `j` named sources being Prized.
Then `P-j` cards are uniformly Prized among those `M`.
There are `M-P+j` unprized non-source cards left in the deck
after the remaining named sources have been removed.

The target survives the Prize allocation with probability
`(M-P+j)/M`. Conditional on survival, a uniform `s`-card
observation hits the target with probability `s/(M-P+j)`.
Multiplying gives `s/M` in **every feasible stratum j**.
Averaging over how many named sources were Prized therefore
remains `s/M`.

The condition `s <= M-P` ensures the deck always contains at
least `s` unmarked cards, even when no named source is Prized.
Beyond that boundary, sampling may exhaust the deck and a
different, saturated expression is required.

## Stronger statement: the entire observation subset is uniform

The single-target theorem is a corollary of a stronger result.
After removing every available named non-target source, the
**entire unordered `s`-card observation** is a uniform subset
of the `M=U-c` originally unseen non-source physical cards,
regardless of the uniform Prize count `P`, provided
`s<=M-P` and the search/removal policy does not depend on
hidden identities among those non-source cards.

For any particular subset `A` of `s` non-source cards,
condition on `j` of the named sources being Prized and
write `r=P-j`. The Prizes select `r` among `M` uniformly.
The probability that none of the `s` selected cards is
Prized equals `C(M-s,r)/C(M,r)`. Conditional on their
survival, the remaining deck has `M-r` cards and the
probability that the later uniform observation is exactly
`A` is `1/C(M-r,s)`. Multiplying gives

`Pr(observed exactly A | j)=1/C(M,s)`.

This does not depend on `j`, so averaging over all
possible Prized-source counts gives the same expression.
Consequently **any payoff depending only on the observed
card identities** can be averaged against a uniform
`s`-subset of the `U-c` non-source pool, without
simulating the Prize allocation.

If `q` of the non-source cards are marked desirable
targets, the exact probability of seeing `x` among
the `s` observations is

`C(q,x) C(M-q,s-x) / C(M,s)`.

For two disjoint named groups, with `t` Ticket and
`m` Map cards, the probability of **seeing at least
one member of each group** is

`1 - [C(M-t,s)+C(M-m,s)-C(M-t-m,s)]/C(M,s)`.

For example, `M=49,s=5,t=2,m=1` gives exactly
`65/3948` for *visibility of both groups*,
independent of the feasible Prize count. Note that
Jirachi's Stellar Wish obtains at most **one Trainer
card** from the five observed cards, so this
two-group *visibility* event is not simultaneous
two-card acquisition.

The expanded SFT enumerates entire physical top-`s`
sets across small-deck Prize worlds and checks that
each non-source subset has probability exactly
`1/C(M,s)`. It independently tests the target-count
hypergeometric law and the two-disjoint-groups
inclusion-exclusion formula.

The property can fail when sources are removed
selectively as a function of hidden non-source
information, after changing the deck via other
non-exchangeable operations, or when too few cards
remain for the requested observation. K1 policies
that adapt to hidden Prize locations require a
separate calculation.

## Concrete Guzma & Hala application

The source-grounded [Aichi omitted-action example](../gnh_optional_paid_duplicate_search/)
holds TM: Evolution and Jet Energy, with a second copy of each
possibly hidden in the deck, plus one Artazon and a Ticket-role
TechSlot. Assume it can execute the source searches and that
two otherwise expendable cards are available for G&H's on-play cost.

A twelve-card unseen pool has one Ticket, one Artazon, one spare
TM: Evolution, one spare Jet Energy, and eight other cards. Its
Prize count may be any `P` from zero through four under a
five-card observation.

- G&H without the optional two-card payment searches Artazon when
  it is available, removing one predetermined non-target source
  (`c=1`). Expected Ticket access is **5/11**.
- G&H with the optional payment searches Artazon plus both spare
  TM and Jet when each is available (`c=3`). Expected access is
  **5/9**.

The exact unconditional access difference is **10/99** in this
deliberately restricted, cost-agnostic model, even though the set
of available search outputs varies with the random Prize
configuration. It is a conditional draw-access geometry result
rather than a deck win-rate estimate.

The player can commit to the paid line without knowing which
named sources were Prized: once the on-play cost is committed,
G&H's category-restricted search may obtain each currently
searchable named card. The discard decision must occur before
G&H's own first deck search, as established in the
[official payment timing audit](../gnh_on_play_discard_timing/).
A prior Tag Call search can change the information available
before choosing whether to pay, though Tag Call also changes the
physical card pool.

## Reproduction and limits

Source: [tools/prized_filler_search_invariance.py](../../tools/prized_filler_search_invariance.py).
SFT: [reproduce.py](reproduce.py).

The SFT checks exact stratified hypergeometric probabilities, all
physical Prize subsets, and an independent small-deck oracle that
enumerates literal `s`-card observations. It checks the
5/11 and 5/9 Aichi witness for five Prize counts.

Important limits: the formula says nothing about a player's
willingness to discard valuable Supporters, availability of
Tag Call or G&H, Bench and Active constraints, additional
stochastic deck shuffles, target cards in hand, or multiple
simultaneously required draw targets. For joint targets, card
identities and dependence become important again. In complete
games, these restrictions are essential.
