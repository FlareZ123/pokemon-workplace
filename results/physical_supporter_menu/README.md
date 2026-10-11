# Exact Supporter availability and Prize information

## Scope

This model extends [three-Supporter information](../three_supporter_information_envelope/) and the [four-action Pass option](../supporter_pass_option_frontier/) by requiring a corresponding Supporter to be physically in hand. The outcome is one-step target-in-hand probability minus a hypothetical weight for the opponent's next-turn target readiness.

## Constructed physical 60-card deck

The disjoint category counts are **12 Basic Pokémon**, **4 Iono**, **4 N**, **4 Professor's Research**, **4 useful target cards**, and **32 inert filler**. The player goes second, draws seven, conditions on an opening containing at least one Basic, selects exactly one Active Basic, places six random Prize cards, and draws one ordinary turn card. At the action snapshot, the player has seven cards in hand and 46 in deck. The experiment omits mulligan bonus draws, Bench plays, Ability actions, Energy actions, additional searches and locks.

Pass is always a possible action. A Supporter may be chosen only when held; playing it removes that Supporter, leaving six old-hand cards. The hypothetical perfect K1 deck observation reveals the count K of useful outs remaining in deck. K0 knows the actual hand without K; K1 knows both. The opponent has 46 deck cards, six Prizes hiding a hypergeometric allocation of four useful outs, and a five-card hand already containing one known out. Opponent next-draw target-readiness probabilities are 44.964447% after Iono, 49.953439% after N, and 100% after Research or Pass. Opponent Prize information remains hidden to the player.

## Exact enumeration

For deck category counts n and opening composition c, the unconditioned opening probability is the multivariate hypergeometric product of binomial(n_i,c_i) divided by binomial(60,7). Conditional on a valid Basic opening, choose one Basic as Active. After Prizes, the natural draw belongs to class j with marginal probability (n_j-c_j)/53 by exchangeability; the final hand is c minus one Basic plus one j.

For a final hand with h useful targets, there are U=4-h useful cards among the 46 remaining deck and six Prize cards. The K0 posterior for remaining-deck targets is exactly P(K=k)=binomial(46,k)binomial(6,U-k)/binomial(52,U). K1 chooses the optimal physically available action for each possible k. Both policies condition on hand composition.

| Probability or count | Exact result rounded |
| --- | ---: |
| Basic-valid initial opening | **80.935331%** |
| At least one of the 12 Supporter copies in hand, conditional on valid Basic | **83.843801%** |
| At least two held Supporter copies, conditional on valid Basic | **47.707707%** |
| At least one useful target initially held, conditional on valid Basic | **42.738824%** |
| Distinct final hand compositions | **708** |

The exact additional K1 information premiums in percentage points are: lambda0 **0**; lambda0.1 **+0.006666181713**; lambda0.25 **0**; lambda0.5 **0**; lambda1 **0**; and lambda2 **+0.000072562303**.

Compared with an unrestricted menu, the conditional value of deck information can be small because only physically held Supporters may be used. The probability spaces and hand compositions differ, so results from the earlier fixed-hand examples cannot be subtracted as a controlled causal effect.

## Reproduction

- [Physical source-menu engine](../../tools/physical_supporter_menu.py) contains the rational conditional distribution and exact hand-dependent action envelope.
- [Independent regression](reproduce.py) exhaustively enumerates labeled opening cards, Prize sets, and turn draws in ten small cases, then independently evaluates legal Supporter payoffs via without-replacement draw subsets in 18 weighted small cases. It checks full probability conservation and the reported 60-card values.
- [Windows CI](../../.github/workflows/validate-agent2-physical-supporter-menu.yml) runs on Python 3.13.

The exact K1 gain is a *gross information upper bound*: a physical search effect, its availability, its card cost and its post-payment menu are omitted. The artificial deck and the opponent target proxy are neither tournament deck recommendations nor game-win-rate estimates. A higher-fidelity successor should introduce physically held and payable zero-output search with an exact opportunity-cost comparison.
