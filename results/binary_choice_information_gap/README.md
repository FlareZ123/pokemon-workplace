# Binary action-choice information value is a disagreement gap

## Result

For any pair of actions A and B with state-dependent payoffs `a_s` and `b_s`, and a normalized belief distribution `p_s`, the benefit of observing the state *before choosing* rather than committing to one fixed action is

`V = E[max(a,b)] - max(E[a], E[b])`.

The exact **binary disagreement-gap identity** is

`V = (E[|a-b|] - |E[a-b]|) / 2`.

The identity is independent of Pokémon card effects, including the monetary or strategic units used for the payoffs. It follows immediately by substituting `max(a,b) = (a+b+|a-b|)/2` into the first expression.

The representation separates two state-uncertainty statistics:

1. `E[|a-b|]`: the average magnitude of state-dependent action preference.
2. `|E[a-b]|`: the average preference if the player cannot adapt to the state.

The benefit of information is exactly half of the excess disagreement over the fixed preference.

## Consequences for search and strategic information

- If one action weakly dominates in every state that can occur, both terms are equal and information has **zero action-switching option value**, even though the information may be tactically interesting for other reasons.
- If hidden states favor opposing actions, `E[|a-b|]` may exceed `|E[a-b]|`, giving positive option value. Both the magnitude of action preferences and how belief mass is distributed matter.
- If a paid search changes the hand, deck or action set, recompute these two terms **after the payment**. Using a static reward for the observation before paying can be wrong.

This is an identity for **exactly two** candidate actions and a specified payoff. More than two actions require their own envelope calculation rather than naively extending the absolute-difference formula.

## Exact Pokémon TCG Expanded witness

The [Prize-informed Iono/N comparison](../prize_informed_iono_n_choice/README.md) uses a hypergeometric prior over deck outs. For D=46 deck cards, P=6 hidden Prize cards, U=10 useful unknown-zone outs, H=5 old-hand cards with one known out, d=6 Prize-card-dependent redraw and two cards in the opponent's hand:

- Expected difference `E[P_Iono - P_N]`: **+0.026215 percentage points**.
- Expected absolute difference `E[|P_Iono - P_N|]`: **0.364237 percentage points**.
- Half their difference: **+0.169011 percentage points** exact K1 action-choice option value.

After a hypothetical zero-target Quick Ball payment consumes two non-outs from that five-card old hand, N dominates Iono at every feasible deck-out count K=4..10. The two disagreement statistics become equal, and the choice-information value becomes exactly zero.

These are target-access probabilities under a specified model. Deck searches may have other informational or material benefits beyond selecting between these two Supporters.

## Reproducibility

- `tools/binary_choice_information_gap.py`: reusable Fraction-valued belief distribution helper.
- `results/binary_choice_information_gap/reproduce.py`: 5,120 exhaustive exact two-state examples with varying beliefs and action payoffs, independent direct max-policy calculations, plus the Iono/N before/after-payment witnesses.
- `.github/workflows/validate-binary-choice-information-gap.yml`: CI validation.

This theorem is a generally useful diagnostic for AMR, K0/K1 and connector-domination research. A search action's value arises from the changes it permits in later decisions. Information that leaves the best action unchanged under the chosen objective has no additional action-switching value in that projected decision.
