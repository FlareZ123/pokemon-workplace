# Agent 9: Goodra Slimy Sliding stochastic Retreat gate

Date: 2026-10-12. Source: Chaos Rising Goodra `me4-68`, plus official
Japanese rulings for the failed action and Dashing Pouch.

Exact state-aware code is now at `tools/retreat_goodra_coin_gate.py`
with a physical reproducer and result narrative at
`results/retreat_goodra_coin_gate/`.
CI: https://github.com/FlareZ123/pokemon-workplace/actions/runs/38279081110
(PASS).

One printed Goodra Ability applies a single coin flip when the opponent
attempts ordinary Retreat, even if its effective cost is zero. Heads
executes normal Retreat, including Dashing Pouch. Tails preserves
Active, attached Energy, Tool, physical instance classes and zones,
while consuming the canonical once-per-turn Retreat quota. Two Goodra
do not cause multiple flips. Effect-based Switch does not incur this
gate. The exact branch weights are 1/2 and 1/2 under ordinary coin
rules.

Full canonical Retreat actions are deterministic; this wrapper yields
two immutable weighted outcomes around those validated actions.
Ability suppression state is explicitly projected, not inferred from
raw card names.

This is a confirmed mechanical rule and a constructed physical-state
test, with no deck strength or win-rate implication. Routing stochastic
Retreat outcomes into opponent modeling and policy-based line choice is
an open research direction.
