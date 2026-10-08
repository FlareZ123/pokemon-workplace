# agent48: physical copied-attack reaction integration

I connected `attack_copy_physical_ko_bridge` to reactions on a separate,
conserved attacker `StackBoardMaterialState`. The test at
`results/physical_copy_damage_reaction_bridge/` now covers Haughty Order
-> Timeless-GX, 150 damage, 15 Strong Bash reflection counters, and 2
Spiky Energy counters. Both Active Pokémon become pending KO candidates
without losing their physically attached cards. Cross-player disposal and
promotion ordering conserve all card-class counts.

The physical copied-attack replay now records actual target provenance,
and the reaction adapter refuses a mismatched target. Spiky Energy
eligibility is inferred from the physically attached Energy, Active Spot,
positive damage, and opposing-Pokémon attack condition.

Workflow run 37769026052 passed. Remaining gaps are general reaction
source eligibility and multiple damage targets per copied body event.
