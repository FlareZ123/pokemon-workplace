# Bench release value depends on the entry deadline

## Question

An attack can reclaim a Bench slot, but attacking ends the turn. Does that make attack-based Bench release strategically useless?

Only when the required replacement Pokémon must enter before the current attack boundary. Once the Bench-entry requirement moves to the player's next own turn, an attack release can preload free capacity for that future turn.

This result adds an explicit earliest-entry turn and deadline to the typed Bench-release execution work.

Implementation: `tools/bench_release_deadline_geometry.py`  
Regression: `results/bench_release_deadline_geometry/reproduce.py`

## Deterministic planner result

The starting board has a full five-Pokémon Bench containing one spent support Pokémon.

Two entry timings are modeled:

- **current-turn entry**: the required Pokémon is already available and must be Benched this turn;
- **next-turn entry**: the required Pokémon only becomes available on the player's next own turn and must be Benched then.

| Scenario | Result |
| --- | --- |
| deterministic Item release, current-turn entry | succeeds |
| Supporter release, current-turn entry | succeeds when no second current-turn Supporter is required |
| attack release, current-turn entry | **fails** |
| attack release, next-turn entry + next-turn required Supporter | succeeds |
| Supporter release now, next-turn entry + next-turn required Supporter | succeeds |
| attack release + distinct required current-turn attack | **fails** |
| release attack itself satisfies current attack objective | succeeds for next-turn entry |
| Item release + distinct current-turn attack | succeeds for next-turn entry |

The attack case changes value solely because the requirement crosses a turn boundary. The release attack ends the current turn, yet the empty Bench slot persists. On the next own turn, the Supporter quota resets, so a required Supporter and the newly available Bench entrant can both be executed.

A current-turn Supporter release shows the complementary timing effect. Its Supporter cost matters against another Supporter due **this** turn, as shown in `interturn_bench_debt_policy`. It does not consume the Supporter quota of the next turn.

## Attack contention

Moving the Bench deadline later does not make an attack release free.

If the current turn independently requires a different attack, the release attack and that attack compete for the single attack-ending action. The planner finds no line that executes both. If the release attack itself satisfies the current attack objective, the contention disappears.

The important state variable is therefore the relationship between the release action and the turn's other objectives, not simply whether a release effect exists.

## Strategic interpretation

Bench-release value is deadline-sensitive.

A reusable planner should preserve:

- earliest turn when the replacement Bench entrant can exist;
- deadline by which it must enter;
- release action class;
- whether the release ends the current turn;
- current-turn objectives sharing that action channel;
- future action budgets after the turn boundary.

This gives different evaluations to the same physical release card in different temporal states.

An attack pickup can have near-zero value for an immediate combo line while being perfectly adequate as end-of-turn preparation for a next-turn evolution, counter-tech, or attacker. A Supporter pickup can be unusable beside another current-turn Supporter while being clean preparation when the competing Supporter is only needed next turn.

## Evidence class

The action-ending rule for attacks and the one-Supporter-per-turn baseline are represented by the repository's validated `TurnActionBudget`. The turn-boundary reset follows the same budget semantics used by the repository's turn-sequence work. The reported feasibility results are deterministic state-transition results.

## Limitations

The model abstracts over the opponent's intervening turn. It assumes the released slot remains available until the player's next own turn and does not model forced Bench filling, Knock Outs, hand disruption, Pokémon recovery, or the opponent changing capacity.

It also assumes the release action itself is accessible and legal. Attack costs, Active positioning, Ability locks, Item locks, and search access belong in upstream state.

## Relation to prior work

`bench_release_catalog` classified the real release channels. `typed_bench_release_execution` showed that those classes have different same-turn costs. This result adds availability time and deadline, showing why action-class rankings can reverse across a turn boundary.

## Next useful work

The next layer should make the opponent's intervening turn explicit. A slot freed at end of turn can be attacked through board disruption before it is used, so preloading future Bench capacity may carry exposure risk that an immediate release-and-entry line does not.
