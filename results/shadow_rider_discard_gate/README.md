# Shadow Rider: how discard-safe hand cards gate Mysterious Treasure

## The access-versus-payment problem

The [champion Radiant Eternatus launcher](../shadow_rider_radiant_launch/) has **43.699162430%** two-Shadow-Rider-VMAX reachability through either a naturally held Radiant Eternatus or a held Mysterious Treasure. This counts Mysterious Treasure as **mechanically payable**. Its actual text requires the player to discard a card before searching for Radiant, and the discarded card can have important strategic value.

This investigation makes that caveat quantitative without pretending to know the optimal DCI of every individual card.

## Hypothetical discard-safety model

Starting from the champion's exact 60-card category counts, divide its 38 otherwise unmodeled card copies into:

- **d predesignated safe-to-discard physical cards**, selectable from hand for Treasure's one-card discard cost;
- **38-d protected physical cards**, considered unavailable as payment.

All four Shadow Rider VMAX, other 13 starting Basics, Radiant Eternatus, and remaining Mysterious Treasures are also designated protected. This is a deliberately strict, exogenous DCI assumption. It is **not** a claim that those actual cards are unconditionally undiscardable. A spare VMAX, second Treasure, extra Basic or some other card may be a reasonable discard in real matches. The search itself still requires a non-Radiant starting Basic and two VMAX remaining in the deck.

Fixing a grouped opening/Prize/draw state in which the Treasure route works and the hand contains h of the 38 other cards, their preassigned safety classes are exchangeable. Therefore:

\[
P(\text{one or more safe payments}\mid h,d)
=1-\frac{\binom{38-d}{h}}{\binom{38}{h}}
\]

with the numerator treated as zero when too few protected copies exist.

Multiplying this exact weight by each Treasure-ready state's multivariate hypergeometric mass gives the overall probability without resampling Prize cards or inserting imaginary extra hand cards.

## Exact conditional launch sensitivity

All rows condition on a valid seven-card Basic opening, six Prizes, and one normal first draw going second.

| Hypothetically safe cards among the 38 | Treasure-mediated dual VMAX | Total direct + payable Treasure dual VMAX |
| ---: | ---: | ---: |
| 0 | 0.000000% | 12.017840% |
| 1 | 3.711186% | 15.729026% |
| 2 | 7.051542% | 19.069382% |
| 4 | 12.739312% | 24.757153% |
| 8 | 20.877434% | 32.895274% |
| 10 | 23.687230% | 35.705070% |
| 12 | 25.857006% | 37.874846% |
| 16 | 28.749567% | 40.767407% |
| 20 | 30.325874% | 42.343714% |
| 24 | 31.118753% | 43.136594% |
| 32 | 31.620904% | 43.638744% |
| 38 | 31.675657% | 43.693497% |

**Key finding:** merely having four Mysterious Treasure copies in the list cannot be equated with guaranteed usable access. Under the hypothetical ten-safe-card partition, the two-VMAX access fraction is **35.705070%**, compared with the mechanically payable 43.699162%.

Even when all 38 other copies are safe, **0.0056658 percentage points** of Treasure dual-launch states hold none of them; this particular strict policy cannot pay there. In real games a redundant other-category card may be disposable, so this is a model limitation rather than an inherent unpayable rate for the real list.

The biggest strategic uncertainty is *which cards are genuinely safe to discard in which matchups*, including the opportunity cost of using Mysterious Treasure to obtain Radiant rather than another Psychic/Dragon Pokémon. The correct policy changes with Prizes, opponent, planned turn, and other search available. The table therefore represents a **sensitivity frontier over hypothetical DCI assignments**, not measured win rates or estimates of actual discard quality.

## Validation

The [exact reproducer](reproduce.py) derives a distribution of Treasure-ready outcomes by the number of other physical cards in hand. For each d it integrates the hypergeometric presence gate algebraically.

A separate full physical-card ten-card toy oracle marks two of four filler copies safe, enumerates all **8,925 accepted labeled opening/Prize/draw combinations**, then tests whether Treasure can really discard an eligible physical copy. The exact grouped and labeled results match, including the direct-Radiant baseline. Regressions additionally check the current 60-card source and the complete-disposable limiting case.

This result is a practical connector-domination warning: increasing theoretical reachability can leave a deck with few acceptable discard choices. A future policy should value those alternatives in the same game state rather than assigning fixed DCI categories once for all turns.
