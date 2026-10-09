# Joint Gothitelle access with four physical core Basics by turn one

## Question

The prior [joint Quick Ball/Sky Field access result](../gothitelle_dual_use_joint_access/)
finds a 0.542350465% card-access probability under a supplied compatible
Bench state. How much does the event narrow if the player must also have
**four ordinary Basic Pokémon** available by turn one's end, to put one
in the Active Spot and three on the Bench alongside Gothita?

This exact refinement keeps the same 60-card population and timing.
Only **one** first-turn Quick Ball and one next-turn natural draw are
permitted. The Stadium/lock context and the two subsequent entrant
requirements from the existing physical witness are still supplied
externally.

- Model: [`tools/gothitelle_core_board_joint_access.py`](../../tools/gothitelle_core_board_joint_access.py)
- Labeled exhaustive SFT: [`reproduce.py`](reproduce.py)

## Action policy and three disjoint branches

The initial seven-card opener must contain an ordinary Basic Pokémon
to supply the non-Gothitelle Active. By the end of the first player's
turn, Quick Ball and Sky Field must both have appeared in the initial
hand or first natural draw. Quick Ball must discard Sky Field.

- **Board already ready:** At least four ordinary Basics and a Gothita
  are naturally present among the first eight observed cards. Quick Ball
  pays Sky Field and selects zero restricted-search targets.
- **Search a core Basic:** Gothita and exactly three ordinary Basics
  are naturally present. Quick Ball pays Sky Field and retrieves an
  unprized fourth ordinary Basic from the deck.
- **Search Gothita:** At least four ordinary Basics are naturally
  present but Gothita is absent. Quick Ball pays Sky Field and
  retrieves one unprized Gothita.

States requiring both missing Gothita and an additional core Basic
cannot be solved by the same single Quick Ball. All three branches
require access to Rare Candy and Gothitelle by the second-turn draw.
Search availability, physical deck reduction, and remaining target
Prizes are calculated jointly.

## Exact 60-card example

Same partition as the previous study: Gothita 3, Gothitelle 2,
Rare Candy 4, other opening-capable Basics 8, Quick Ball 4,
Sky Field 2, filler 37. Seven opening cards, six random Prizes,
one natural draw on each of turns one and two.

| Branch | Per seven-card opening attempt |
| --- | ---: |
| Gothita and all four ordinary Basics naturally ready | 0.000020203% |
| Quick Ball searches the fourth ordinary Basic | 0.001097614% |
| Quick Ball searches Gothita | 0.000455535% |
| **Combined** | **0.001573353%** |
| **Conditional on legal opener** | **0.002023400%** |

This more demanding state is a strict subset of the earlier
0.542350465% card-access event, and its probability is much smaller.

Under the restricted model, the **search-core** branch contributes
more than the search-Gothita branch. That distinction is missed when
Quick Ball is modeled only as a Gothita search card.

## Validation and semantics

Exact multivariate opening-hand weights and first-turn draw weights
are combined with a hypergeometric distribution over Prize cards.
Each conditional Basic search selects one physically unprized target.
If both evolution pieces are already present, the turn-two draw need
not hit anything. If exactly one is missing, its expected remaining
copies are divided by the correct post-search physical deck size.

Two separately implemented labeled enumerators on 12-card and
13-card toy populations agree with all three exact rational event
masses. A zero-Prize variant and boundary regressions for zero
Quick Ball, zero Sky Field, too few ordinary Basics, and increasing
Sky Field copies are also included. The card-text and rules grounding
is inherited from the prior result and its passing CI test.

## Limits

Four ordinary Basics are an abstract compatible group: the model
assumes they may be used as one Active and three Benched Pokémon
without requiring specific names, costs, Abilities or additional
search. It does not assign them individual card identities beyond
the disjoint category count.

The current model assumes Sky Field enters discard on turn one and
Gothita survives to turn two. It does not sample the opponent's
Collapsed Stadium/Ninetales establishment, the two later Basic
entrants, Item lock, opponent attacks, or other draw/search engine
resources. Their omission makes this a **minimal no-extra-search
board-access benchmark**, not a deck win rate or a reliable empirical
estimate of a competitive archetype.

## Next useful work

Allow a second independent first-turn Basic search action and price
its discard and search-target contention. The expected improvement
is state dependent: additional search matters most when both Gothita
and a core Basic are missing, whereas an extra Quick copy without
another disposable card may be unplayable.
