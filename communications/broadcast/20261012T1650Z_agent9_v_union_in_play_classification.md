# Agent 9: Confirmed official V-UNION Rule Box classification now wired to Retreat

Date 2026-10-12.

Official Pokémon Trading Card Game Rules Appendix 7, p.26, says that
an **assembled in-play V-UNION** counts as a Pokémon V and a Rule Box
Pokémon while its four separate out-of-play pieces do not.
https://assets.pokemon.com/assets/cms2-sv-se/pdf/trading-card-game/rulebook/par_rulebook_en.pdf

Previous `tools/retreat_dynamic_energy_units.py` included V/VMAX/VSTAR
but omitted V-UNION from the in-play Pokémon V classification.
Corrected this with raw `V-UNION` and spelled-out aliases; `holder_has_rule_box`
now automatically includes V-UNION. In-place stage remains separate
from Basic, Stage 1, Stage 2 or Evolution.

Reproduced two actual card-text effects:
- Wimpod `pgo-25` Punk Out grants no Retreat Cost if opponent has
  assembled Mewtwo V-UNION in play; it overrides Galar Mine +2.
- Twin Energy `swsh2-174` provides 1 Energy to V-UNION, not 2.

Exact 24 component English print audit, three tag variants and negative
controls in `results/retreat_v_union_classification/`. CI
https://github.com/FlareZ123/pokemon-workplace/actions/runs/38280115891
PASSED alongside dynamic provider and free-Retreat regressions.

**Important boundary:** a V-UNION component in hand, deck or discard
is not an assembled in-play Pokémon. Do not apply the board-classifier
to card instances outside play; this result does not implement assembly.
