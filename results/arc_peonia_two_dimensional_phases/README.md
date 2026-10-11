# Two-dimensional Prize-prior and deck-size policy phases

## Research question

The optimal four-Item mix of Arc Phone and Trekking Shoes depends on two pieces of information: how likely a critical singleton is Prized, and how many unseen deck cards remain.

We calculate the complete joint phase diagram in a controlled Peonia-access model. T is in one of six face-down Prizes with prior probability p and uniform physical position; otherwise, it is in one of d unknown deck positions with uniform conditional position. One Peonia, sufficient replacement filler and four immediately usable Items are held, with a Arc Phone and 4-a Trekking Shoes. Other hidden cards are inert filler F.

## Exact efficient target-location coverage pairs

Each ordered pair below is the number of initially Prized and initially deck-located T positions from which a legal adaptive action policy can retrieve T:

| Inventory (Arc / Shoes) | Attainable efficient (Prize, Deck) pairs |
|---|---|
| 0 / 4 | (3, min(d,8)) |
| 1 / 3 | (3, min(d,7)) or (4, min(d,6)) |
| 2 / 2 | (4, min(d,5)) or (5, min(d,4)) |
| 3 / 1 | (5, min(d,3)) or (6, min(d,2)) |
| 4 / 0 | (6, min(d,1)) |

The deck-heavy variant of a mixed package probes more original deck cards before spending some Arcs on Prize positions. The Prize-heavy variant uses an additional Arc to inspect a displaced Prize before consuming Shoes. These alternatives are observation-respecting and achieve all tabulated covered positions.

A coverage pair (r,k) yields

\`V_{r,k}(p,d) = p*r/6 + (1-p)*k/d\`.

The exact optimal retrieval probability is the upper envelope over those eight affine functions of p. This produces discrete switches when two envelopes cross. The program checks that the envelopes match a separately written physical-world Bellman optimizer.

## Interior optimal inventory phases

In this table intervals are strict and a represents the optimal Arc count, with 4-a Shoes. At every listed boundary the adjacent winners tie, and in some cases an additional inventory also ties.

| Unknown deck size d | Optimal Arc counts as p increases from 0 to 1 |
|---:|---|
| 1 | 3 or 4 throughout |
| 2 | 3 throughout |
| 3 | 2 or 3 for p below 2/3; 3 above |
| 4 | 2 below 3/4; 3 above |
| 5 | 1 or 2 below 6/11; 2 from 6/11 to 12/17; 3 above 12/17 |
| 6 | 1 below 2/3; 3 above |
| 7 | 0 or 1 below 6/13; 1 from 6/13 to 12/19; 3 above 12/19 |
| 8 and above | 0 below 12/(d+12); 3 above |

For d>=8 and 0<=p<1, the full interior optimum simplifies to

\`V*(p,d)=max[ p/2 + 8(1-p)/d, p+2(1-p)/d ]\`.

Its sole interior breakpoint is

\`p_c(d)=12/(d+12)\`.

At d=46 this recovers [the previously derived 6/29 breakpoint](../arc_peonia_mixed_prior/). At d=8 the breakpoint is 3/5. At the breakpoint, Arc counts 0,1,2 and 3 all tie. At p=1, Arc count 4 also ties with count 3.

For short decks, finite Shoes draw reach saturates, and intermediate Item mixes can become the unique optimum. For example at d=4, p below 3/4 favors two Arcs and two Shoes, while above 3/4 three Arcs and one Shoes wins. At d=5, three distinct inventory regions exist.

## Evidence and reproducibility

\`tools/arc_peonia_two_dimensional_phases.py\` constructs the eight exact coverage pairs, computes their rational line intersections, removes intersections that do not change the optimum, and verifies the expected optimal intervals across d=1..46.

At d=1..8 and d=46, each phase midpoint, boundary and endpoint is compared with the **independent exact physical-world Bellman policy** in \`tools/arc_peonia_mixed_prior.py\`. This solver retains full target origin-zone provenance after Arc exchanges and Shoes draw transitions, so the policy never uses future knowledge of whether the target was originally in the deck or in the Prizes.

The regression asserts the exact best inventory and exact retrieval probability on every tested posterior. Run \`python tools/arc_peonia_two_dimensional_phases.py\`; the shared Windows CI workflow executes it.

## Interpretation and limits

The phase diagram represents an information-sensitive resource-allocation problem inside a small card-interaction model. It contains genuine Pokémon effect timing and physical card-zone changes, but assumes all useful Items and Peonia are already available, one target singleton, inert filler, and no lock, opponent, Supporter opportunity cost or turn deadlines. Consequently, this is a conditional target-acquisition frontier, not a deck-building recommendation or win-rate prediction.

Future work: estimate attainable points (p,d) from actual K0 and K1 search observations and compare options with a finite probability of running out of deck before the recovered card can be used.
