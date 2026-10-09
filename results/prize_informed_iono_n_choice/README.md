# Prize uncertainty and the option value of choosing Iono or N after deck search

## Question

Previous exact result [Iono versus N](../iono_n_access_comparison/README.md) found that the preferable Prize-dependent redraw changes with the number of useful outs in the original deck. Before the first deck search, some outs might be among hidden Prizes. Does information from an otherwise available deck search change the optimal choice?

This is a K0/K1 illustration in the terminology of `resources/human_concepts.md`. K0 knows the preexisting deck's distribution but not its exact remaining useful-out count; K1 knows that count after inspecting the complete deck.

## Exact combinatorial setup

Let D = old deck size, P = hidden Prize count, U = number of useful interchangeable outs among deck plus hidden Prizes. Let H = own known old hand size, R = known outs in that hand, d = own remaining Prize draw count, Q = opponent hand size.

Before search, the K0 number K of deck outs has probability

`Pr(K=k) = C(D,k) C(P,U-k) / C(D+P,U)`.

For every possible K, the conditional one-step access probabilities for Iono and N follow the earlier exact model, including Iono's either-player nonempty-hand draw gate. A player who must choose before seeing K obtains

`V_K0 = max(E[Pr(hit | Iono,K)], E[Pr(hit | N,K)])`.

When a legal deck search reveals K without altering the modeled draw distribution or action availability,

`V_K1 = E[max(Pr(hit | Iono,K),Pr(hit | N,K))]`.

The pure observation option value is `V_K1 - V_K0 >= 0`, with equality whenever the same action dominates every K with positive probability. This is **the value of observing deck composition alone**, conditional on both choices still being available; it does not price the search Item, Supporter timing, search payments or known deck order.

## Exact numerical witness

For D=46, P=6, U=10 unknown-zone outs, H=5, R=1 hand out, d=6 and Q=2:

| Policy | Conditional immediate access |
| --- | ---: |
| Always Iono | 74.232970% |
| Always N | 74.206755% |
| Search first, choose based on observed K | **74.401981%** |

Pure K1 option value: **+0.169011 percentage points** above the best K0 fixed decision.

The deck can contain K=4..10 outs depending on how many of U=10 are Prized. K1 chooses N when K=4..8 and Iono when K=9..10. For this specific prior, the hidden-Prize distribution places most probability at K=8..10, so the benefit of the conditional choice is real and modest.

## General interpretation

The result demonstrates an action-selection information benefit independent of any new card being fetched. When the same redraw is optimal in every hidden state, observation provides no action-switching benefit for this objective. When some hidden states favor different redraw destinations, a deck search that reveals the state can create positive option value.

This information value cannot be interpreted as net benefit of spending a connector. A real search may use a card, consume a discard payment, shuffle a known top deck, alter the hand, reveal other information and restrict what remains legal. The true sequencing choice needs those costs represented together.

## Reproducibility

- `tools/prize_informed_iono_n_choice.py`: exact Fraction-valued Prize-out prior and K0/K1 policy comparison.
- `results/prize_informed_iono_n_choice/reproduce.py`: independent exhaustive enumeration of small Prize subsets, conditional draw subsets for both destination effects, and action-choice aggregation.
- `.github/workflows/validate-prize-informed-iono-n-choice.yml`: standalone CI regression.

No whole-game strategy, match-up win rate, or tournament strength claim is made. Next useful work is to attach a real search connector whose payment, shuffled deck and possible target output are conserved, then recompute whether the information is worth its material cost.
