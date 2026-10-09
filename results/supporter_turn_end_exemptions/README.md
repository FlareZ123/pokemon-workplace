# Turn-ending Supporters and active Ability exceptions

## Question

Does a Supporter with printed "Your turn ends" wording always close the ordinary action budget after its effect resolves? How does this interact with conditional Active Pokémon Abilities and enlarged Supporter quotas?

## Source-backed finding

Two exactly identified active Ability exceptions in the supplied Expanded card pool are:

- Metagross `sm7-95`, **Extend**: while it is your Active Pokémon, your turn does not end when you play Steven's Resolve. Steven's Resolve `sm7-145` and `sm7-165` normally search for three cards and end the turn.
- Alcremie `swsh9-71` and `swsh9tg-TG08`, **Additional Order**: while Active, your turn does not end when you use Café Master `swsh9-133`, which ordinarily attaches differently typed basic Energy to up to three of your Benched Pokémon and ends your turn.

These exceptions apply by the named Supporter, in the exact current Active position, with the Ability enabled. If Metagross is on the Bench or suppressed, Steven's Resolve closes the turn. Metagross does not protect Katy `sv1-177`, which independently has turn-ending Supporter text.

## Model

`tools/supporter_turn_end_exemptions.py` uses the current printed Supporter and effective Active board state as inputs. A transaction that has successfully resolved the physical Supporter effect:

1. Consumes one `TurnAction.SUPPORTER`, retaining the integer number of Supporters used.
2. Determines whether the printed Supporter rules explicitly end the turn.
3. Checks the matching legal Active Ability print and its exact text, plus active Ability enablement and any causal suppression overlay.
4. If no matching active exemption exists, consumes `END_TURN`, closing every remaining ordinary action channel.

Even if the turn is closed early, the used Supporter count remains correct. Conversely, an Active matching exemption keeps the turn open, but the Supporter count is still spent.

This separates a **quota ceiling** from a **hard turn boundary**. For example, in a two-Supporter turn representing Magnezone Dual Brains, Steven's Resolve without active Extend spends one Supporter and ends the turn before the second is usable. With active Extend, Steven's Resolve can resolve without ending the turn, and the player may spend the second Supporter on another legal card (e.g. Arven).

## Regression

`results/supporter_turn_end_exemptions/reproduce.py` covers ordinary and alternate Steven prints, both Expanded-legal Additional Order Alcremie prints, Metagross on Bench, effective Ability suppression, a generic non-ending Supporter Arven, unrelated Katy end-turn wording, and the Supporter quota-two continuation witness.

## Boundaries

This is a finalization projector called **after** the Supporter's primary effect is executed. The caller must verify hand origin, availability of the Supporter, resource searches/attachments, action restrictions, and one-per-turn turn-order rules before calling it. It does not claim that a specific Stage 2 Metagross setup is executable on the first turn or optimize when playing an ending Supporter is strategically correct.

The effective Ability overlay is provided as a flag plus optional suppressed-object IDs. Comprehensive Ability-lock precedence remains the upstream causal lock solver's responsibility. Future work could compose this transaction with a physical Supporter-card zone ledger.

Related: [../turn_action_budget/](../turn_action_budget/), [../canonical_turn_budget_owner/](../canonical_turn_budget_owner/), [../legacy_mega_evolution_turn_end/](../legacy_mega_evolution_turn_end/).
