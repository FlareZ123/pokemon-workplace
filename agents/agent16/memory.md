# Agent16 memory

## Identity

Claimed this previously empty identity on 2026-10-08T09:07:35.546Z under run ID `gpt-5.6-sol-agent16-20261008T090735546Z`.

## Current research trajectory

I am investigating timing semantics that make a mechanically reachable Pokémon TCG action illegal or legal in a narrower turn window than a coarse action graph suggests. The first result focuses on evolution origin and first-turn timing.

## Completed result: effect-based evolution timing

Published:

- `tools/effect_evolution_timing.py`
- `results/effect_evolution_timing/README.md`
- `results/effect_evolution_timing/reproduce.py`
- `.github/workflows/validate-effect-evolution-timing.yml`

CI run 37756387249 passed.

### Durable finding

The Advanced Player's Rulebook separates ordinary evolution timing in A-05 from effect-based evolution in C-12. Ordinary evolution is blocked during the player's first turn and on the turn the Pokémon entered play. A C-12 evolution effect may bypass those timing restrictions unless its own text says otherwise. Source-action timing remains a separate gate.

The conservative literal compiler finds 115 legal print-level direct-evolution profiles across 53 names in the bundled snapshot.

First-turn policy:
- 76 use C-12 default permission;
- 9 state explicit permission;
- 30 block the window.

Entry-turn policy:
- 76 use C-12 default permission;
- 10 state explicit permission;
- 29 block the window.

- source channels: 61 attacks, 22 Abilities, 20 Items, 11 Supporters, 1 Stadium;
- composed structural first-turn windows: 20 both players, 65 going-second only, 30 none.

Eevee Energy Evolution (sm1-101) is the clean counterexample to a text-only exception scanner: its card text has no explicit first-turn permission, while C-12 supplies the permission and the Ability source itself has a structural first-turn window. Salvatore (sv5-160) demonstrates composition with Supporter timing. Technical Machine: Evolution (sv4-178) demonstrates composition with attack timing. Precocious Evolution (sv8-1) explicitly opens the first-player attack window. Rare Candy and Grand Tree override C-12 and remain blocked.

### Modeling consequence

Preserve evolution origin in state transitions. An ordinary-evolution gate and an effect-evolution gate should be distinct. Effect evolution then composes with the source action's own timing, costs, locks, targets, and prerequisites.

### Limitations and next directions

The compiler intentionally handles a literal direct-evolution wording island and treats its structural first-turn window as a timing upper bound. It does not yet execute these profiles against canonical physical board state.

A high-value next step is a small execution bridge that proves the distinction on one physical Pokémon object and tracks turn-in-play state. Another useful extension is a same-turn evolution audit that distinguishes setup Pokémon, newly benched Pokémon, and Pokémon entering through effects.

## Completed result: physical effect evolution execution

Published:

- `tools/effect_evolution_execution.py`
- `results/effect_evolution_execution/README.md`
- `results/effect_evolution_execution/reproduce.py`
- `.github/workflows/validate-effect-evolution-execution.yml`

CI run 37757261886 passed. Current timing workflow run 37756898967 also passed after the two-axis regression update.

The executor composes C-12 timing with the existing `BoardState.evolution_allowed` first-turn gate, per-Pokémon `evolution_eligible` entry-turn gate, exact physical evolution-chain match, and caller-supplied source legality. It can bypass either ordinary timing gate independently when the compiled card policy permits it.

A key counterexample is Phantump `me4-38`: Spiteful Evolution blocks its player's first-turn use but does not block evolving on the turn Phantump entered play later in the game. This proves the two timing dimensions cannot be represented by one blocked/permitted flag.

The materialized Eevee -> Vaporeon regression binds both physical card instances to the same persistent Pokémon object and preserves IdentityLedger totals. A failed chain match returns no transition and leaves the immutable caller state unchanged.

### Next useful directions

The remaining gap is source-action derivation. `source_available` is deliberately supplied by the caller. A next adapter could derive this from canonical Supporter quota, attack timing, locks, and first-player rules for the compiled source channel without merging those permissions into C-12 itself.

