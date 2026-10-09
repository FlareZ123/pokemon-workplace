# Arc Phone can repack the deck top as a known Peonia target

## Question

Is playing Peonia before Arc Phone always as good as keeping Peonia available for later? Earlier fixed-K1 Prized-singleton retrieval tests gave equal optima under both orders, but that is not a theorem.

**Counterexample:** When a critical singleton might be in the Prizes *or* on the deck top, and the endpoint requires keeping an unused Trekking Shoes, playing Arc Phone first can strictly outperform playing Peonia first.

## Concrete card-text mechanism

Arc Phone `swsh11-152` says to look at the top card of the deck and optionally switch it with one face-down Prize card. Peonia `swsh6-149` can move up to three selected Prize cards into hand, returning the same number of hand cards face down as Prizes. Trekking Shoes `swsh10-156` can retrieve deck top, but *playing* it consumes the sole Shoes required by the stronger objective.

If Arc Phone sees T on deck top, the player switches that T into a **chosen, now known physical Prize position**, replacing the former Prize with the deck top. Peonia is then played and selects the known position to retrieve T while the original Shoes remains unplayed in hand. This is a genuine, legal sequence of separate Item and Supporter actions under their printed text.

If the top is F, Arc can decline the exchange. Peonia then examines up to three Prize positions normally. The player's information is used at the correct time; the model never reveals unseen Prize identities.

## Exact small-state witness

A single target `T` is uniformly distributed among five unknown face-down Prize positions and the two unknown deck positions. All six other cards in those zones are inert `F`. Hand contains Peonia, Arc Phone, Trekking Shoes and one expendable filler. No other effects intervene. Success means **T and an unused Shoes are both in hand at once**. This is a synthetic seven-position K0-like uncertainty model in a very late-game deck state, not an estimate of a frequent competitive situation.

- **Peonia-first optimum:** `3/7 = 42.857143%`. It can retrieve T from three of the seven physical positions. If T was in the deck, later Shoes can take it but then no Shoes remains to satisfy the endpoint.
- **Unrestricted optimum:** `4/7 = 57.142857%`. Arc-first can recover topdeck T using Peonia, in addition to the three ordinary Prize positions.
- **Absolute timing gain:** `1/7 = 14.285714` percentage points.

This is a strict counterexample to universal Peonia-first dominance. It also shows that an Item's look-then-exchange mode may act as a **conversion from deck-top knowledge to position-known Prize retrieval** rather than merely as a draw accelerator.

## Small general theorem under the same assumptions

For `n >= 3` Prize positions, `d >= 1` hidden deck positions, one uniformly located T, Peonia capable of inspecting three Prizes, one held Arc, one Shoes that must remain unused, sufficient filler payment and no other useful effects:

- Peonia first: `3/(n+d)`.
- Arc before Peonia, adapt after observing deck top: `4/(n+d)`.
- Timing advantage: `1/(n+d)`.

The upper bound follows from counting distinguishable reachable target locations: preserving Shoes means T must reach hand through Peonia. Before spending Peonia, Arc can inspect only one deck position and stage it in a known Prize location; Peonia can recover the target from at most three other unknown Prize positions. The described Arc-first policy attains this bound. Peonia-first never gets an opportunity to retrieve the staged target after using Arc, so it can access only its first three selections.

The exact physical-world Bellman solver independently returns the stated formula for all twelve `n` in `4,5,6` and `d` in `1,2,3,4`, preserving the observation partitions and optional Arc exchange.

## Method and reproducibility

Source: `results/peonia_repackaged_top/reproduce.py`, using the shared `tools/peonia_timing_policy.py` exact Fraction-based policy engine. This extends `results/peonia_prized_item_recycling/` by changing hidden composition and the downstream terminal constraint. Every physical target location is equally weighted; the program tests Peonia-first and unrestricted timing with separate cached action policies.

## Limits

This model has one single-copy T, all other hidden cards inert and exactly one held Arc/Shoes. A broader 60-card state could include recovery, search, evolving, hand disruption or other Item draw that reverses the timing ranking. Real paper Expanded normally starts with six Prizes; the smaller Prize counts are illustrative midgame states. Card legality and printed effects are supported by the bundled card database, and the underlying sequencing follows the advanced rulebook. No win-rate or archetype recommendation follows from this isolated event.

Next, test if this particular strict timing advantage survives realistic deck-tail distributions, multiple Items and a costed Supporter window. Another valuable direction is identifying all card combinations that safely repack a known deck-top target into an action channel which preserves some other scarce resource.
