# Full-hand replacement destinations and pre-reset payment geometry

## Question

Earlier [pre-reset sequencing synthesis](../pre_reset_sequencing_synthesis/README.md) proved a conditional hand-material equivalence for playing Quick Ball before a *discard-hand* reset. Does the same equivalence hold when the redraw shuffles the old hand into the deck or puts it on the bottom?

## Card-text catalog

The new scanner (`tools/catalog_full_hand_replacements.py`) explicitly matches full-hand return-and-draw wordings in bundled English prints from Expanded-eligible sets, using the repository's effective print-ban classifier. It supplements [the existing 80-print discard-reset catalog](../full_hand_reset_catalog/README.md).

Current resource snapshot, counting distinct exact print IDs:

| Hand destination | Prints | Distinct normalized full effect-text variants |
| --- | ---: | ---: |
| Shuffle hand into deck | **128** | 59 |
| Shuffle hand to bottom of deck | **19** | 6 |
| **Combined** | **147** | **65** |

Print-source split: 97 Supporter, 40 attack, 7 Ability, 2 Stadium, 1 Item. Target-scope and source-gate differences still matter.

Direct card-text witnesses: Cynthia, N, Judge, and Unfair Stamp shuffle hands back into decks. Marnie, Iono, Skwovet, and Kingdra send hands to the bottom of decks. Jubilife Village allows a redraw during a player's turn and ends that turn. Reprinted texts remain separate when their complete effect wording differs, even under the same name.

**Scope caution:** These are syntactic candidate print records in the current local data and legality overlay, not proof of a complete legal-name family inventory. Historical functional-reprint eligibility, current errata, conditional draw gates, opponent effects, and detailed source timing remain separate evaluation problems. Cards that return only *part* of a hand (for example Caitlin, Maintenance, Kofu) and effects replacing only the opponent's hand are deliberately excluded.

## Exact material and singleton-access model

Let N be the size of the original deck, H the number of cards in the old hand after any reset source leaves the hand, P the number of old-hand cards consumed by a prior optional action, and d the number of new cards drawn. Assume a legal fixed-count effect, exactly one target card, an exchangeable deck ordering, and no other transitions or intervention before the draw.

All probabilities below are conditional on the target's current zone; they are not full-deck consistency rates.

| Destination | Target in original deck | Target in retained old hand | Target consumed as payment |
| --- | --- | --- | --- |
| Discard old hand | min(d,N)/N | 0 | 0 |
| Shuffle old hand into deck | min(d,N+H-P)/(N+H-P) | same | 0 |
| Put old hand on bottom | min(d,N)/N | min(max(d-N,0),H-P)/(H-P) | 0 |

The bottom-of-deck retained-hand expression assumes H-P is positive. For d at most N, that exposure is exactly zero. If the deck order is known or a subsequent shuffle occurs, the relevant probabilities change.

**Key inference:** The committed-reset material equivalence for Quick Ball under a discard-all reset does not generally extend to either hand-return destination. A prior search payment permanently diverts those physical cards to discard instead of returning them to the deck. For a bottom-deck reset, this difference may have zero *immediate* exposure effect while remaining material to future turns. For a shuffle-back reset, the immediate draw pool also changes size.

## Numerical witness

Choose N=46, H=5, P=2, d=6. The prior action consumes Quick Ball plus another hand card, chooses zero search targets, and the subsequent redraw proceeds. The values intentionally ignore the opportunity cost of using Quick Ball as a later search.

- For a singleton originally in the deck, a shuffle-back reset alone reaches it with 6/51 = **11.764706%** probability. Consuming two other hand cards before that reset changes the pool to 49 and the probability to 6/49 = **12.244898%**. Immediate draw exposure increases by **0.480192 percentage points**.
- If the singleton was originally in the hand and is paid to the prior action, the same comparison falls from 6/51 = **11.764706%** to **0%**, a decrease of **11.764706 percentage points**.
- Under a bottom-deck reset with d=6, a retained hand singleton has **0%** immediate exposure, while a deck singleton has 6/46 = **13.043478%** exposure under the exchangeable-order assumption.
- Under a discard-all reset with the same deck and neutral shuffle, paying with two cards already destined for discard leaves the target-in-deck one-step exposure at 6/46.

This illustrates why DCI and connector availability must be evaluated relative to the actual **hand destination**. A search-first play can thin the immediate shuffle-back draw pool yet destroy a future reusable search or target card. Either effect can reverse the preferred sequence depending on what the deck needs.

## Reproducibility and validation

- `tools/catalog_full_hand_replacements.py`: prints the candidate variants and provenance IDs using the local card snapshot and shared legality classifier.
- `tools/hand_destination_reset_geometry.py`: exact rational one-step target exposure and pre-action deltas.
- `results/hand_destination_reset_geometry/reproduce.py`: checks 147 matching card IDs and the 128/19 split; checks known included/excluded cards; compares the analytic formulas against exhaustive permutations of small labeled decks and hands for all three destinations, target locations, payment states, and draw windows.

Run the reproducer with Python standard library only. The catalog has an explicit exact-snapshot count regression to catch data and regex drift; a future dataset update will require inspecting the changed records.

## Limitations and next research

The formulas deliberately omit Prize cards, opening conditioning, Supporter/Item/Ability contention, reset cancellation, deck-order information, draw modifiers, how the pre-action obtained its payment, triggered discard effects, recycling, and the actual game utility of held/discarded cards.

Next useful work: feed these return destinations into the existing typed reset transition profiles; model conditional multi-action policies where a search action reveals K1 and the player may cancel or change the redraw; compare the future option value of a card recycled into the deck with its immediate thinning effect.

Research type: card-text snapshot classification plus exact combinatorial model and exhaustive small-state validation. No gameplay win-rate or meta-strength claim is made.
