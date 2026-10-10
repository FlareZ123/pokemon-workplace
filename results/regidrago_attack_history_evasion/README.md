# Regidrago can use the Timeless-GX bonus turn to cover Apex Dragon attack history

## Question

The Aichi-winning Shadow Rider counter uses Mimikyu's Copycat after an opponent declares Regidrago VSTAR's Apex Dragon.

If Regidrago itself uses:

\`Apex Dragon -> Timeless-GX\`

does the bonus turn create a chance to remove Apex Dragon from the attack-history state before the Shadow Rider player gets a turn?

Yes.

This is a turn-order consequence of two already-established repository semantics:

1. copied Timeless-GX schedules another turn for the same player before the opponent acts;
2. the outer declared attack identity is what becomes the player's recorded last attack.

Regression:
\`results/regidrago_attack_history_evasion/reproduce.py\`

Empirical fixture:
\`results/regidrago_attack_history_evasion/aichi_2026_published_regidrago.json\`

## Event evidence

Limitless publishes nine Regidrago lists from the 2026 CL Aichi Open League top 32:

https://limitlesstcg.com/tournaments/566/cards

The nine published lists are places 10, 12, 13, 14, 18, 20, 21, 27, and 32. The tournament history page classifies two additional top-32 finishes as Regidrago, but their detailed lists are absent from the published-card aggregation, so this result does not impute their contents.

Across the nine published lists:

- all 9 contain Budew;
- the lists contain 12 Budew copies total, matching the aggregate average 1.33;
- 5 of 9 contain the Dragon Koraidon ex from Temporal Forces;
- those lists contain 5 Koraidon ex copies total, matching the aggregate average 0.56;
- the nine lists contain 34 Double Dragon Energy total, matching the aggregate average 3.78.

The fixture records each published list URL and the three counts used here.

## Rules and card-text facts

The relevant Budew has:

\`Itchy Pollen\`

with no Energy requirement. Its effect prevents the opponent from playing Items from hand during their next turn.

The relevant Koraidon ex is Dragon type and has:

\`Retribution Strike [C][C]\`

Double Dragon Energy can attach to Dragon Pokémon and supplies two Energy at a time while attached to one. Therefore one Double Dragon Energy is sufficient to pay Retribution Strike's printed two-Colorless cost on this Koraidon ex.

These are direct attacks. Their declared identities are Itchy Pollen and Retribution Strike rather than Apex Dragon.

## Extra-turn history covering

Start from the Regidrago player's turn:

\`Apex Dragon -> Timeless-GX\`

The copy resolver records:

\`last declared attack = Apex Dragon\`

Timeless-GX schedules another turn for the same Regidrago player and skips the intervening Pokémon Checkup in the repository's current boundary abstraction.

The Shadow Rider player has not received a turn yet.

### Cover with Budew

On the bonus turn, the Regidrago player promotes Budew and declares Itchy Pollen.

The recorded history becomes:

\`last declared attack = Itchy Pollen\`

When the Shadow Rider player's turn finally begins, Copycat sees Itchy Pollen as the opponent's last attack. It can copy Itchy Pollen because it is not a GX attack, but Apex Dragon is no longer an eligible target.

The regression explicitly rejects an attempted:

\`Copycat -> Apex Dragon\`

selection in that state.

Budew therefore acts as a zero-Energy **history cover** after Timeless-GX.

This does not make the line free. Regidrago still needs Budew in play or accessible, a way to make it Active, and must accept the tactical consequences of attacking with a 30-HP support Pokémon for 10 damage. The Item-lock effect can be useful, but the board-position cost is real.

### Cover with Koraidon ex

On the bonus turn, the Regidrago player can instead promote Koraidon ex and declare Retribution Strike.

The recorded history becomes:

\`last declared attack = Retribution Strike\`

Copycat then sees Retribution Strike rather than Apex Dragon.

Compared with Budew, Koraidon needs Energy. One Double Dragon Energy is sufficient for its two-Colorless attack because Koraidon is Dragon type. Five of the nine published Regidrago lists contained this exact Koraidon ex, and all nine contained multiple Double Dragon Energy.

Promotion and card access remain separate requirements.

### Repeat Apex Dragon

If Regidrago uses Apex Dragon again on the Timeless-GX bonus turn, attack history remains:

\`last declared attack = Apex Dragon\`

When the opponent's turn begins, Mimikyu can still execute:

\`Copycat -> Apex Dragon -> Timeless-GX\`

provided the Shadow Rider-side payload and readiness conditions are satisfied.

The canonical regression confirms that the Regidrago player having already spent its GX attack does not consume the Shadow Rider player's independent GX-use channel. The copied Timeless-GX on the Mimikyu side then marks both players as having used a GX attack.

## Strategic interpretation

This creates a temporal form of AMR that a static interaction graph misses.

The graph:

\`Mimikyu -> Copycat -> Apex Dragon -> Timeless-GX\`

is legal when Apex Dragon is the opponent's last declared attack at the response deadline.

The copied Timeless-GX line creates an intermediate extra turn before that deadline. During that turn, the Regidrago player can change the history state.

So the relevant condition is more precise:

\`Apex Dragon exposed at the start of the opponent's next turn\`

rather than merely:

\`Apex Dragon was used sometime during the previous sequence\`.

This is an **attack-history deadline**.

The counter-ALS and the counter-counterplay therefore interact:

1. Shadow Rider rewards Regidrago for exposing Apex Dragon because Copycat can turn that declaration into access to Shadow Rider's own discarded Dialga-GX.
2. Regidrago's own Timeless-GX can create an extra action window before Shadow Rider receives priority.
3. A direct attack during that window overwrites the last-declared-attack state.
4. A second Apex Dragon declaration reopens or preserves the exposure.

The board and resource cost of the cover attack determines whether that option has high AMR.

## Why Budew is especially important empirically

Budew is present in every one of the nine published top-32 Aichi Regidrago lists, with 12 copies across them.

Its zero-Energy attack means the Energy channel itself does not block the history-cover action. Its real costs are physical:

- having or finding Budew;
- Bench space;
- moving Budew Active;
- giving up Apex Dragon's stronger body for that turn;
- exposing a fragile 30-HP Pokémon;
- accepting the downstream game state created by Item lock.

This makes Budew a concrete example of a card whose discrete matchup value extends beyond the obvious Item-lock effect. In this matchup state it can also control what attack is visible to Copycat.

## Evidence classification

**Tournament-list observation**

Nine published Aichi Regidrago lists are available in the Limitless card aggregation. All nine contain Budew. Five contain Koraidon ex TEF 120. Aggregate counts match the per-list fixture.

**Rules/card-text facts**

Budew's Itchy Pollen has no Energy requirement. Koraidon ex TEF 120 is Dragon and Retribution Strike costs two Colorless. Double Dragon Energy supplies two Energy while attached to Dragon Pokémon.

**Computational result**

The regression composes the repository's canonical attack-copy resolver with the canonical copied-extra-turn boundary bridge:

- Apex Dragon copying Timeless-GX grants Regidrago the next turn before the opponent;
- Budew's attack on that turn replaces Apex Dragon in last-declared-attack history;
- Koraidon's attack does the same;
- a repeated Apex Dragon leaves Apex Dragon exposed;
- Mimikyu's attempted Apex selection is rejected after either cover attack;
- Mimikyu's Copycat -> Apex Dragon -> Timeless-GX remains valid after repeated Apex.

## Limits

This result establishes availability and semantics, not optimal play.

It does not estimate the probability that Budew or Koraidon can be promoted on the bonus turn, nor the opportunity cost of abandoning another Apex Dragon attack. It does not model Knock Outs caused by the first attack, hand disruption, Prize locations, Bench occupancy, gust requirements, retreat costs, or whether Item lock matters positively in the resulting board state.

The nine-list empirical statement applies only to published detailed Regidrago decklists from this event. Two additional top-32 finishes are classified as Regidrago in tournament history but do not appear in the nine-list card aggregation.

A high-value continuation is to compute the AMR of Budew history covering from actual Regidrago states after Timeless-GX, including promotion routes, Bench occupancy, Prize knowledge, and whether the lost Apex body changes the Prize race.


## Validated follow-up work

- [Budew physical-promotion and inventory baseline](../regidrago_budew_promotion_baselines/README.md) analyzes nine Aichi lists' Guzma/Prime Catcher counts, the Basic-only Latias ex Skyliner effect, Regidrago VSTAR's Retreat Cost, and exact but explicitly non-gameplay card-inventory baselines (CI 38061691316).
- [Timeless-GX Budew compound denial](../timeless_budew_dual_denial/README.md) composes this attack-history cover with Itchy Pollen Item lock; its bounded Shadow Rider payload-routing state space contracts from 15/16 zone pairs to 2/16, and to 1/16 when Tulip's Supporter channel must be reserved for Guzma (CI 38061863206). These are reachability counts, not play or win probabilities.
