# Aichi Regidrago bonus-turn response: Kyurem can snipe a pre-staged Mimikyu

## Question

The 2026 CL Aichi Open League winning Shadow Rider Calyrex VMAX list has **one Mimikyu (Guardians Rising 58), 70 HP**, whose Copycat can respond to an exposed Regidrago VSTAR Apex Dragon declaration. Pre-staging that Mimikyu on the Bench can lessen later search and Item-lock problems.

Can Regidrago use the Timeless-GX bonus turn to remove the prepared Mimikyu without first changing its declared attack identity?

**Yes, conditionally.** The Kyurem from Shrouded Fable has Trifrost: discard all Energy from the attacker and deal 110 damage to three of the opponent's Pokémon. Regidrago can copy Trifrost through Apex Dragon from its Dragon discard pile, so an unprotected 70-HP Benched Mimikyu is Knocked Out.

The tradeoff is material: Regidrago discards its attached Energy, and its last *declared* attack stays Apex Dragon. If Shadow Rider can recover or re-establish Mimikyu in time, the copying threat may return.

## Empirical source anchors

- 2026 CL Aichi winning Shadow Rider list: https://limitlesstcg.com/decks/list/26807 (one Mimikyu, no second copy).
- Nine published top-32 Aichi Regidrago lists: https://limitlesstcg.com/tournaments/566/cards. Each published list contains exactly one Kyurem of the named Shrouded Fable print, as checked against the individual list links in `../regidrago_budew_promotion_baselines/aichi9_counts.json`.
- Physical print facts in the repository card pool:
  - `resources/cards/en/sm2.json` `sm2-58`: Mimikyu 70 HP, Psychic, Basic, Copycat.
  - `resources/cards/en/sv6pt5.json` `sv6pt5-47`: Kyurem, Dragon, Trifrost.
  - `resources/cards/en/swsh12.json` `swsh12-136`: Regidrago VSTAR, Apex Dragon.
  - `resources/cards/en/sm5.json` `sm5-100`: Dialga-GX, Timeless-GX.

The full damage and Knock Out process follows the Advanced Player's Rulebook §§A-01 and D. The targeted Benched Mimikyu takes 110 damage unless an applicable protective effect prevents or reduces it.

## Two Regidrago choices during the extra turn

Assume Regidrago has just declared `Apex Dragon -> Timeless-GX`, gets an extra turn, retains sufficient Energy to use Apex Dragon, and its Kyurem is in the discard pile.

**Option A: Promote Budew and attack with Itchy Pollen.** The new declared identity overwrites Apex Dragon and prevents the opponent from playing Items during their next turn. This is the [dual-denial strategy](../timeless_budew_dual_denial/README.md); promotion itself is constrained by [physical switching costs](../regidrago_budew_promotion_baselines/README.md).

**Option B: Keep Regidrago Active and use Apex Dragon -> Trifrost.** There is no need to promote Budew. Provided Mimikyu is in play, Trifrost can select it among up to three available opposing Pokémon and its 110 unprotected damage exceeds Mimikyu's 70 HP. Regidrago discards *all its attached Energy* from the copied attack. Its latest declared attack remains **Apex Dragon**.

This yields a matchup-specific **readiness-versus-exposure dilemma**:

| Shadow Rider Mimikyu at bonus-turn deadline | Budew history/Item cover | Kyurem Trifrost repeat-Apex |
| --- | --- | --- |
| Mimikyu still in a hidden or non-board zone | History covered, Items unavailable on response turn | Mimikyu cannot be targeted; Apex remains exposed if they assemble a counter |
| Mimikyu already on Bench, unprotected, 70 HP | History covered; Item lock still affects response | Trifrost Knocks Out Mimikyu for one Prize and may damage two other targets; Apex remains exposed, recovery is possible |

The Regidrago player sees whether Mimikyu occupies the Bench before choosing a bonus-turn attack. This is a *sequential public-board adaptation*, and it explains why an isolated `Copycat -> Apex Dragon` graph is insufficient to evaluate the matchup.

## Reproduced mechanics

`python results/regidrago_bonus_turn_mimikyu_snipe/reproduce.py`

The regression:
1. Checks the exact Kyurem and Mimikyu prints, attack text and HP, and all-nine Kyurem tournament fixture.
2. Builds a board with Regidrago VSTAR Active, Dialga-GX and Kyurem in Regidrago's discard, an opposing Shadow Rider VMAX Active, and Mimikyu Benched.
3. Calls the canonical copy kernel for `Apex Dragon -> Timeless-GX`, and then for `Apex Dragon -> Trifrost` after the extra-turn boundary.
4. Checks body chains, preserved outer declared identity, and per-player GX-use state.
5. Verifies the damage threshold: 110 unprotected damage is sufficient to Knock Out a 70-HP Mimikyu.

The attack-copy kernel does **not** execute damage allocation, Knock Out, Prize taking, Tool-based mitigation, or other active protection. The damage threshold uses the explicit card text and printed HP. This is an exact conditional rules observation with a simplified execution trace, not a full battlefield simulation.

## Limits and next test

- The Mimikyu might be in hand, deck, discard or Prize, so Trifrost cannot target it.
- An attached protection effect, an ability, or an attack effect can potentially change whether 110 damage Knocks Out the target.
- Kyurem must be in Regidrago's discard. Card inclusion alone does not establish that the payload is accessible, and its singleton may be Prized.
- Discarding all attacking Regidrago Energy sacrifices future attack readiness.
- The champion list has Night Stretcher, Tulip, search cards, and other ways to re-establish a discarded Mimikyu. A KO does not remove the card from the game.
- The board can be changed by the first Timeless-GX hit, including ending the game before a bonus turn matters.
- No actual match results or win-rate improvements can be inferred from the decision matrix.

A next improvement is an exact post-Trifrost recovery model that asks whether one discarded Mimikyu can be brought back, powered with Psychic Energy, promoted, and use Copycat on the very next Shadow Rider turn while Apex Dragon remains exposed. That is the correct stress test of whether the snipe reliably covers the counter.
