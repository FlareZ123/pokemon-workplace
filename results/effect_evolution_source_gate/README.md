# Effect evolution keeps source-action legality separate

## Question

Once C-12 evolution timing is modeled correctly, how should the source attack, Ability, Item, Supporter, or Stadium be gated without folding its permissions into the evolution rule?

## Result

tools/effect_evolution_source_gate.py composes each compiled direct-evolution profile with the repository's generic action-budget and play-lock layers. The adapter preserves a boundary between source permission and evolution permission.

A SourceActionContext carries the player's first-turn status, whether that player went first, the canonical TurnActionBudget, hand-play lock channels, generic Ability availability, and generic attack availability. The compiled profile supplies its source channel and first-turn source window.

The adapter checks source permission first. It stages the relevant generic quota only after that check, then executes the separate C-12 evolution transition. Because all state is immutable, a later evolution failure returns no transition and does not consume the caller's quota.

## Regression cases

The reproducer validates these boundaries:

- Salvatore is source-blocked on the first turn when its player went first and source-open when the player went second. A successful going-second line consumes one Supporter use.
- Supporter lock and an already-spent Supporter quota independently close Salvatore's source.
- Technical Machine: Evolution is attack-blocked on the first turn going first and source-open going second.
- Exeggcute's Precocious Evolution explicitly opens its attack source on the first turn going first, then the returned budget is turn-ended after the attack.
- A generic attack prohibition still closes Precocious Evolution.
- Eevee Energy Evolution is closed by generic Ability suppression.
- Boost Shake is closed by Item lock.
- Grand Tree's Stadium source can be open while its first-turn evolution policy still blocks the target transition.
- A failed Salvatore evolution-chain match does not consume the caller's Supporter quota.

## Why the separation matters

C-12 answers whether an evolution effect can bypass ordinary evolution timing. It does not create a legal source action. The player going first still cannot normally play a Supporter or attack on the first turn, Item lock can stop an Item source, Ability suppression can stop an Ability source, and per-turn quota can be exhausted before the effect is reached.

The reverse separation matters too. A source can be legal while the evolution is forbidden. Grand Tree can be in play and its Stadium effect can be otherwise available, while its own text prevents the represented first-turn Basic evolution.

## Scope

This adapter covers generic source channels only. It does not validate exact attack Energy, source position, named activation conditions, card presence, Trainer payment, target search, or card-specific lock exceptions. Those remain upstream state predicates.

The first-turn source window is taken from the compiled profile. This preserves the existing repository interpretation that a normal attack is unavailable to the player going first on the first turn, while an explicit card exception such as Precocious Evolution can open that attack source.

## Reproduction

    python results/effect_evolution_source_gate/reproduce.py

## Confidence

High for the represented generic action channels. The result is intentionally narrower than full card execution and keeps unmodeled card-specific prerequisites visible as limitations.

## Correction: Stadium activation has its own instance budget

The original generic source gate incorrectly spent `TurnAction.STADIUM_PLAY` when
resolving Grand Tree's already-in-play effect. Rulebook B-04 separates playing
one Stadium card from hand during a turn from voluntarily using an effect on an
existing Stadium. Grand Tree (`sv7-136`) specifies `Once during each player's
turn` for its effect separately from the ordinary Stadium-play instruction.

The source adapter now composes the preexisting `StadiumEffectState` model,
requiring a matching Grand Tree currently in play, and checks per-in-play-instance
voluntary-effect usage. Executing Grand Tree's effect marks that instance used
while leaving the ordinary Stadium-play quota unchanged. Spending the Stadium
play quota or disabling Stadium cards *played from hand* does not disable an
already-in-play Grand Tree effect. A failed target evolution leaves the caller's
Stadium instance-use history unchanged.

Tests cover absent or wrong Stadium, spent Stadium-play quota, hand-play lock,
Grand Tree's explicit first-turn evolution prohibition, successful later-turn
activation, repeated use of the same instance, and separate use history for
another same-name Stadium instance. The replacement of one physical Stadium
with another, including replacement timing and play quota, remains owned by
the `stadium_effect_instance_usage.py` lifecycle model. Exact card-specific
search and target prerequisites remain outside this generic source adapter.

**Evidence:** Advanced Player's Rulebook B-04; bundled card record `sv7-136`;
`results/stadium_effect_instance_usage/README.md` for the Brooklet Hill
same-name, different-instance official ruling.
