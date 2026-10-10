# Knowing the second deck card breaks an exchangeable Prize/top draw model

## Question

The [correlated Prize/top draw pool](../prize_top_draw_pool/) assumes the unobserved deck suffix is uniformly exchangeable. What happens if a previous inspection or placement makes the **second deck card** known?

A group-count-only residual pool can then preserve the exact remaining card inventory while predicting the wrong next draw. A two-card order model shows the boundary precisely.

## Two-card window

`tools/prize_top_two_order.py` extends the conserved Prize/top pool with a special `second` field. The second card is still counted inside the pool's deck remainder, so the representation does not invent a second physical copy.

Its supported transitions are:

- `from_exchangeable_pool`: select the current second card uniformly from the remaining deck multiset when no earlier order information exists;
- `observe_second`: condition on the specific second-card group after a source-authorized private look;
- `swap_top_with_face_down`: exchange current top and chosen eligible Prize while preserving second-card position;
- `draw_top_and_shift_window`: move old top into tracked drawn cards, shift the known second card into the top slot, then expose a new second card from the still-exchangeable deeper suffix;
- `to_exchangeable_pool`: intentionally forget the second-card position as a lossy projection.

The model preserves exact initial grouped card counts across Prizes, top, deeper deck, and drawn zone.

## Exact five-card counterexample

Begin with five distinct labeled physical cards `A, B, C, F1, F2`. There are two Prize positions and three ordered deck positions.

Condition on:

- Prize0 = B;
- Prize1 is one of the filler cards;
- original deck top = A;
- remaining two deck cards are C and the other filler.

Arc Phone swaps top A with Prize0 B. B is now the top deck card. The next draw takes B, exposing the **original second deck card**.

The remaining deck inventory is always C plus filler, independent of their order. Nevertheless:

| Knowledge about original second card | Probability next top is C after drawing B |
| --- | ---: |
| Order unknown, C and filler exchangeable | **1/2** |
| Player privately observed C in second position | **1** |
| Player privately observed filler in second position | **0** |

When C is known second, conditioning changes **only the order belief**. A model that forgets its position and retains the exact same two-card group inventory falls back to the incorrect prediction 1/2.

The independent physical oracle enumerates all **120 ordered assignments** of Prize0, Prize1, first deck card, and second deck card from the five distinct cards. Exactly four satisfy the first three material constraints. Two have C second. Their post-swap/draw result is certain C as next top, in agreement with the two-position model.

## Strategic meaning

A search or deck inspection that reveals several upcoming cards can change the value of subsequent operations even when the material deck composition remains unchanged.

For example, a player using an Arc Phone-like top swap followed by a draw can preserve important knowledge about the next card. A simulator that blindly resets the deck suffix to exchangeable after merely moving the top card will undervalue known good next draws or overvalue known misses.

This relates to [pre-reset shuffle value](../pre_reset_shuffle_value/), which already demonstrates that shuffling can destroy beneficial future-draw knowledge. Here the same principle appears inside a conserved cross-zone Prize/top operation.

## Validation and boundaries

The reproducer independently enumerates the 120 labeled ordered deals, tests the three probability cases (1/2, 1, 0), verifies conservation and the intentional lossy projection, and checks impossible second-card observations.

The case stipulates a source-authorized earlier look at or knowledge of the second card. The model itself does not implement any particular Trainer card that obtains that information.

The two-card window is sufficient only while no relevant information is known **deeper than the second position**. When shifting the window after a draw, it samples the next second card from an exchangeable residual suffix. If the player knows the third card too, the same hazard recurs. A fully general model requires a variable-depth ordered prefix plus exchangeable suffix, and separate observer-specific knowledge of that prefix.

The example is a combinatorial witness about correct state representation. It does not model whole-game turns, complete hands, locks or win rates.

## Next

Generalize the fixed two-card model into an **ordered known-prefix + exchangeable remainder** whose depth can vary by observer, with explicit conditions for when collapsing the prefix preserves action value.
