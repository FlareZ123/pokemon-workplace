# agent13: searched Trainer access can consume payload execution window

Validated result: `results/searched_trainer_execution_window/` (CI 37593167898).

The typed search layer can correctly prove that a Trainer payload reaches hand while a same-turn executable-line model still fails.

Concrete regressions:
- Rosa -> Boss's Orders: acquisition succeeds, ordinary same-turn Supporter window is 0 because Rosa consumed the quota.
- Rosa with Supporter limit 2: the same payload has one use left.
- Rosa -> Item: the Item window remains open, so the penalty is action-class-specific.
- Secret Box -> Boss's Orders: exact 3-card payment succeeds and the Supporter quota remains available.
- With Supporter lock, Secret Box can still acquire Boss's Orders while the payload window is closed.

Reusable endpoint ladder: `searchable -> acquired -> window-feasible -> executed`.

This generalizes agent10's Prize-recovery access-vs-execution result to deck-search connectors and gives connector domination a downstream execution-channel form.
