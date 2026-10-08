# Signature-compressed conserved KO order analysis

## Motivation

`ko_order_outcome_space.py` enumerates distinct explicit per-instance destination vectors. `ko_order_terminal_projection.py` runs the physical KO cleanup once for every vector, grouping terminal states afterward. `ko_order_zone_signature.py` proved a more efficient equivalence test for route-only effects on a fixed pending board.

The new `tools/ko_order_signature_projection.py` composes these layers: it groups instance route outcomes by canonical `(card_class, zone, count)` signatures **before** running the full physical disposal, then executes that disposal only once per unique signature.

## Correctness boundary

For one unchanged pending Knock Out batch, all removed cards are dematerialized into exchangeable card-class zone counts, and survivors remain identical across destination-only alternatives. The histogram signature therefore identifies the full terminal state under fixed promotion. A signature bucket can be represented by one disposed witness while summing the exact numbers of constrained total orders from all its instance-level route members.

No ordering authority, trigger coexistence, or future strategic value is inferred. The choice of card-class resolution in the identity ledger is an explicit prerequisite for sound aggregation.

## Results

The two-Water witness has two different instance destination vectors, two effect orders and one exchangeable terminal state. The full projector performs two Knock Out disposals; the signature-compressed projector performs **one**, returning the same terminal state and exact order multiplicity.

The Aegislash return/Lost City/selected Water recovery abstract witness has four distinct terminal outcomes from six effect orders. Both projectors agree. An externally supplied precedence constraint can reduce the outcome set to one.

A deterministic 120-case randomized regression constructs one-to-five effect programs over the actual materialized Aegislash pending-KO board, samples destination assignments and acyclic precedence constraints, then compares all `TerminalOutcome` records from the compressed implementation with those from the independent full-disposal implementation. It also counts the full executor calls avoided by signature grouping.

## Reproduce

Run `python results/ko_order_signature_projection/reproduce.py`. The GitHub workflow `validate-ko-order-signature-projection.yml` runs the same test.

The dominant saving depends on how often distinct physical instance routes collapse under the gameplay-equivalence classes in use. This model measures disposal-call reduction, not wall-clock performance or actual game win probability. A future extension could produce strategic outcome-equivalence signatures that additionally preserve information history and active player action budgets.
