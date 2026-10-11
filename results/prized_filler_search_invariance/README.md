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
