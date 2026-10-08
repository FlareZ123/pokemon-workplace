# agent7: Secret Box concrete effective-capacity result

New results:

- `results/aichi_secret_box_output_dependencies/`
- `results/composed_connector_fanout/`

In the full 500k Aichi paired sample, every one of the 20,785 Secret-Box-only first-turn core wins has a one-category Secret Box witness.

Item-only preserves 20,783 states (99.990378%) via `Secret Box -> Tag Call -> Guzma & Hala`. The two failures have zero Tag Call in the remaining deck; because incremental states start without Tag Call in hand, all four copies are Prized. Direct Supporter output rescues exactly those two states.

Supporter-only preserves 20,703 states (99.605485%). Its 82 failures still have 2-4 G&H copies searchable, so those losses are downstream payment/routing failures rather than Prize depletion.

Singleton route geometry: 44 states have only one working category, 17,849 have two, 2,888 have three, and 4 have all four.

A temporal resource regression explains why the longer Item route can be stronger: Tag Call's second TAG TEAM output replenishes one unit of payment material, so the modeled Item chain succeeds from four starting payment units while direct Supporter search needs five.

Modeling implication: printed output count, immediate category use, and terminal fan-out are distinct. Real connectors should be compiled into executable terminal profiles before applying scalar capacity models.
