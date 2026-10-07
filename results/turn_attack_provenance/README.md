# Turn-scoped attack provenance and multi-attack turns

## Question

What state should an Expanded simulator preserve for attacks that refer to an attack used during a player's last turn?

The existing attack-copy kernel stores one scalar attack ID per player. That representation works for an ordinary turn with exactly one attack, but two legal situations expose missing state: a later turn can end without attacking, and Ω Barrage can allow two attacks in one turn.

Implementation: `tools/turn_attack_history.py`

Regression: `results/turn_attack_provenance/reproduce.py`

## Rules and card-text basis

The Advanced Player's Rulebook gives the ordinary rule that using an attack ends the turn. The same rulebook also says current card text takes priority when it contradicts the basic rules.

Mimikyu `smp-SM99` uses the wording "during their last turn" in Copycat. Its source state is therefore the opponent's last turn, rather than a permanent memory of the last attack that opponent ever declared.

The current Expanded card snapshot also contains Ω Barrage. Its text says the Pokémon may attack twice a turn. Five effectively legal prints in the English snapshot carry that exact Ancient Trait:

- Torchic `xy5-26`
- Nidoqueen `xy5-69`
- Medicham `xy5-81`
- Excadrill `xy5-97`
- Bunnelby `xy5-121`

This is a direct card-text exception to a universal one-attack-per-turn state model.

## Finding 1: blank turns overwrite older attack provenance

A concrete counterexample combines Apex Dragon, Timeless-GX, and Copycat.

1. Player 2 declares Apex Dragon and copies Timeless-GX.
2. Timeless-GX gives Player 2 another turn.
3. Player 2 ends that extra turn without attacking.
4. Player 1 then considers Copycat.

Player 2's last completed turn is the blank extra turn. A state field that still contains Apex Dragon from the earlier turn is stale for Copycat's "during their last turn" condition.

The regression composes the existing copy kernel with the existing turn-sequence kernel and demonstrates the error directly. The stale scalar state lets Player 1 continue through Copycat -> Apex Dragon -> Timeless-GX. Replacing it with the turn-scoped history correctly leaves Player 2 with no qualifying last-turn attack, so the Copycat edge has no legal target.

Extra turns also show why provenance should be kept per player. If Player 1 takes consecutive turns, Player 2's own most recently completed turn stays unchanged until Player 2 completes another turn.

## Finding 2: one scalar attack ID is lossy for Ω Barrage

`TurnAttackHistory` stores an ordered tuple of declared attack IDs for each player's most recently completed turn.

A Bunnelby Ω Barrage turn can therefore be represented as:

`(Burrow, Rototiller)`

The compatibility projection into `attack_copy_kernel.State.last_declared_attack` accepts blank and one-attack turns. It raises `LossyLastAttackProjectionError` for a multi-attack turn, because choosing one attack silently would destroy information.

This result deliberately stops before deciding how every "during the last turn" card should interpret a turn containing several attacks. The local rulebook and card text establish that such a turn can exist. They do not supply a complete ruling here for every historical copy effect. A future resolver should preserve the full ordered sequence and apply a card-specific or authoritative interpretation when that distinction matters.

## Representation

The reusable state keeps:

- the current player;
- a chronological turn index;
- the ordered declared attacks in the current turn;
- one completed-turn attack record per player.

Completing a turn always writes a record, including an empty tuple. That empty record is necessary state because it invalidates an older attack for later "last turn" checks.

The module records provenance only. It does not decide whether a second attack is legal. That legality belongs to attack-budget and card-effect state.

## Consequence for shared turn modeling

The current `TurnActionBudget` and `turn_sequence_kernel` use the ordinary attack boundary as an absorbing turn end. Ω Barrage demonstrates that this is an ordinary baseline rather than a universal Expanded rule.

A broader turn engine should separate "an attack resolved" from "the turn must now end" and derive remaining attack permission from card/effect state. The exact window between first and second attacks should be modeled from authoritative rules before planners are allowed to insert arbitrary ordinary actions there.

## Validation

The reproducer:

- verifies Copycat's last-turn wording from the bundled card data;
- verifies Timeless-GX's extra-turn wording;
- scans effectively legal Expanded sets and finds the five Ω Barrage prints above;
- reproduces the stale-extra-turn false positive in the current scalar copy state;
- shows that the turn-scoped record clears the stale attack after the blank extra turn;
- verifies that another player's provenance survives a same-player extra turn;
- preserves both ordered Ω Barrage attacks and rejects lossy scalar projection.

## Limits and next work

This is a provenance model. It does not resolve the full timing of a second Ω Barrage attack, attack costs, Knock Outs between attacks, or the historical ruling for copy effects when several attacks were used during the referenced turn.

The next high-value step is a quota-aware attack continuation model that can represent ordinary one-attack turns and explicit multi-attack exceptions without assuming that every normal action window reopens between attacks.
