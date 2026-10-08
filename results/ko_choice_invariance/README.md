# Three levels of invariance in sourced Knock Out choices

## Research question

If a Pokémon TCG effect-order choice is disputed, under what conditions does the disagreement matter to a state evaluator?

`tools/ko_choice_invariance.py` combines the source-aware zero-sum choice solver with the independently validated conserved terminal-state histogram, producing three separate invariance assessments:

1. **Value invariance:** every resolved source-conditioned player optimum has exactly the same caller-defined utility score.
2. **Physical-instance-route invariance:** all source-optimal, potentially tied physical destination vectors are identical.
3. **Conserved terminal-state invariance:** all those vectors produce the same card-class zone histogram once Knocked Out cards become exchangeable.

All conclusions are conditional on the rules sources that actually yield a complete chooser, the caller's payoff, a fixed pending KO batch, one promotion, and the repo's destination-only cleanup transition. Any unresolved sources are enumerated by ID. With zero resolved sources, the three answers are **unknown**.

The source-choice solver was extended to retain **all tied-optimal physical outcomes** for each source. Its older `best_outcome` field remains as one deterministic witness, while `optimal_outcomes` preserves the full set. This avoids misreporting physical certainty when multiple endpoints carry equal utility.

## Exact examples

### Aegislash versus Tyranitar-GX

The official Japan Aegislash/Lost Out Q&A permits the Knocked Out Aegislash's owner to choose order, while February 2026 TPCi Professor guidance identifies the current player as chooser of multiple KO triggers. Their source relationship remains a separate policy issue, recorded in [tyranitar_aegislash_authority](../tyranitar_aegislash_authority/).

Using the illustrative defender utility **number of evolutionary stack cards returned to hand**:

- The Japan-profile defender chooses Durable Blade first, gaining three cards.
- The TPCi-profile attacker chooses Lost Out first, recovering zero cards for the defender.

Across individually selected source profiles, **value, instance-route, and terminal-state invariance are all false**. This example supplies a physical witness that resolving the authority source can alter card access.

If a caller assigns equal payoff to both destinations, value becomes invariant but both physical endpoints remain available because each chooser is indifferent. That gives a concrete case of **value invariance without physical invariance**.

If the same player is both current-turn player and Aegislash owner, the sources agree on the concrete chooser, whose strict utility preference selects the same return-first order. All three invariances hold in this state, even though the abstract source-policy precedence remains undecided.

### Two equivalent Basic Water Energy copies

A synthetic two-effect construction sends one of two physically distinct Basic Water attachments to hand and the other to discard, with the instance assignments reversed between programs.

Under an explicitly equal-payoff policy, both instance destination vectors remain possible. The chosen source and payoff are the same, so value invariance holds. The two instance vectors differ, so instance-route invariance fails. After dematerialization, both terminal states contain one Basic Water Energy in hand and one in discard, with identical surviving board and all other card zones. **Conserved terminal-state invariance holds.**

This is a representation-level test of identity loss after card copies become exchangeable. It does not represent a verified co-triggering real-world pair.

### Missing source authority

The bundled Advanced Player's Rulebook v3.4 only explicitly assigns current-player authority when several Pokémon are Knocked Out simultaneously, so that narrow source alone yields no applicable chooser for the single-Aegislash scenario. All three certificates are `None` (unknown), and the source is listed as unresolved.

## Reproduction

`python results/ko_choice_invariance/reproduce.py` checks the above examples, verifies physical card conservation, then constructs **110 deterministic random destination-program sets** over the actual Aegislash materialized KO board. The code gives every order equal caller utility under one source, making all order endpoints optimal. For every case, it compares the claimed number of distinct terminal histograms and terminal invariance with the independently executed full physical KO disposal states.

## Interpretation

The hierarchy is useful to pruning and decision algorithms:

- A stable utility value alone can justify **value-level** pruning for that exact objective.
- A stable conserved terminal state can justify **full-state** coalescence in the fixed-batch destination-only kernel, provided the chosen card-class equivalence relation is valid.
- State invariance cannot be assumed when earlier effects can modify the surviving board, trigger new effects, reveal information, or change future action budgets.

The result does not claim all admissible effect orders are equally likely. When actual players control order, indifference may leave multiple physical endpoints possible. Robust evaluation should retain that choice set or introduce an explicit policy model with justified tie-breaking.
