# State-dependent action quota effects

## Question

How should a turn-action budget respond when a card in play changes an ordinary per-turn action limit and that effect later becomes inactive?

Magnezone `bw8-46` supplies a concrete legal Expanded case. Its Dual Brains Ability permits two Supporter cards during its controller's turn.

Implementation: `tools/action_quota_effects.py`  
Regression: `results/action_quota_effects/reproduce.py`

## Finding

Action limits are live board-state variables.

A player can begin under the basic one-Supporter rule, gain a two-Supporter ceiling while Dual Brains is active, lose that ceiling when the Ability is suppressed or its source leaves play, and regain it if the effect becomes active again.

Usage and current limit therefore need separate state.

For example, after one Supporter:

- usage can remain at one;
- Dual Brains active gives a current limit of two, leaving one use;
- Dual Brains suppressed restores the current limit to one, leaving no use.

After two Supporters have already been played, later suppression can produce `used = 2, limit = 1`. That state is historically coherent. It says the earlier actions happened while permitted and no further Supporter play is available.

## Representation

`ActionQuotaGrant` contains:

- source identity;
- affected `TurnAction`;
- total-use limit granted by that source;
- whether the grant is currently active.

`derive_action_quotas(...)` recomputes limits from the basic-rule ceilings and the currently active grants while preserving usage counts and turn-end state.

Recomputation from base is essential. Mutating only upward would leave a stale two-Supporter limit after Ability suppression.

A total-limit grant is treated as a ceiling, so duplicate active instances of the same “play 2 Supporter cards” wording still produce a limit of two. This differs from wording that would explicitly grant an additional use, which is outside the current grammar.

## Separation from locks

The existing lock model tracks whether the player may play Supporters at all. That permission is distinct from quota.

A composed planner therefore needs both:

1. a play-permission channel such as `PlayerChannels.supporter_play`;
2. a `TurnActionBudget` whose current Supporter limit is derived from active quota effects.

A Supporter lock can deny play even when the budget has unused quota. Ability suppression can instead remove the quota-granting Ability and reduce the limit.

## Validation

The reproducer:

- loads Magnezone `bw8-46` from the bundled resources;
- verifies both bundled Lt. Surge's Strategy three-Supporter prints (`sm10-178`, `sm115-60`) are effectively Banned, preventing raw text scans from treating that capacity as legal Expanded state;
- verifies its Dual Brains text;
- checks effective Expanded legality through the shared legality classifier;
- verifies the ordinary one-Supporter ceiling;
- verifies a two-Supporter ceiling while Dual Brains is active;
- removes and restores the grant after one Supporter;
- preserves two already-used Supporters when the limit later falls back to one;
- verifies duplicate total-limit grants remain a ceiling of two.

## Limits

This result models direct total-use quota grants. It does not claim to parse every possible card wording that can affect turn actions.

A targeted text scan of the bundled corpus found Dual Brains as the legal direct numeric Supporter-limit case. Two Lt. Surge's Strategy prints contain a three-Supporter instruction, and both are effectively Banned. The same targeted grammar found no direct numeric wording for extra Stadium plays, extra normal Retreats, or extra ordinary manual Energy attachments. That is a coverage observation rather than proof that no indirect mechanic can affect those channels.

Future text-compilation work should distinguish at least total-limit wording, additional-use wording, effect-based actions that do not consume the ordinary channel, and player-level prohibitions.
