# Prize-informed one-output search across duplicate target families

The [single-target search option model](search_choice_notes.md)
assumed that every possible target was a singleton. Competitive decks
often play several copies of one preferred resource, alongside a
different fallback card.

This extension treats the candidate targets as ranked families, with
copy counts `n_i` and utilities `v_i` that satisfy

    v_1 >= v_2 >= ... >= v_k >= 0.

All family copies are assumed absent from the currently held hand.
There are M unseen physical card positions including P unknown
Prize cards. A usable one-output search can fetch a card from the first
available highest-value family after looking through the deck.

## Exact valuation

Let

    Q(t) = C(M-t,P-t) / C(M,P)

be the probability that a particular named set of t distinct
unseen cards is entirely Prized. For t=0, Q(0)=1.

Let C_i be the number of physical cards in families 1..i.
Then

    V_fixed = v_1 * [1 - Q(n_1)]

and

    V_adaptive =
      sum_i v_i * [Q(C_(i-1)) - Q(C_i)].

The term for family i is the exact probability that all higher-ranked
families are unavailable from the deck and at least one copy of family
i remains searchable. The formula reduces to the singleton analysis
when all n_i equal one. It also applies directly to multi-copy
fall-back decks if all model assumptions are met.

## One-card slot swap example

Take M=53 unseen cards after a seven-card opening in a 60-card game,
and P=6 Prizes. The preferred A resource has value 1, the different
B fallback has value 0.6.

| Two physical target-card slots | Expected best available search output |
| --- | ---: |
| A singleton and B singleton | 0.948185776 |
| Two copies of A | 0.989114659 |

The duplication increases expected immediate retrieval value by
0.040928882 units in this specialized situation.

The exact advantage is

    (1-0.6) * (6/53) * (47/52) = 0.040928882.

If there are already two A copies and a B singleton, the additional
benefit attributable to B as a lower-ranked contingency is only
0.006018953 normalized units.

The result concerns one immediate choice of target from the deck.
Different target identities can possess distinct later-matchup,
tactical, engine or alternate-channel value. A B target with tactical
access value beyond the scalar payoff may be strategically preferable
to duplicate A, even if it is inferior in this narrow lookup value
calculation. A copied A could also be in hand or Prized differently
in actual games.

## Verification

[tools/opponent_bonus_search_family_value.py](../../tools/opponent_bonus_search_family_value.py)
implements the complete exact rational expression. The
[reproducer](search_family_reproduce.py) enumerates all physical Prize
subsets in small decks, independently computes the best retrievable
value and fixed-choice value, checks equivalence to the prior
singleton model and validates the numerical example.
The [shared CI](../../.github/workflows/validate-opponent-bonus-assembly.yml)
runs this as an additional exact test.
