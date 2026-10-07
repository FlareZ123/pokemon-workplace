# Attack-use requirements depend on invocation context

## Question

If an attack says that it can be used only when a condition is true, what
happens when another attack selects it and uses it as the copied body?

The condition still matters, but selection and direct declaration have
different failure boundaries.

## Primary evidence

The current Advanced Player's Rulebook describes `use it as this attack` as
executing the chosen attack's effects and damage while preserving the identity
of the outer attack. Its Foul Play examples also show that copied-body
instructions are evaluated on the copying Pokémon and that impossible
non-cost instructions can be skipped according to the ordinary partial-
resolution rules.

A more direct official ruling appears in the Japanese Pokémon Card Game Q&A:

- Slowking's **Inspiration Challenge** discards the top card of its deck and,
  when that card is an eligible Pokémon, selects one of that Pokémon's attacks
  and uses it as Inspiration Challenge.
- The official Q&A asks what happens when the discarded Pokémon is Sableye and
  the selected attack is **Lost Mine**, whose text says it can be used only
  with at least 10 cards in the player's Lost Zone.
- The ruling says Lost Mine **may be selected**. If the player has fewer than
  10 cards in the Lost Zone, the attack's processing is not performed and the
  attack ends.

Official card:
https://www.pokemon-card.com/card-search/details.php/card/45978/regu/XY

Official Q&A:
https://www.pokemon-card.com/rules/faq/search.php?freeword=%E3%83%A4%E3%83%89%E3%82%AD%E3%83%B3%E3%82%B0

Current English Advanced Player's Rulebook:
https://asia.pokemon-card.com/sg/wp-content/uploads/sites/6/2025/10/EN_advanced_manual-2025.pdf

## State-machine consequence

A requirement such as:

`You can use this attack only if CONDITION.`

needs invocation context.

### Direct declaration

The requirement is checked before the attack can be announced. If false, the
attack cannot be declared.

### Copied-body invocation

The selecting copy effect can still choose the attack. The requirement is then
checked while entering that selected body. If false, the selected attack body
does not process.

This creates three distinct concepts that should not be collapsed:

1. **selection eligibility**: can the outer copy effect name this attack?
2. **declaration eligibility**: could this attack itself be announced?
3. **copied-body executability**: after selection, does its body process?

The Slowking/Lost Mine ruling proves that (1) can be true while (3) is false.

## Implementation impact

`attack_copy_outer_control.evaluate_outer_control()` now accepts
`invocation_mode`.

For the currently compiled Nightcap requirement:

- false under `declared` -> `declaration_illegal`;
- false under `copied_body` -> `resolve_without_copy`.

Skill Thief's empty-hand condition and the four coin gates are body controls in
either invocation context.

The direct controlled executor intentionally remains scoped to the announced
attack. A later nested integration should evaluate controlled selected bodies
inside the recursive copy kernel rather than pre-filtering them out of the
candidate set.

## Strategic implication

A reachability model that deletes condition-failing attacks from copy target
sets is too strict. Some copy effects can legally select the attack and consume
the attack window even though the selected body then produces no useful
effect.

That distinction can matter for attack-history lines, coin-dependent AMR,
nested copies, and any planner that assigns value to failed or deliberately
chosen no-effect bodies.
