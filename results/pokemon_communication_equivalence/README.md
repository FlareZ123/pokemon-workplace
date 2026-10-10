# Pokémon Communication: return, search, and shuffle

## Question

Can the historical `hgss1-98` Pokémon Communication Item's
"show" and "put on top" wording produce the same physical and
publicly observed outcomes as the legal `bw1-99` and
`sm9-152` versions?

## Bounded result

Across **54** source-state configurations and **1,854** conditional
labeled-card outcomes, the three described procedures have identical
final outcome sets. In the model, one hand Pokémon is revealed and
returned to the deck, the player can search for a Pokémon (including
the just-returned card), and the deck is shuffled afterward.
The target selection is public and counted before the shuffle.
All post-shuffle orders are explicitly enumerated with their
conditional uniform probabilities.

The new `sm9-152` text places the returned Pokémon **into the deck**
rather than expressly **on top**. That intermediate position is erased
by the mandatory subsequent shuffle. Both procedures provide the
same searchable set and retain the revealed returned card identity.
The HGSS and BW prints both expressly place the returned card on top;
`show` and `reveal` are treated as the same public information.

This is a state-model equivalence and remains subject to a full
tournament reprint interpretation. The resolver currently retains
`hgss1-98` as `semantic_review`; this research does not
automatically promote it to a legal candidate.

## Reproduction

`python -m results.pokemon_communication_equivalence.reproduce`

`tools/pokemon_communication_equivalence.py` models 0–2 hand
Pokémon, 0–1 unrelated hand cards, 0–2 deck Pokémon, and 0–2
non-Pokémon deck cards using distinguishable physical IDs.
It includes voluntary failure to select a card from the
type-limited deck search, according to the bundled Advanced
Player's Rulebook section I-H.

## Remaining caveats

The comparison assumes no external effect intervenes between
returning the card, searching the deck, and the required shuffle.
Any claimed mid-effect reaction or observable placement order must
be supported by card text and the actual rules. The test covers
exactly the stated bounded cases; it is not a match simulation.
