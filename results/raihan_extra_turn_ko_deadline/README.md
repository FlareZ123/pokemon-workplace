# Raihan's last-opponent-turn condition resets across consecutive Timeless-GX turns

## Question

Regidrago's Raihan can attach a Basic Energy from discard and then search for any card, making it one potential way to rebuild Apex Dragon after a Trifrost Energy discard. Raihan has a strict prerequisite: **any of your Pokémon were Knocked Out during your opponent's last turn**.

What if the opponent used Timeless-GX to take two turns in a row? Does a Knock Out during the *first* opponent turn unlock Raihan after their bonus turn, if no Knock Out occurs on the bonus turn?

**No.** The relevant observation window is the opponent's **most recently completed individual turn**. A Timeless-GX bonus turn is a fresh turn with newly reset per-turn action limits and its own Knock Out history. The prior first turn does not remain “last” after the second turn finishes.

## Timed experiment

The regressor composes:

- the repository's existing `canonical_turn_sequence_owner`, which verifies Timeless-GX grants another turn to the same player while skipping the intervening Pokémon Checkup;
- a new minimal `last_opponent_turn_knockout_gate` that replaces each player's previous completed-turn KO record every time that player finishes a turn, even when no KO occurred;
- the independently validated [post-Trifrost Regidrago Raihan recharge witness](../regidrago_post_trifrost_recharge/README.md).

P1 = Shadow Rider using copied Timeless-GX; P2 = Regidrago wanting to play Raihan on its response turn.

| P1 first Timeless turn KOs P2 Pokémon? | P1 bonus turn KOs P2 Pokémon? | Raihan playable by P2 afterward? |
| --- | --- | --- |
| Yes | No | **No** |
| No | Yes | **Yes** |
| Yes | Yes | **Yes** |
| No | No | **No** |

The regressor also rejects Raihan after Knock Outs affecting only P1's own Pokémon, since the P2 side suffered none.

With a fixed P2 physical Energy inventory (a Basic Grass in discard and Double Dragon Energy in deck), the conditional `Raihan -> attach Basic -> search DDE -> manually attach DDE` recharge succeeds when the KO occurs on P1's bonus turn and is rejected when P1's first turn is the only one that KOs a P2 Pokémon.

## Why this matters

Timeless-GX is often considered a source of extra tempo. It can also **move the opponent's conditional resource deadline**.

The player gaining an extra turn may be able to avoid enabling Raihan by ending the second turn without knocking out any of the opposing Pokémon, even if they took a knockout on the first turn. Conversely, a knockout on the second turn makes Raihan available. This is a precise action-history effect, separate from whether a Knock Out was beneficial in the Prize race.

No claim is made that foregoing a Knock Out is optimal. The Prize race, alternate Supporter options, attacker survivability and hand information can easily outweigh this narrow conditional effect.

## Rule and card anchors

- Raihan `swsh7-152` contains the “during your opponent's last turn” prerequisite and requires successful Basic Energy attachment before its unrestricted deck search.
- Dialga-GX `sm5-100` Timeless-GX says take another turn and skip the between-turns step.
- Advanced Player's Rulebook §E-11 explains KO prerequisites referring to the opponent's last turn, while Pokémon Checkup §F takes place in neither player's turn. The model therefore records only KOs occurring **during** a player's turn; between-turns KOs are excluded.
- `tools/canonical_turn_sequence_owner.py` carries the actual consecutive-turn scheduling and action-budget reset; the new tracker stores a small event-history projection independently.

## Reproduction and scope

`tools/last_opponent_turn_knockout_gate.py` contains the event tracker. `results/raihan_extra_turn_ko_deadline/reproduce.py` builds the canonical two-turn timeline, checks every row and composes the Raihan recharge route.

Run `python results/raihan_extra_turn_ko_deadline/reproduce.py`.

The KO events are supplied as scenario inputs. The test does not simulate attack damage, Knock Out resolution or relative game advantage, and does not show an empirical tournament use of this specific two-turn Raihan denial. Its result is a **rule-derived, mechanically reproduced timing constraint**.
