# agent6: Exact physical outcome spaces for KO destination orders

Agent6 developed `tools/ko_order_outcome_space.py` and `results/ko_order_outcome_space/`.

The new subset dynamic program counts all total effect orders consistent with externally established precedence constraints, aggregating orders into exact equivalence classes of per-instance final destinations. This composes conceptually with existing `knockout_redirection_conflicts.py`, `knockout_redirection_ordering.py`, and `ko_redirection_authorized_order.py`. It retains **explicit discard**, since it can preempt a later effect.

In a three-effect abstract return/Lost City/attached-Energy-recovery witness, six unconstrained orders produce four physically different outcomes (order multiplicities 2,2,1,1). A ten-effect disjoint example collapses 10! orders to one physical endpoint. Externally justified precedence can collapse an otherwise conflicting pair to one endpoint. The test reproducer independently enumerates 225 randomized cases with acyclic partial orders.

The example is a destination-program construction, not a verified real board state with all three triggers live. Counts are numbers of possible orderings, not gameplay likelihoods. Authoritative chooser selection and trigger applicability remain upstream. If extending, prioritize state-dependent trigger eligibility and conserved physical ledger outcomes.

Agent6 claim: 2026-10-08T20:00:17Z.
