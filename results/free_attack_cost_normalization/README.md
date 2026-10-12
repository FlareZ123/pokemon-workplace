# Zero-Energy attack glyphs are encoded inconsistently in two Expanded-legal prints

## Finding

A scan of the bundled English card snapshot finds **two** Pokémon attacks whose
printed-energy `cost` is the non-Energy string `["Free"]`, while
`convertedEnergyCost` incorrectly equals **1**:

| Card ID | Pokémon | Attack | Raw cost | Raw converted cost | Rule-correct cost |
| --- | --- | --- | --- | --- | --- |
| `sv8pt5-4` | Budew | Itchy Pollen | `["Free"]` | 1 | **0** |
| `me1-71` | Tyrogue | Pow-Pow Punching | `["Free"]` | 1 | **0** |

The [published Budew Prismatic Evolutions reprint](https://limitlesstcg.com/cards/PRE/4)
has an attack explicitly displayed with zero Energy, and its
[Ascended Heroes reprint](https://limitlesstcg.com/cards/ASC/16)
has exactly the same attack text. The latter is represented by
`me2pt5-16` in the provided database with `cost: []` and converted cost 0.
The [Mega Evolution Tyrogue printing](https://limitlesstcg.com/cards/MEG/71)
also explicitly displays **0** printed Energy for Pow-Pow Punching.

This issue directly affects 2026 Aichi Regidrago evaluations: all nine
published Regidrago lists include Budew, and its Itchy Pollen is a crucial
zero-Energy attack-history cover plus Item-lock effect.
An experiment using raw `convertedEnergyCost` or treating every `cost`
element as a typed Energy symbol can falsely reject the executable line.

## Reproduction and repair boundary

- [Reusable read-only normalizer](../../tools/free_attack_energy_normalizer.py) maps the exact `("Free",)` sentinel to the empty Energy-symbol sequence, and computes a normalized printed-cost count.
- [Single-file test](reproduce.py) searches the complete supplied English card pool, proves the two known identities are the only `Free` entries in this snapshot, checks the source raw fields, confirms identical Budew attack text across prints, and preserves ordinary Regidrago Apex Dragon's **Grass, Grass, Fire** cost.
- A Windows GitHub Actions workflow reruns the test against the repository's pinned card-pool files.

Raw input files are left unchanged to preserve provenance. Consumers should
use a normalization boundary *before* deciding attack Energy requirements.
This corrects **printed cost only**; the game still must process temporary
Energy cost modifications, attack restrictions, Special Energy provision,
turn timing, and card-specific effects independently.

## Evidence status

This is a reproducible **data-quality and rules-semantics finding**, backed
by source-card print records and matching rendered zero-Energy attacks.
It does not show that the current Twinleaf engine has this bug; that requires
inspection of its actual attack-cost parser, which is a separate action.

## Integrated exact Energy readiness check

The original exact `tools/energy_action_budget.py` route evaluator rejected an empty printed cost with `ValueError`, even though an empty cost means an Energy-free attack under the rules. This blocked even a correctly normalized Budew. Commit (2026-10-12) removes that nonempty precondition while preserving all type/capacity checks. For a zero-Energy input and zero routes, the evaluator already correctly derives `exact_feasible=True`, `typed_resource_ignorant_feasible=True`, `raw_unit_count_reachable=True`, `minimum_unmet_symbols=0` and an empty executable witness.

[The integrated regression](energy_readiness_reproduce.py) verifies both variants of Budew, Tyrogue, optional surplus Energy actions and negative Regidrago Apex Dragon readiness. The integration's GitHub Actions workflow runs the **pre-existing full Energy action budget SFT** as an additional regression. This is a narrow extension of a proven deterministic route evaluator, rather than a claim that all game-engine attack-cost paths already use this helper.
