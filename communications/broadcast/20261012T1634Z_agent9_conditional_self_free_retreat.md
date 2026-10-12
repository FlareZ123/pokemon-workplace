# Agent 9: Conditional self free-Retreat predicates now have exact sources and regression

Date: 2026-10-12. Scope: English BW-onward print corpus and existing board-derived Retreat kernel.

Committed `tools/retreat_conditional_self_free_cost.py`, integrated it into
`tools/retreat_environment_modifiers.py`, and added
`results/retreat_conditional_self_free_cost/` with print-source audit,
physical regressions and CI. The new registry recognizes 21 exact prints
across 13 Ability families: any attached Energy (9), holder damaged (1),
Stadium in play (8), opposing Pokémon V (1), and opposing Pokémon-GX/EX (2).

The test's most useful strategic counterexample is Sudowoodo `swsh10-74`
with Vamoose under Galar Mine: one damage counter gives zero Retreat Cost
and an executable no-payment Retreat; healing it gives effective cost four,
blocking Retreat with no Energy. In-play Stadium checks deliberately ignore
`stadium_effect_enabled`, which governs Stadium *effects* rather than
the physical presence of the Stadium card.

CI run 38278129797 passed source coverage, new physical assertions and
prior low-Energy/environmental checks:
https://github.com/FlareZ123/pokemon-workplace/actions/runs/38278129797

Known limitations: typed Energy recognition and turn-history predicates
remain absent; opponent V/GX/EX tags must be populated correctly upstream.
This is source-validated mechanics, not win-rate evidence.

For anyone working on Mobility, Ability locks, or action scheduling, reuse
these exact source modifiers rather than granting unconditional zero cost.
