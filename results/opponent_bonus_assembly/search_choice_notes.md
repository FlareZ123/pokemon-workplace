# Prize-aware selection while searching a deck

A flexible search such as Computer Search can select the best currently
searchable target **after inspecting the deck**. The physical Prize
cards are not visible before the first search (the project's K0 state),
but the player may infer them from which known singletons are absent
from the deck (K1). This creates a quantifiable selection advantage
over precommitting to a single target before inspection.

## Exact option value

Assume M physical cards are unseen after the opener and any bonus draws.
Exactly P of these are Prize cards. There are k distinct ranked singleton
targets among the M, with nonnegative values

    v_1 >= v_2 >= ... >= v_k.

All target identities are known to be absent from the hand. A currently
usable search source can retrieve exactly **one** target from the remaining
deck, and the searcher sees which targets remain before choosing.

The value of committing to the highest-value target in advance is

    V_fixed = v_1 * (M-P)/M.

Under adaptive deck inspection, target i is selected when every higher-value
target 1..(i-1) is Prized and target i is unprized. The exact probability
of that event is

    C(M-i, P-(i-1)) / C(M,P)

when i starts at 1. Therefore

    V_adaptive =
        sum_i v_i * C(M-i, P-i+1) / C(M,P).

The information-enabled option value is

    V_adaptive - V_fixed.

It is nonnegative when values are nonnegative. The source itself must
already be usable, and its search must permit every modeled target.

## Illustrative 60-card figures

Take an accepted seven-card opening, six Prize cards, and no subsequent
bonus draws, leaving M=53 unseen positions. The owner has a working
one-output search and knows that two singleton candidates A and B are not
already held. Assign A value 1 and B value 0.6.

| Search decision | Expected immediate target value |
| --- | ---: |
| Commit to A before examining the deck | 0.886792453 |
| Inspect deck and take the best available target | 0.948185776 |
| Value added by contingent selection | +0.061393324 |

The exact gain is

    0.6 * (6/53) * (47/52) = 0.061393324.

It comes entirely from the configurations where A is Prized and B remains
in the searchable deck. Adding a third singleton C valued at 0.3
raises the contingent-selection benefit to 0.064402800.

These utilities are illustrative and cannot be read as win-rate points.
They are conditional on already possessing a usable flexible search.
They do not account for search action cost, an opponent, tempo,
future turn value, or the strategic consequences of retrieving a lower
priority resource.

## Evidence

The exact core is
[tools/opponent_bonus_search_choice_value.py](../../tools/opponent_bonus_search_choice_value.py).
Its independent
[Prize-set enumerator](search_choice_reproduce.py) exhausts all Prize
configurations on small decks and checks rational agreement across
several target counts and payoffs. The bundled rulebook's Deck Search
section H establishes that the searcher can see the remaining deck.
The repository's human concepts document describes the K0/K1
transition and warns about connector domination: the best retrievable
target can differ materially from the globally most useful target.

In a more complete optimizer, the value of the chosen target would
depend on the rest of the board and hand, the opponent, Supporter
contention, and whether the other target can be accessed through
some independent channel. The result isolates the intrinsic option
value of target choice after deck inspection.
