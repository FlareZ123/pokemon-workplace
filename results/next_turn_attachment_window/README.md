# Dragon's Wish: unbounded next-turn manual Energy attachment

## Question

The canonical \`TurnActionBudget\` stores finite ordinary per-turn action limits. Does the paper Expanded card pool contain an effect that grants **unbounded ordinary attachments from hand**, as opposed to executing several Energy attachments during a separate Trainer, Ability, or attack effect?

**Yes.** Dragonair \`sm1-95\`, Dragon's Wish, reads:

> During your next turn, you may attach any number of Energy cards from your hand to your Pokémon.

The bundled snapshot marks this print Expanded-legal. This is a time-delayed effect granting a player additional *manual attachment permission* during that player's next turn. It is distinct from attacks and Abilities that instruct their user to attach several cards immediately.

## Source-backed comparison

| Print | Effect / fact | Semantic channel |
| --- | --- | --- |
| Dragonair \`sm1-95\` | Dragon's Wish grants any number of attachments **during your next turn** | Temporary override of the ordinary manual-attachment limit |
| Magnezone \`bw8-46\` | Dual Brains allows two Supporter cards during your turn | In-play continuous finite Supporter quota; handled by existing quota model |
| Lt. Surge's Strategy \`sm10-178\`, \`sm115-60\` | Allows three Supporters in a turn including itself, but both prints are Expanded-banned in the bundled snapshot | Excluded from legal execution; useful search false positives |
| Emboar \`bw1-20\` | Inferno Fandango attaches a Fire Energy by using an Ability | Separate Ability-effect attachment; does not spend or enlarge ordinary manual quota |
| Pokémon Ranger \`xy11-104\` | Removes effects of attacks on each player and Pokémon | Removal of Dragon's Wish pending/active permission |

The Advanced Player's Rulebook, C-09, explicitly distinguishes Energy attached by an effect from the once-per-turn hand attachment. E-02 defines "your next turn" as the player's next actual turn. The rulebook's C-19 identifies attack effects that restrict a player as player-scoped. The same representation boundary is useful for permission-granting attack effects.

## Model

\`tools/next_turn_attachment_window.py\` adds a small immutable player-scoped overlay on the existing \`TurnActionBudget\`.

- \`pending_for\` records the owner of a Dragon's Wish attack effect.
- On every actual new turn, \`on_turn_start(incoming_player)\` activates only that player's pending permission. Pending permissions survive intervening opponent turns, including extra turns.
- \`consume_manual_attachment(player, budget)\` increments the canonical integer *usage history* for each attachment. While the permission is active, usage can exceed the ordinary integer limit without being rejected. The base quota remains one.
- Turn closure is always enforced. Active permission cannot authorize attachments after an attack or voluntary end.
- \`remove_attack_effects()\` clears the pending or active attack-granted permission. The existing physical attachment history remains. If the player has already attached at least once, removal does not magically reopen the ordinary one-per-turn allowance.
- Once the player's permitted turn ends and a different player's turn begins, the active permission expires. A newly queued Dragon's Wish is independently preserved for a later turn.

An integer such as 999 is **not** a faithful encoding of the printed "any number" text. It would impose an invented upper bound and would interact poorly with quota derivation. Because the actual deck and hand are finite, a game has only finitely many attachments, but the permitted count derives from physical supply and available actions.

## Regression

Run \`python results/next_turn_attachment_window/reproduce.py\` from the repository root.

The regression verifies exact card text and baseline legality, normal attachment exhaustion, a delayed Dragon's Wish across an opponent's extra turn, three manual attachments under the standard limit of one, turn closure, Pokémon Ranger-style removal, rearming, and the separation from Emboar's Ability-based acceleration.

## Boundaries and unresolved questions

This is an **action-bandwidth** kernel, not a full Energy-attachment executor. It does not select a physical Energy card, validate eligible targets or attached card constraints, resolve attacks, or enforce effects preventing attachment. Those belong in the existing typed physical/permission kernels. The initiating attack must have been legitimately announced and resolved upstream.

A larger composed simulator should invoke \`on_turn_start\` only on a real turn transition from \`canonical_turn_sequence_owner.advance_turn\`. Merely changing a player identifier or refreshing a quota is insufficient. It should also clear the permission when an applicable attack-effect-removal event resolves.

The current audit establishes a concrete counterexample to **finite-only quota modeling**. It does not prove all future prints or all historical reprint semantics have been catalogued. An automated semantic card-text compiler should distinguish turns containing an independently attached Energy **effect** from turns where the ordinary from-hand **permission** changes.

## Related research

- [../turn_action_budget/](../turn_action_budget/)
- [../canonical_turn_sequence_owner/](../canonical_turn_sequence_owner/)
- [../action_quota_effects/](../action_quota_effects/)
- [../energy_hand_attachment_events/](../energy_hand_attachment_events/)
