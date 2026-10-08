# Current Stadium Tool effects and Retreat prohibitions

## Question

A board-level Tool may change Retreat Cost, redirect discarded Energy, or
protect its holder from an opponent's Ability. What happens when Jamming
Tower disables those Tool effects, and can the existing Retreat executor
apply the consequences consistently?

## Source text

The bundled paper Expanded card corpus contains three exact Jamming Tower
prints: `sv6-153`, `sv10-243`, and `me2pt5-261`. Their rules text makes
Pokémon Tools attached to either player's Pokémon have no effect.

Stealthy Hood `sm10-186` protects its holder against opposing Pokémon
Abilities. In the model, that prevents opponent-origin continuous
Retreat prohibitions from affecting the holder when the Hood effect is
active. This is a direct card-text interpretation. A specific
Hood-versus-Block ruling was not located in this investigation.

## Implementation

`tools/retreat_stadium_tool_overlay.py` produces temporary board projections
for the three exact Tower prints. With an effective Jamming Tower in play,
it marks currently functional attached Tool effects inactive on both boards,
without removing the physical Tool cards. The helper reports affected
Tool instance IDs.

`tools/board_derived_retreat.py` now normalizes physical Energy, applies
the Tool overlay, then projects continuous Ability suppression. All subsequent
cost, denial, and destination checks consume the projected source state.
The pending Retreat transaction uses the corrected own-board Tool effect
flags, so Dashing Pouch cannot redirect Energy while Jamming Tower is live.

The committed physical state and the returned pre-action normalization retain
the prior Tool-effect baseline. The temporary Stadium overlay is undone after
the internal action is resolved, and is recomputed for each future decision
from its current Stadium input. This prevents a removed Jamming Tower from
silently leaving all previously suppressed Tools disabled. The regression
checks that a zero-cost Float Stone Retreat becomes available again directly
from the failed Tower-attempt's returned normalized physical state.

`tools/retreat_ability_denial.py` consults the already existing
`stealthy_hood_protects_from_opponent()` predicate. An active Hood
prevents opponent-origin continuous Ability Retreat prohibitions. Jamming
Tower blanks the Hood's effect first, so a still-active Snorlax Block
restriction applies normally.

## Distinguishing tests

- All three Jamming Tower prints remove Float Stone's no-cost modifier:
  a cost-2, zero-Energy Retreat changes from legal to illegal.
- If the Stadium's own effect is disabled, the Float Stone line remains legal.
- Dashing Pouch normally returns a physically paid Double Colorless Energy
  to hand. Under Jamming Tower the same copy is discarded instead.
- Jamming Tower cancels an opposing Active Gravity Gemstone's +1 Retreat
  Cost, allowing a base-zero Pokémon to Retreat without Energy.
- An Active wearing Stealthy Hood can normally Retreat through opposing
  Snorlax Block when physically able to pay. Jamming Tower disables Hood,
  restoring the prohibition.
- Source-disabled Tool effect flags produce the same Hood lock status.

## Limits

The adapter accepts an exact currently active `stadium_print_id` and
`stadium_effect_enabled` flag. It does not infer the Stadium zone
or calculate Stadium cancellation from other effects. Its result is a
current-state projection; retaining suppressed Tool flags after a
Stadium change would be stale and requires a subsequent rederivation.

Tool-protection scope is limited to opponent-origin Ability effects on the
holder. Other Tool blocking, Tool attachment legality, and copied effects
are outside this module.

The existing causal Ability-lock graph must be evaluated with Stadium
effects already considered (for example, Jamming Tower can remove Hood
protection and change lock dependency edges).

The exact Stealthy Hood card text is also available from the
[official Japanese Pokémon card database](https://www.pokemon-card.com/card-search/details.php/card/36191/regu/all).
The [official Japanese Block Snorlax entry](https://www.pokemon-card.com/card-search/details.php/card/41737/regu/BW)
confirms that its prohibition applies to the opponent's Active Pokémon.

Reproduce with `python results/retreat_stadium_tool_overlay/reproduce.py`.
