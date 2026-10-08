# Complete-phrase coverage of fixed and blank printed attack text

## Question

How many legal attack rows are reasonably understood by a conservative
card-text compiler after parsing the printed damage field, and how many
still contain state-changing effects that are invisible to the current
damage, direct-KO, and attack-use-gate safeguards?

## Method

`tools/attack_text_coverage_inventory.py` inventories full attack text
using the live legality-filtered Expanded corpus and reuses the existing
`CompiledAttackBoardSemantics` representation.

It recognizes exact and disjoint semantic islands:

- empty text or a lone global GX-use reminder;
- exact damage-counter placement templates;
- exact Weakness/Resistance bypass instructions;
- exact defender-effect bypass instructions;
- unconditional extra-turn directives, including Pokémon Checkup wording;
- unknown text;
- nonfixed printed damage not yet resolved by the narrow fixed-number compiler.

The catalog records the downstream handler still required even for known
text. An exact match therefore expresses recognized meaning, rather than
claiming full simulation. In particular, the typed damage bridge, counter
placement, global GX budget, and turn-boundary scheduler are distinct
components.

## Live inventory

The 2026-10-08 CI validation counted 19,992 effectively legal attack-print
rows: 5,687 plain fixed/blank or GX-reminder-only, 91 exact counter clauses,
119 exact defender-effect bypasses, 133 exact type-modifier bypasses,
6 exact extra-turn clauses, 10,092 uncompiled effect texts, and
3,864 variable printed-damage expressions.

Among those 10,092 uncompiled text rows, 2,523 already fall under a
specific damage/Knock Out/attack-use guard. The remaining **7,569** have
other unmodeled effect text. A recognized clause still requires its own
typed handler. The inventory is a coverage metric rather than a guarantee
of complete gameplay execution.

CI: https://github.com/FlareZ123/pokemon-workplace/actions/runs/37771177710

## Strict damage-only entry point

`materialize_damage_only_verified()` accepts only text whose complete
currently modeled board consequence is base damage or one of the exact
damage-counter templates. It explicitly rejects effects that need
typed-damage bypass, defender-effect handling, a GX budget, extra-turn
scheduling, or any uncompiled clause.

The live regression identifies **5,765** suitable attack-print rows.
It verifies plain Jet Headbutt and compound Phantom Dive, while rejecting
eight real counterexamples spanning status changes, card movement, draws,
extra turns, and type-effect exceptions. This is a conservative route to
construct damage-only programs, with downstream attack-legality and live
damage modifiers still independently required.

[Strict materializer CI passed](https://github.com/FlareZ123/pokemon-workplace/actions/runs/37771343439).

## Representative omissions outside existing guards

The specific fail-closed flags currently recognize uncompiled text-damage,
direct Knock Outs, and attack-use gates. Several other effects can still
appear on attacks with blank or fixed printed damage:

- Servine Wrap may Paralyze after a coin flip.
- Serperior Leaf Storm heals other Pokémon.
- Pignite Flame Charge attaches Energy from the deck.
- Swanna Aqua Ring switches out the attacking Pokémon.
- Lillipup Collect draws a card.

These can affect later gameplay while a damage-only replay appears correct.
A simulation intending to advance full game state must therefore require
the complete semantic handler set for the attack body.

## Verification

`results/attack_text_coverage_inventory/reproduce.py` compares the
classifier's output against real source cards and audits the intersection
with the current three specific incompleteness flags.

Run it directly or through the repository workflow
`validate-attack-text-coverage-inventory.yml`.

## Limits

The exact-text grammar is deliberately small. Other effects may be
equivalent in meaning to recognized examples yet remain unclassified.
A recognized text clause still needs appropriate live-state inputs,
the right timing, and a complete board transaction to support game-play claims.
