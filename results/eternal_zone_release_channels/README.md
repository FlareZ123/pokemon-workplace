# Release-channel feasibility after an Eternal Zone contraction

## Question

After Path to the Peak suppresses Eternal Zone and a full eight-slot Bench contracts to a full five-slot Bench, which Stadium-removal channels can actually restore Eternal Zone in time to reuse the slots during the same turn?

## Post-contraction state

The self-refresh line in `results/eternal_zone_refresh/` reaches a specific intermediate state:

- Path to the Peak has already been played this turn;
- Eternal Zone is suppressed;
- the player has discarded from eight Benched Pokémon down to five;
- the normal five-slot Bench is now full;
- the next action must remove Path to the Peak if the player wants Eternal Zone back.

This state filters release resources differently from a generic "can discard a Stadium" catalog.

Implementation: `tools/bench_release_channel.py`.

## Same-turn release channels

### Field Blower

Field Blower is an Item that can discard the player's own Stadium. It requires no Bench slot and does not consume the Supporter window. If Items are playable, it can remove Path to the Peak and leave the turn open.

### Lost Vacuum

Lost Vacuum is also an Item and needs no Bench slot. It can remove a Stadium by putting it in the Lost Zone, while requiring the player to put another hand card into the Lost Zone as its use condition. When that cost is payable and Items are playable, it also restores Eternal Zone before the attack.

### Worker

Worker draws three cards and discards a Stadium in play. It can remove Path to the Peak from a full Bench because it does not require board space. The cost is the Supporter window for the turn.

## Channels that fail or change the timing

### Pumpkaboo and Chien-Pao

Pumpkaboo's Pumpkin Pit and Chien-Pao's Snow Sink can discard a Stadium when the Pokémon is played from hand onto the Bench.

The contracted state has five Pokémon on a five-slot Bench. Those trigger Pokémon cannot be played onto the full Bench, so their Stadium-removal Abilities are mechanically unavailable exactly when the full-board Eternal Zone refresh needs them.

This is a connector-capacity interaction: the release card exists and its text answers the Stadium, while the route still fails because the release action itself demands the capacity it is supposed to restore.

### Another Stadium

Playing a new Stadium would normally replace Path to the Peak. In this line, Path to the Peak was already the Stadium played for the turn. The ordinary one-Stadium-per-turn rule prevents a second Stadium play that turn.

### Attack-based Stadium removal

An attack can remove Path to the Peak if an appropriate attacker and attack are available. The attack ends the turn, so the restored three slots cannot support further same-turn Bench-entry actions. This is a delayed release channel rather than a same-turn refresh channel.

## Lock sensitivity

The Item-based release line has an important failure mode under Item lock. If the player commits to Path to the Peak, contracts to five, and then cannot use the intended Item release, Eternal Zone remains suppressed.

Worker avoids Item lock while consuming the Supporter window. This creates a real resource substitution rather than a generic interchangeable release edge.

A robust state model should therefore attach at least these predicates to a release action:

- action class;
- whether it requires an open Bench slot;
- whether the relevant play channel is locked;
- whether a once-per-turn action window has already been consumed;
- whether the action ends the turn;
- whether additional costs are payable.

## General principle

An action that restores capacity can depend on that same capacity.

This is a form of self-gating. Bench-entry release cards are excellent examples because they are strongest when a slot already exists and can become unusable in the full-board state where cleanup is most desired.

The same reasoning applies to other connectors. Access to a card name is insufficient evidence that its state transition can be executed from the current board.

## Validation

`results/eternal_zone_release_channels/reproduce.py` checks the full-five post-contraction state. Field Blower, a payable Lost Vacuum, and an unused Worker Supporter window permit same-turn continuation. Pumpkaboo/Chien-Pao and a second Stadium play are blocked. Attack-based removal is usable in the abstract model while failing the same-turn-continuation requirement.

## Limits

The kernel treats card access as already satisfied. It does not model whether the release card is in hand, Prized, searchable, or strategically preferable to competing uses.

Attack-based removal is represented only by timing class and does not assert that a particular Darkness attacker with suitable Energy exists in an Eternatus deck.
