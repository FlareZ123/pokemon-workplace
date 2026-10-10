# Gladion plus Pokémon Communication repairs Grand Tree's deck-search destination

## Question

Grand Tree (`sv7-136`) evolves a Pokémon using Stage 1 and Stage 2
cards searched **from the deck**. If a necessary Gothorita or Gothitelle
is in the Prize cards, Gladion (`sm4-95`) can recover it. However Gladion
puts the retrieved card **into hand**, leaving Grand Tree unable to search
for it directly.

Can a legal Expanded Item bridge the destination in the same turn, and
how does a single bridge change the conditional Prize-supply probability
for the four-Gothitelle bootstrap scenario?

## Legally supported physical route

Pokémon Communication (`sm9-152`) says to reveal one Pokémon in hand,
put it into deck, then search deck for a Pokémon and put it into hand,
and shuffle. The bundled Advanced Player's Rulebook, section I-H,
permits selecting **zero** cards for a category-constrained deck search;
the exception for compulsory selection applies when searching for
arbitrary card identities with no type restriction.

Consequently, after Gladion puts a specifically selected Prized Pokémon
into hand, Pokémon Communication may:

1. Return that same physical Gothorita or Gothitelle to deck.
2. Choose **zero** Pokémon from the subsequent search.
3. Shuffle the deck and leave the returned card available for Grand
   Tree to search.

No alternative Pokémon has to be taken out of deck. The returned Pokémon
itself suffices to make the Item effective: its source-zone change
already happened. Gladion itself moves into the vacated Prize slot, and
the Pokémon Communication Item goes to the discard pile.

This sequence requires Gladion and Pokémon Communication in hand
or otherwise obtainable, an unused ordinary Supporter play,
the ability to play the Item (no applicable lock), and an eligible
Grand Tree Basic target in play. Grand Tree's timing and evolution
requirements remain unchanged.

The official Japanese Pokémon Communication card confirms the basic
hand-to-deck and search effect:
https://www.pokemon-card.com/card-search/details.php/card/36958

The provided Advanced Rulebook supplies the zero-target deck-search
permission, so the route does not rely on guessing a special-case Q&A.

## Exact material transaction

`tools/gladion_communication_material_bridge.py` composes the
repository's existing literal `resolve_gladion_physical()` kernel with
the Pokémon Communication movement using materialized card-instance IDs.

It enumerates every possible post-Gladion Prize ordering, preserves
all six Prize positions, routes the played Gladion to Prize,
routes Pokémon Communication to discard, and returns the
**same selected physical Prize Pokémon** from hand into deck.

Because Pokémon Communication shuffles the deck, the bridge deliberately
drops the old designated deck-top positional identity after routing
its physical card into deck. It retains exact card-instance IDs,
zone ownership, and Prize positions while projecting away random deck
order. All material card totals are conserved.

The regression then invokes the existing `execute_grand_tree_chain()`
to evolve a materialized eligible Gothita with the returned Gothorita
and a Gothitelle that was already in deck. It binds those two physical
cards to the same in-play Pokémon object and validates complete
evolution stack identities.

The three exact availability states are:

| Route | Stage 1 zone | Grand Tree full Stage 2 chain |
|---|---|---|
| Before Gladion | Prize | Unavailable |
| After Gladion | Hand | Still unavailable |
| After Pokémon Communication (zero-search) | Deck | Available if other prerequisites hold |

## Joint Prize combinatorics with one rescue

For a comparable **conditioned** prior to the previous source-bootstrap
result, assume ten cards are already known not to be Prized: one
Gothitelle evolution stack, three eligible Gothita, Grand Tree in play,
Brooklet Hill in hand, Gladion in hand, Pokémon Communication in hand.
This leaves 50 unseen physical cards, including three Gothorita,
three Gothitelle, and 44 others. Six Prizes are sampled uniformly.

Let X and Y be the numbers of Prized Gothorita and Gothitelle. A single
legal, accessible Gladion + Pokémon Communication route can restore one
Prized Pokémon of either category to the deck. It optimizes
`min(3,3-X,3-Y)` with at most one restored card.

The exact distribution for new Gothitelle supplies is:

| Additional Gothitelle | No Prize repair | One available bridge |
|---|---:|---:|
| 0 | 0.204075% | 0.000006% |
| 1 | 6.679454% | 0.257648% |
| 2 | 48.693934% | 14.314391% |
| 3 | 44.422536% | **85.427955%** |

The full-three outcome increases by **41.005418 percentage points**
given the bridge resources, card-zone assumptions and optimistic
per-entry Grand Tree reuse model. The expected number of additional
Gothitelle increases from **2.373349** to **2.851703**.

This improvement is largely explained by the exact event
`X+Y<=1`: if zero of the six necessary evolutions are Prized,
nothing needs rescue; if exactly one is Prized, Gladion plus
Communication repairs it. With two missing cards a single rescue
cannot produce all three Stage2s.

Thus, with `N=50`, `C=6` critical Pokémon and six Prize cards,
the exact full-three probability with one rescue is:

`[binom(44,6) + 6 binom(44,5)] / binom(50,6)`.

This is a **conditional supply sensitivity comparison**. A
matched probability difference does not mean adding Gladion and Pokémon
Communication to an otherwise fixed 60-card deck produces the same
41-point practical gain. Conditioning on having both cards already in
hand is the principal reason the bridge is guaranteed, and the two
newly conditioned hand cards reduce the random unseen population
from the prior 52-card experiment to 50. The baseline column in
this table uses the same 50-card conditioned space for fair comparison.

## Reproduction and validation

`python results/grand_tree_prize_rescue_bridge/reproduce.py`

The regression checks actual bundled Expanded card text and
the rulebook's limited-search permission. It carries exact physical
card IDs through 720 distinct Gladion Prize orderings, verifies
conservation and the change in search availability at each
zone boundary, and executes one Grand Tree Gothita-to-Gothitelle
chain using the repository's evolution kernel. A separate labeled
Prize-subset enumerator verifies the joint exact probability model
against independently enumerated tiny decks.

## Limitations

The action-cap of three new Gothitelle comes from the previously
computed conditional bootstrap model, **assuming the still-unresolved
per-entry same-physical-Stadium use refresh**. Neither the Prize
probability nor the physical bridge resolves that ruling.

The exact supply model assumes that unprized evolution cards are
searchable in deck. It does not simulate the opening-hand conditioning
that produces Gladion and Pokémon Communication, their search
connectors, Item lock, Supporter contention, opponent actions,
alternative Prize recourse, or Pokémon Communication's multiple
possible strategic targets.

The physical witness is a valid controlled route, rather than proof
that a particular deck can establish all the necessary evolved source
Pokémon on a real turn.

Related work:
[Grand Tree physical Stage1/Stage2 chain](../grand_tree_materialized_chain/),
[literal Gladion Prize destination](../literal_gladion_projection/),
[source bootstrap](../stadium_gothitelle_bootstrap/).
