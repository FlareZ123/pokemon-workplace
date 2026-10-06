# Supporter connector temporality: access edges need action-class timing

## Question

When a card can obtain a Supporter such as Gladion, does a graph edge to that Supporter imply that the Supporter is usable on the same turn?

No. In paper Expanded, the answer depends on **what kind of action produced the Supporter** and on the current Supporter-capacity state. This is a mechanically grounded refinement of connector domination, Supporter contention, and Active Move Realism.

## Rules basis

The local advanced manual gives two relevant default rules:

- after a player uses an attack, that player's turn ends;
- a player may normally use only one Supporter during their turn.

Card text can alter normal rules. The local Expanded card pool contains `Magnezone` (`bw8-46`) with the `Dual Brains` Ability: `During your turn, you may play 2 Supporter cards.` That exception is important because it shows that Supporter capacity is a state variable rather than an absolute constant.

## Core result

A search graph should type connector edges by the action class and action budget they consume. For a target Supporter `T` that the player wants to **play this turn**, the following default timing applies when no effect increases Supporter capacity.

| Connector class | Example | Can put target Supporter into hand this turn? | Can normally play target Supporter this turn? | Main caveat |
| --- | --- | --- | --- | --- |
| Item | `Xtransceiver` (`bw3-96`) | Yes on heads | Yes | Coin flip |
| Item | `Computer Search` (`bw7-137`) | Yes | Yes | Discard 2 cards; ACE SPEC |
| Item | `Secret Box` (`sv6-163`) | Yes | Yes | Discard 3 cards; ACE SPEC |
| Item | `Trainers' Mail` (`xy6-92`) | Sometimes | Yes if found | Top-4 hit only |
| Ability | `Tapu Lele-GX` Wonder Tag | Yes | Yes | Bench slot and play-from-hand condition |
| Ability | `Jirachi-EX` Stellar Guidance | Yes | Yes | Bench slot and play-from-hand condition |
| Supporter | `Steven` (`xy6-90`) | Yes | **No under normal 1-Supporter capacity** | Steven consumed the Supporter action |
| Supporter | `Skyla` (`bw7-134`) | Yes, because Gladion is a Trainer | **No under normal 1-Supporter capacity** | Skyla consumed the Supporter action |
| Supporter | `Teammates` (`xy5-141`) | Yes when its condition is met | **No under normal 1-Supporter capacity** | Teammates consumed the Supporter action |
| Supporter | `Steven's Resolve` (`sm7-145`) | Yes | No | Also ends the turn |
| Supporter | `Cynthia & Caitlin` (`sm12-189`) | Yes from discard | **No under normal 1-Supporter capacity** | Itself is the Supporter play |
| Attack | `Lilligant` (`bwp-BW49`) Lead | Yes | No | The attack ends the turn |

The distinction is not semantic bookkeeping. It changes whether a line exists before a deadline.

## Same-turn feasibility theorem

Under the ordinary one-Supporter-per-turn rule, suppose a line requires playing target Supporter `T` during the current turn.

- If the path to `T` contains a Supporter connector that must be played before `T`, the path is not same-turn feasible because the connector consumes the turn's sole ordinary Supporter play.
- If the path to `T` ends in an attack, the path is not same-turn feasible because the turn ends after that attack.
- If the path uses only Items, Abilities, or other actions that do not consume the Supporter play and do not end the turn, the path may be same-turn feasible, subject to its other costs and conditions.
- If a card effect increases Supporter capacity, such as `Magnezone` (`bw8-46`) `Dual Brains`, the first statement must be evaluated against the increased remaining capacity rather than treated as an unconditional prohibition.

This theorem follows directly from action timing and does not depend on deck statistics.

## Why naive associativity graphs fail

Consider these two graph paths to Gladion:

`Tapu Lele-GX -> Gladion`

`Steven -> Gladion`

As untyped reachability edges, both say that Gladion is accessible. For a current-turn Prize rescue, they have different feasibility. Wonder Tag can search Gladion while leaving the ordinary Supporter action unused. Playing Steven uses that action, so the fetched Gladion is normally a future-turn resource.

The same problem appears with generic any-card connectors. `Computer Search -> Gladion` is potentially same-turn, while `Teammates -> Gladion` normally is not. Counting both as equivalent one-edge access systematically overstates early Supporter accessibility.

## Relation to timed Prize rescue

`results/timed_prize_rescue/` separates initial Prize topology, timed card access, and Supporter action bandwidth. Connector temporality adds another layer: **the method used to obtain the rescuer can itself consume the action budget required to use it**.

A future deck simulator should therefore represent a rescue connector with at least:

- source zone and destination zone;
- action class: Item, Ability, Supporter, attack, or another explicit class;
- whether it ends the turn;
- Supporter-capacity cost;
- other costs such as discard requirements, Bench occupancy, VSTAR usage, coin flips, or conditional activation;
- whether the target is chosen deterministically or only sampled from a subset such as top 4/top 7.

## Interaction with AMR and DCI

Temporal feasibility still does not guarantee realistic playability. `Computer Search` can obtain Gladion without spending the Supporter action, but its two-card discard cost can be difficult when the hand contains protected resources. `Secret Box` preserves Supporter capacity too, while demanding three discards. These are exactly the kinds of states where DCI and AMR matter.

Similarly, `Tapu Lele-GX` and `Jirachi-EX` can leave the Supporter action available while consuming Bench space and requiring the Pokémon to be played from hand. Their edge cost is therefore spatial and state-dependent rather than Supporter-capacity based.

## Connector domination consequence

A connector can be temporally valid and still be strategically dominated. If `Computer Search` is the only remaining route to an attacker or Energy piece, spending it on Gladion may destroy the stronger line. Search algorithms should therefore distinguish:

1. whether a target is reachable;
2. whether it is reachable before the deadline;
3. whether the connector leaves enough action capacity to use the target;
4. whether consuming that connector dominates or is dominated by competing uses.

This gives a concrete reason that simple hypergraph connectivity is insufficient even when every card-text edge is individually correct.

## Confidence and limits

The timing theorem is a rules-derived result. The card examples are local-card-pool observations from prints marked Expanded legal in the bundled database, with the repository's paper Expanded scope in mind.

The example table is illustrative rather than an exhaustive catalog of every card that can reach a Supporter. Generic any-card search, top-deck manipulation, discard-recovery chains, and multi-step sequences create many additional paths. The important result is the temporal/action typing of the edges, which applies to those paths as well.

## Next useful work

The next computational step is to add connector classes to the timed Prize-rescue model. A small exact state model can compare, for example, direct Gladion copies, Item/Ability outs that preserve the Supporter action, and Supporter-based outs that delay Gladion unless extra Supporter capacity is active. That would quantify how much a raw `outs` count overstates rescue availability by a specific turn.
