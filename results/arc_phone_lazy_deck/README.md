# Exact Prize/top policy without permuting the whole remaining deck

## Question

Can a finite-horizon Arc Phone and Trekking Shoes optimizer account for an ordinary large deck's exact top-card probabilities, despite correlations with Prized cards, without enumerating every full deck ordering?

Yes for this restricted transition set. The hidden deck suffix remains **exchangeable** after each action, so a complete materialized ordering is unnecessary.

## Representation and proof boundary

Implementation: `tools/arc_phone_lazy_deck.py`. Each posterior world stores:

1. a physical ordered mapping from Prize positions to strategic groups;
2. one deck-top group, or empty;
3. the multiset counts of the unseen deck tail.

A rational probability is attached to each world. The groups are `T` (target), `A` (Arc Phone), `S` (Trekking Shoes), and `F` (filler). The initial deck tail is uniformly random conditional on its composition, and the initial Prize positions are uniformly random conditional on their composition.

**Inductive sufficiency argument:** Arc Phone inspects top, then optionally exchanges it with one chosen face-down Prize position. That leaves the deck tail untouched. Trekking Shoes reveals top and either takes it or discards it and draws the next card. Under uniform-tail exchangeability, the next revealed group has probability `count(group)/tail_size`, and conditioning on that observation leaves the remaining tail uniformly exchangeable. Thus every supported material action and observation preserves the representation. The joint posterior tracks correlations between Prize position, top, and tail composition, since these fields coexist inside each weighted world.

The result does **not** establish sufficiency for effects that inspect or rearrange deeper positions, know specific top sequences, shuffle only parts of a deck, or manipulate named physical identities beyond these categories. Those need extra state.

## Full 60-card controlled snapshot

Consider a physically conserving 60-card state:

- six Prizes containing exactly `T + 5F`, hidden positional mapping, known composition;
- 47 cards remaining in deck: `2A + 2S + 43F`, random unknown order;
- a hand containing `2A + 2S + 2F`;
- one established Basic represented by the remaining `F` on the board.

The target is known Prized, and the player has the necessary Items in hand, with no opposing locks. The objective is to obtain `T` into hand before running out of those Items, using the legal Arc Phone and Trekking Shoes actions only.

| Shoes policy | Exact success probability |
| --- | ---: |
| Take viewed top only | `46/135 = 34.074074074%` |
| Choose to take or discard-and-draw | `111820/321057 = 34.828706429%` |
| Marginal benefit of Shoes discard option | `1346/178365 = 0.754632355 percentage points` |

This is a conditional, internally consistent research state, not a sampled distribution of legal openings or a game win-rate model. It assumes K1 Prize composition and access to the stated hand. Only target acquisition is valued; the strategic cost of moving a filler card into the Prize zone is ignored.

### Computational compression

For this exact 47-card deck, the number of distinct deck orderings is

`C(47,2) * C(45,2) = 1,070,190`.

The target's six possible Prize positions produce **6,421,140** joint fully ordered initial worlds. The factorized representation stores only **18** initial posterior support worlds: six Prize layouts times three possible top groups. This is a **356,730-fold initial support reduction**.

It does not guarantee a similar reduction in every later posterior or for other card effects; in this case, the dynamic program completes the full 60-card-state calculation without expanding the deck permutations.

## Independent mechanical and policy validation

`results/arc_phone_lazy_deck/reproduce.py` compares factorized transitions to the preceding full-permutation `tools/arc_phone_deck_order_policy.py` for four independent small-state fixtures. It verifies, with exact rational equality:

- projected initial full-deck belief;
- ordinary one-card draw;
- two-card removal corresponding to Shoes discard-and-draw;
- all Prize-position swaps;
- Bellman-optimal target retrieval with and without Shoes' discard mode.

These comparisons supplement the previous solver's independent labeled-world oracle. The new regression also asserts both exact full-state fractions above, providing a reproducible controlled 60-card result.

## Next work

The natural extension is a hybrid physical-belief kernel that detects when exchangeability remains sufficient and materializes deck positions only when a card effect creates order-specific information. Coupling the compressed policy to valid openings, K0/K1 transitions, Peonia replacement payments, and ordinary draw/search actions would give a more representative deck-level resource-access model.
