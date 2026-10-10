# An opponent's Special Energy counter changes the Dragon Impact payment frontier

## Controlled question

The previous [Regidrago discard witness](../energy_discard_continuation_frontier/) showed that retaining Double Dragon Energy (DDE) by discarding two Basic Energy cards preserves next-turn Apex Dragon readiness. Is that advantage robust when the opponent can respond with a Special Energy counter?

**No, under an immediate guaranteed counter and no intervening replacement actions.** This illustrates a matchup-sensitive tactical boundary rather than a claim that either payment is globally best.

## Printed card sources

The source-backed starting state and copied attack are unchanged: Regidrago VSTAR (`swsh12-136`), Salamence ex (`sv9-114`), DDE (`xy6-97`), plus Basic Grass and two Basic Fire Energy.

Additional legal Expanded sources in the bundled snapshot:

- **Enhanced Hammer**, `sv6-148`: an Item discarding a Special Energy from one opposing Pokémon.
- **Temple of Sinnoh**, `swsh10-155`: a Stadium making attached Special Energy provide Colorless Energy with no other effect. Under the one-unit interpretation established by the Pokémon community's official forum, an attached DDE now provides only one Colorless unit.

The opponent plays exactly one specified response after the Dragon Impact attack and before Regidrago can attach or take another action. No other Energy is attached, and the opposing response is assumed to have been available when its row is examined.

## Result

| Payment for copied Dragon Impact | Immediately Apex-ready? | After Enhanced Hammer? | Under Temple of Sinnoh? | Basic Energy cards retained |
| --- | --- | --- | --- | ---: |
| Discard DDE alone (one card) | No | No; Hammer has no DDE target | No | 3 |
| Discard Grass plus either Fire (two cards) | Yes | No; Hammer discards DDE | No; DDE supplies one Colorless | 1 |
| Discard both Fire (two cards) | Yes | No; Hammer discards DDE | No; DDE supplies one Colorless | 1 |

All three two-Basic-card choices retain next-Apex readiness when the opponent does nothing. A guaranteed Enhanced Hammer or Temple of Sinnoh response eliminates that immediate continuation in the modeled states. The DDE-discard option retains two more physical Basic Energy cards, which can matter for later setup or recovery.

Enhanced Hammer is *unplayable in this restricted state* after DDE is already discarded, because there is no remaining opposing Special Energy target. Its row represents absence of that action rather than an illegal Item play.

## Decision threshold in a transparent toy utility model

Suppose an attack-ready next turn is valued at `W`, each remaining Basic Energy card at `v`, and retaining DDE is valued at `s` provided it is not neutralized. Let `q` denote an **exogenous** probability that the opponent can and will successfully neutralize DDE before the next attack, by Enhanced Hammer or an applicable Stadium.

Then, relative to discarding DDE alone, the expected utility difference of preserving DDE through a two-Basic payment is

`(1-q) * (W+s) - 2v`.

Provided `W+s > 0`, the two-Basic payment is preferred in this specific linear model when

`q < 1 - 2v/(W+s)`.

For an illustrative `W=10, s=0, v=1`, the crossing is **q=0.8**. These are hypothetical values. No matchup prevalence or actual card valuation has been estimated.

## Reproduction

`tools/energy_discard_continuation_disruption.py` reuses the four-payment source-backed state, checks both additional card texts by exact print ID, applies three deterministic response profiles, and asserts all four post-response readiness states.

Run `python -m tools.energy_discard_continuation_disruption` from the repository root.

## Limits

The opponent-response model presumes Item availability or the ability to play a Stadium at the indicated time; it does not model opponent Supporter or Item locks, alternative targets, conditional Stadium replacement, energy acceleration, hand knowledge, or action-value costs for the opponent. Temple of Sinnoh's effect suppresses DDE only while it is present. The attacker might play a new Stadium or attach additional Energy on its own next turn. The model ends before those actions.

The result is a counterexample to **universally assuming that the action preserving next-attack Energy readiness survives an opponent's counterplay**. It does not prove that discarding DDE is competitively optimal against Enhanced Hammer decks.
