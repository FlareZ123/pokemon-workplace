# agent9: Source-aware Ability/Stadium Retreat Cost

Validated an additive Retreat modifier layer at `tools/retreat_environment_modifiers.py`,
composed into `tools/board_derived_retreat.py`, with exact-board regression
`results/retreat_environment_modifiers/reproduce.py`.

Supported sources: Galar Mine (`swsh2-160`, +2 to both Active);
opponent Ariados Big Net (`sv6-5`, +1 to Active Evolution);
friendly Benched Hisuian Sneasler Carry and Climb (`swsh10-93`, -2).
An exact staged transaction proves one DCE Retreat succeeds at cost 2 with
Sneasler but fails at cost 4 when the same Sneasler is absent.
Two Ariados instances stack; Float Stone overrides additive increases.
Workflow `validate-retreat-environment-modifiers.yml` succeeded
(run `37836767519`).

Scope warning: `abilities_enabled` is an already-resolved suppression fact;
`stadium_print_id` / `stadium_effect_enabled` are passed explicitly.
This only compiles three exact prints; further Stadium/Ability and attack
duration sources remain external. Please reuse the narrow resolver rather
than treating these effects as arbitrary signed integers.
