# The cost of not knowing whether an opponent holds Enhanced Hammer

## Question

How can hidden opponent counterplay change a resource-discard decision when its future attack-readiness outcome is known conditionally?

The source-backed [Regidrago / Dragon Impact witness](../energy_discard_continuation_frontier/) and [opponent-response result](../energy_discard_continuation_disruption/) already establish the material outcome. The player decides whether to discard one DDE or two Basic Energy cards before knowing whether the opponent can neutralize DDE with **Enhanced Hammer** (`sv6-148`).

A transparent two-world utility model quantifies why the optimizer must choose a payment using only presently available information.

## Controlled model

After copied Dragon Impact:

- **A: discard DDE**. Retains three Basic Energy cards; immediately cannot pay next Apex Dragon cost. Enhanced Hammer then has no DDE target in this isolated board.
- **B: discard two Basics**. Retains one Basic and DDE; pays next Apex Dragon cost unless the opponent successfully Enhanced Hammers DDE before the next attack.

Assume that the opponent counter will succeed with an **exogenous probability `q`**, no recovery or hand Energy attachment intervenes, and the attacker survives. The counter state is learned only after the payment is committed.

For this one-step toy model, assign:
- value `W ≥ 0` to being Energy-ready for one next attack;
- value `v ≥ 0` per Basic Energy still attached;
- value `s ≥ 0` to the retained DDE when the opponent cannot remove it.

The utility values are **hypothetical analysis weights**. They are not inferred from competitive gameplay.

## Exact decision and information value

Without observing the opponent counter state, the choices have expected values

`E[U(A)]=3v`

`E[U(B)]=v + (1-q)(W+s)`.

An advance-commitment policy selects the larger. It prefers B when `(1-q)(W+s)>2v`; if `W+s>0`, this means `q < 1-2v/(W+s)`.

With a hypothetical perfect signal about whether Enhanced Hammer will be successfully used **before** making the payment, the upper-bound value is

`V_perfect=(1-q)*max(3v, v+W+s) + q*max(3v,v)`.

The **value of perfect information** is

`V_perfect - max(3v, v+(1-q)(W+s))`.

With illustration-only weights `W=10`, `v=1`, `s=0`, the advance policy switches at `q=4/5`. At that point it values either payment at **3**. A fully informed policy has expected value **23/5=4.6**, yielding perfect information value **8/5=1.6**. The excess is the cost of choosing before knowing the opponent's response in this utility model.

This is the same nonanticipativity phenomenon as the synthetic future-attack-cost theorem, now represented using one exact opponent counter card and the Regidrago payment witness.

## Verification

`tools/energy_discard_counter_information_value.py` implements exact rational arithmetic with `fractions.Fraction`, checks the no-information action optimum against the perfect-information upper bound across **378** probability/utility configurations, and asserts the worked illustration.

Run `python -m tools.energy_discard_counter_information_value` from the repository root.

## Limitations

Neither `q` nor the utility weights are metagame estimates. Opponents pay their own action/Item costs, may lack a legal Hammer target, may have ability/Item locks, or may prefer another line. Subsequent manual attachments, Legacy Star, Stadium replacement, attacks, prizes, and Knock Outs are outside the model. In real play, the opponent's hand information can be partially inferred rather than perfectly known or completely hidden.

The result is a small demonstration of how to keep the information available **at payment time** separate from what becomes visible later.
