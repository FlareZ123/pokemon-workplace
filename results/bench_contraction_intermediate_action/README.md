# An intervening Lunar Cycle breaks physical Bench-contraction confluence

## Question

Pure forced Bench contractions can be merged by their final survivor set. Does that remain valid if a player takes a legal resource-changing action after the first contraction and before the second?

**No.** A print-specific Lunar Cycle witness leaves the same final Pokémon, evolution stacks and attachments on the board, but produces a different hand, deck and discard-pile state.

Implementation: `tools/bench_contraction_intermediate_action.py`.  
[Passing GitHub Actions run 38132398998](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38132398998).

## Printed card and rules basis

The bundled `cards/en/me1.json` record `me1-74`, Lunatone, has the Ability **Lunar Cycle**:

> Once during your turn, if you have Solrock in play, you may discard a Basic Fighting Energy card from your hand in order to use this Ability. Draw 3 cards. You can't use more than 1 Lunar Cycle Ability each turn.

The fixture uses a source-specific `me1-74` materialized Lunatone card and `pgo-39` Solrock card. A Basic Fighting Energy begins in hand, and three explicitly modeled exchangeable cards begin in deck. The ability-use function checks both in-play print presences and the payment before moving the Fighting Energy to discard and three cards from deck to hand. The caller must guarantee the use has not already occurred this turn and that no disabling lock applies.

The first and second physical contractions reuse the validated full-stack `contract_with_choice` transition. They are abstract authorized capacity-change events; a complete turn scheduler must separately enforce Stadium play quotas and the actual sequence of turns.

## Explicit physical witness

The original five Bench objects are:

- `pair-a`: evolved Tarountula → Spidops, with a physical Grass Energy and Muscle Band attached;
- `pair-b`: Solrock `pgo-39`;
- `extra1`: Lunatone `me1-74`;
- `extra2`: Regirock;
- `extra3`: Regice.

The Active Bidoof remains unchanged.

**Staged route with an action**

1. Reduce capacity from five to four, discarding Regice (`extra3`).
2. With both Lunatone and Solrock still in play, use Lunar Cycle: discard one Basic Fighting Energy, draw three cards.
3. Reduce capacity from four to three, discarding Lunatone (`extra1`).

**Direct route with no preceding action**

1. Reduce capacity from five to three, discarding Regice and Lunatone.
2. Lunar Cycle is now unavailable because Lunatone is no longer in play.

Both routes leave precisely the same three Benched Pokémon: Spidops, Solrock and Regirock. The evolved Spidops retains all of its materialized cards and the full materialized instance sets agree.

However, the staged route's exchangeable counts contain one Fighting Energy in discard and three newly drawn cards in hand. The direct route still contains one Fighting Energy in hand and three cards in deck. Their complete `StackBoardMaterialState` objects are unequal. Every card-class total is conserved in both.

## Tested invariants

The standalone regression verifies:

- the two routes have exactly equal physical boards and equal remaining materialized card instances;
- their exchangeable zone-count distributions are different;
- the staged action requires a printed Lunatone and Solrock in play plus the Basic Fighting Energy payment;
- the payment can be made only once in this small fixture because the one available Basic Fighting Energy is consumed;
- the direct-route post-contraction action correctly fails;
- full per-card-class conservation holds in both routes.

All checks passed CI run **38132398998**.

## General lesson and limits

An optimizer may safely merge pure contractions only after accounting for intervening actions, available resources and changed activation conditions. Equivalent final visible Bench geometry is a weaker condition than equivalent resource and history state.

This particular witness proves a *conditional possibility* under explicitly supplied authorized action windows. It is not a tournament-frequency or deck win-rate statement. The scripted action does not validate entire turn history, competing Abilities, opponent interaction, lock removal, conditional choice of drawn cards, or random deck order. Those belong to larger simulators.

Related result: [bench_contraction_physical_confluence](../bench_contraction_physical_confluence/) proves and tests the exact state-merging boundary **without** intervening actions.
