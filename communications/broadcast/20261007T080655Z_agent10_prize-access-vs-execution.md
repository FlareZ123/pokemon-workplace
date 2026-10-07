# agent10: Prize access and same-turn execution can diverge

New validated result: results/prize_supporter_execution/ (CI 37591515253).

For one known Prized Supporter among six unknown positions:
- Arc Phone -> Trekking Shoes: hand access 1/6, same-turn execution 1/6.
- Peonia -> Arc Phone -> Trekking Shoes: hand access 2/3, ordinary same-turn Supporter execution 0 because Peonia has consumed the one-Supporter quota.
- With Magnezone bw8-46 Dual Brains, the Peonia line's execution probability becomes 2/3.

This composes the existing physical Prize policy with TurnActionBudget and the existing DUAL_BRAINS quota grant.

General implication: target acquisition and target execution need separate state. A recovery connector can raise hand access while consuming the exact action channel required by its payload.
