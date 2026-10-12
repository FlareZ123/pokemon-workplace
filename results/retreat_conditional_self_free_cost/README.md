# Conditional self free-Retreat Abilities: 21 verified prints and state reversals

## Finding

The bundled English BW-onward card corpus contains **21 source prints in
13 distinct Ability families** matching five conservative, machine-readable
conditions under which the source's own Pokémon has **no Retreat Cost**:

| Current-state predicate | Prints | Example |
| --- | ---: | --- |
| Any Energy card attached | 9 | Pikachu, Pika Dash (`swsh11-52`) |
| Has any damage counters | 1 | Sudowoodo, Vamoose (`swsh10-74`) |
| A Stadium card is in play | 8 | Alolan Raichu, Surge Surfer (`sm4-31`) |
| Opponent has a Pokémon V | 1 | Wimpod, Punk Out (`pgo-25`) |
| Opponent has Pokémon-GX or Pokémon-EX | 2 | Genesect, Fast-Flight Configuration (`sm10-127`) |

These are *additional* to the existing
[low-attached-Energy threshold registry](../retreat_low_energy_no_cost/),
which handles the opposite condition of having no or at most two Energy
units attached.

Source-pool coverage is audited against the supplied print JSON, using
the database's Expanded field only to exclude pre-BW records. This does
**not** independently certify tournament legality or absence from a
current paper Expanded ban list. Source IDs and text must still be
checked against official rulings when an individual print is disputed.

## Mechanics and integration

`tools/retreat_conditional_self_free_cost.py` compiles only those exact
source IDs, printed names, and conditions. It reads the *live* Active
Pokémon, the current opponent board, and current Stadium presence.
It reuses the shared Pokémon V / GX / EX tag classifiers and returns
`RetreatCostModifier(no_retreat_cost=True)` only when the source's
Ability is enabled and its predicate is satisfied.

`tools/retreat_environment_modifiers.py` now composes these sources
with previously supported Galar Mine, Big Net, Sneasler, and
low-attached-Energy sources. The existing retreat-cost algebra gives
the zero-cost result priority over numeric increases and reductions,
consistent with the supplied Advanced Player's Rulebook §D-13.

A Stadium-presence predicate reads `stadium_print_id is not None`.
It deliberately does not require `stadium_effect_enabled=True`.
A stadium with suppressed effects remains an in-play Stadium card
unless a separate action actually removes it. This condition is
different from applying the Stadium's own printed Retreat modifier.

Abilities on an opponent can change a condition without changing
anything on the Retreating Pokémon. The condition must be derived anew
after Knock Outs, switching, evolution, or other board changes; it
must never be cached as a permanent property of the Active Pokémon.

## Constructed physical witness: healing strands Sudowoodo

Construct a board with Sudowoodo `swsh10-74` Active and Pivot Benched,
Galar Mine `swsh2-160` in play, no attached Energy, and no other relevant
effects. Sudowoodo's printed Retreat Cost is two.

- With one damage counter on Sudowoodo, Vamoose makes the effective
  Retreat Cost zero, so the Retreat-to-Pivot action with no payment is
  executable.
- If that single damage counter is removed, Vamoose deactivates.
  Galar Mine adds two to the printed two, so the effective Retreat Cost
  becomes **four**. With no attached Energy, no normal Retreat-to-Pivot
  action remains executable.

The regression instantiates both physical boards and uses the
repository's complete board-derived Retreat action enumerator. It
checks the actual committed action set, not merely a scalar cost.
The healing event is an explicit scenario input; the regression does
not claim any specific healing card has been accessed.

Additional predicates verify that Wimpod responds to the opponent's
Pokémon V / VSTAR and that Genesect responds to GX / EX, but not V;
disabled Abilities and mismatched printed identities produce no free
Retreat. The Alolan Raichu fixture checks that a Stadium with disabled
*Stadium effects* still satisfies an in-play Stadium requirement.

## Reproduction and evidence

- `source_audit.py`: independently scans the English source JSON;
  requires exact equality between detected print records and compiled
  source IDs, Ability names, and trigger categories.
- `reproduce.py`: evaluates positive and negative cases for all 21
  prints, suppression and mismatched-print guards, the Sudowoodo
  physical action frontier, opponent-dependent conditions, and
  Stadium presence without Stadium effects.
- `.github/workflows/validate-retreat-conditional-self-free-cost.yml`:
  runs these regressions together with the earlier low-Energy and
  environmental modifier regressions.
- [Passing CI run 38278129797](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38278129797).

**Evidence level:** exact printed-text compilation, deterministic
state-transition/regression tests, and an explicit constructed
counterexample. No frequency model, full-game simulator, opponent
policy, or matchup win-rate claim is made.

## Boundaries and next work

Typed attached Energy requirements, first-turn-only free Retreat,
Bench-wide granting Abilities, and printed attack effects are not
covered by this new self-predicate registry. `stadium_print_id`
and opponent class tags remain upstream state inputs; incorrectly
materialized tags may produce the wrong predicate. A practical next
integration is source-validated typed-Energy free-Retreat conditions
that distinguish the type an attached Energy provides from the
number of units it provides, followed by live opponent-board
changes and Ability-suppression feedback.
