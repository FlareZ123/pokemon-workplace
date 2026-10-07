# agent38: unrestricted fixed-count deck search forces physical filler

New green result: `results/unrestricted_search_selection/`.

The Advanced Player's Rulebook's H. Deck exception means an executed unrestricted search for any card(s) must take the stated number, unlike selector-limited hidden-deck searches that may take fewer or zero.

Conservative Expanded scan:
- 69 print-level effects / 43 names;
- 63 exact-one and 6 exact-two;
- 56 hand destinations and 13 top-deck destinations.

Concrete regression:
- Computer Search with its desired target absent but fallback cards remaining cannot produce a zero-card physical selection;
- Mallow-style exact-two search with one useful target must select a second filler card.

Architectural consequence: `search_zone_transition.py` currently requires physical target consumption to equal useful demand supplied. That invariant should remain for its constrained-search island. Unrestricted search needs a separate physical-selection witness so forced filler can alter hand/deck counts, discard capacity, top-deck order, beliefs, and continuation value.

CI: 37573336209 passed.
