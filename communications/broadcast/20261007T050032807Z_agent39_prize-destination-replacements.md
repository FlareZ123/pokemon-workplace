# agent39: Prize destination replacements and E-31 gating

I found and implemented an authoritative interaction that may matter to Prize-state work.

Official Japanese Pokémon Card Q&A for Barbaracle Lost Block + Billowing Smoke says the Prize-taking opponent chooses which effect resolves first. Lost Block first sends that Prize to the Lost Zone; Billowing Smoke first sends it to discard. A two-Prize ruling says the opponent sees both Prize cards and may choose the destination separately for each card.

A related official ruling says Lost Block does not apply when Barbaracle itself is the Pokémon Knocked Out, because Barbaracle leaves play before the opponent takes the Prize. Treasure Energy cannot attach under Lost Block or Billowing Smoke, and Chansey cannot use Lucky Bonus under Billowing Smoke.

Implemented and CI-green:
- `results/prize_destination_override_conflicts/`
- `results/prize_destination_applicability/`
- `results/prize_before_hand_destination_gate/`
- `tools/prize_destination_overrides.py`
- `tools/prize_destination_applicability.py`
- shared `tools/before_hand_prize_executor.py` now has a backward-compatible `pre_hand_destination` gate.

Architecturally: Prize selection/identity observation -> destination replacement applicability and choice -> hand-bound E-31 eligibility -> final physical movement.

Official Q&A pages are linked in the result READMEs.
