# Secret Box's hidden-Prize payment is a nonanticipating decision

## Question

Secret Box requires the player to discard **three other cards** before searching the deck. On the first deck search, the player can infer hidden Prize composition, but that information arrives *after* committing the discard payment.

What is the cost of letting an optimizer incorrectly choose its Secret Box payment with advance knowledge of the Prize cards?

See tools/secret_box_k0_payment.py and results/secret_box_k0_payment/reproduce.py. The continuation uses the bounded Secret Box -> Guzma & Hala acquisition model from results/secret_box_gnh_tool_pipeline/.

## Exact finite hidden-state policy

The player has a known post-draw hand and a complete decklist. Of the **52 unseen cards** after an eight-card visible hand, six are randomly assigned to Prizes and the other 46 form the searchable deck.

For each admissible three-card Box payment p, define W(p,z)=1 when some permitted Box-first search and following Guzma & Hala action accomplishes the terminal package under hidden Prize composition z.

A clairvoyant optimizer incorrectly evaluates:

    K1 = sum_z Pr(z) max_p W(p,z)

The correctly nonanticipating payment policy evaluates:

    K0 = max_p sum_z Pr(z) W(p,z)

Search choices following the Box payment *can* depend on its revealed deck contents. The only common prior-world action is the initial three-card discard choice. K1 >= K0 is exact for this bounded model.

All six key searched categories (Item I, Tool A, Tool B, Guzma & Hala G, Stadium S, Special Energy E) are enumerated with hypergeometric integer weights. Prize allocations among protected and disposable filler cards are analytically marginalized. Fractions are exact rationals; no Monte Carlo is used.

## Concrete 60-card witness

Deck composition:

| Category | Count |
| --- | ---: |
| Secret Box | 1 |
| Immediately disposable cards D | 20 |
| Item I | 1 |
| Required Tool A | 2 |
| Required Tool B | 1 |
| Guzma & Hala G | 2 |
| Stadium S | 2 |
| Special Energy E | 1 |
| Protected remaining cards P, including eligible Basics | 30 |
| Total | **60** |

The visible hand after one turn-start draw, including Secret Box, contains Box + D,D,A,G,S,P,P. At least one P is an eligible Basic Pokémon from the accepted opening.

This leaves 52 unseen cards with exactly one remaining searchable copy of each key I,A,B,G,S,E; 46 others. Exactly six Prize cards are hidden.

The terminal acquisition goal is **A+B+S+E** in hand after Box and, if useful, Guzma & Hala. The Box-first line has permission to play one Supporter and no opposing lock.

| Payment information model | Exact success |
| --- | ---: |
| K1: payment may react to true hidden Prizes | **72.941623457894%** |
| K0: one discard choice before the first deck search | **66.208550523319%** |
| Clairvoyance overstatement | **6.733072934575 percentage points** |

Exact rational values:
- K1 = 32637/44744.
- K0 = 1925583/2908360.
- K1-K0 = 97911/1454180.

Three distinct fixed payment plans tie for K0 optimality: spend D+D+A, D+D+G, or D+D+S, leaving the other two of A/G/S in hand. The best selected payment succeeds on 66.2086% of hidden worlds, but across worlds a clairvoyant player can select whichever payment fits that world's surviving search copies.

**The gap is caused entirely by pre-search nonanticipation.** Once Box has been paid, each world is allowed its optimal sequence of typed Item/Tool/Supporter/Stadium output selections and any legal downstream two-card Guzma & Hala payment.

## Validation

A second evaluator enumerates individually labeled card copies, each exact possible Prize combination, literal three-card payment sets, typed Box outputs and downstream Guzma & Hala play. It independently computes the maximum over fixed payments and the average of per-world maxima.

The independent oracle agrees on **48 small-deck policy fixtures**, varying searchable Item/Stadium/Guzma & Hala counts, Item retention, and Supporter availability. The 60-card witness is asserted using exact rational arithmetic. The full multivariate-hypergeometric world-weight sum is checked against the binomial denominator.

## Limits and significance

This is a fixed *visible-hand*, fixed *Box-first* research witness, not the unconditional probability that a real deck achieves its first turn or wins. It does not include G&H-first play, alternative prior deck search that reveals Prizes, exact opponent lock, evolution, Stadium play, Tool attachment, or other search engines. A prior deck inspection would erase this particular information penalty because the true Prize composition would already be known when Box is paid.

The general modeling rule is to respect **when each action's information becomes available**. A card search may reveal the deck while still requiring irreversible payments before that observation. In optimization, a strategy is a policy contingent on observable history, rather than a collection of independent per-hidden-world best moves.

Next steps: measure the effect across actual accepted-opening distributions with physical Prize samples, allow first-search alternatives, and integrate other costs competing for the Box payment cards.
