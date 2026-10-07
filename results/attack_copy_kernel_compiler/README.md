# Lowering attack-copy contracts into the execution kernel

## Question

Can the legal Expanded copy-signature catalog be converted into print-specific
kernel definitions without hand-authoring selectors for every regression?

For most signatures, yes. The lowering layer is conservative about outer
conditions the current kernel cannot represent.

Implementation: `tools/attack_copy_kernel_compiler.py`  
Regression: `results/attack_copy_kernel_compiler/reproduce.py`

## Source-class lowering

All 15 source classes in the current 30-signature catalog have a selector
mapping:

- own discard Dragon -> own discard, Dragon required;
- own Bench Fusion Strike -> own Bench, Fusion Strike required;
- own Bench N's Pokémon -> own Bench, name prefix required;
- own Bench any -> own Bench;
- previous Evolutions -> actor previous-evolution attacks;
- own deck top card -> own deck top;
- opponent top-10 reveal -> opponent revealed cards;
- opponent hand -> opponent hand;
- opponent last attack -> opponent last attack state;
- opponent Active Tera -> opponent Active, Tera subtype required;
- opponent Active non-GX -> opponent Active, non-GX required;
- opponent Active any -> opponent Active;
- opponent in play -> opponent Active or Bench;
- opponent chooses in play -> same source, opponent chooser;
- opponent's Pokémon -> opponent in play.

Contract flags then add selected-Energy gates, source movement, optionality, and
post-copy continuation.

Seek Inspiration's no-Rule-Box filter is also preserved from its raw text.

## Explicit unsupported outer gates

Six signatures contain conditions that the current copy kernel does not own:

- Assist: coin flip;
- Mini-Metronome: coin flip;
- Pendulum Influence: coin flip;
- Try to Imitate: coin flip;
- Nightcap: opponent must have exactly two Prize cards remaining;
- Skill Thief: actor hand must be empty.

Those print rows receive no executable `AttackDef`. They carry an explicit
unsupported condition instead.

This matters because a selector-only lowering would make those attacks appear
available in states where their outer gate fails.

## Haughty Order witness

Team Rocket's Persian ex `sv10-150` now lowers from card data plus the existing
contract compiler to an `AttackDef` with:

- opponent revealed-card source;
- optional selection;
- pre-event `reveal_top_10`;
- post-event `shuffle_revealed`;
- printed Energy cost.

The regression combines that generated outer definition with the generated
Phantom Dive leaf definition from `simple_attack_board_semantics.py`.

Nested resolution records:

`reveal_top_10 -> Phantom Dive body -> shuffle_revealed`

No hand-authored Haughty selector or continuation is needed.

## Other contract witnesses

The regression also checks:

- Seek Inspiration precommits the top card to discard and requires no Rule Box;
- Hypnotic Reign commits the selected hand Pokémon to discard and filters GX
  attacks;
- Copy Anything requires the copying Pokémon to satisfy the selected attack's
  Energy cost;
- Mimed Games assigns source choice to the opponent;
- Apex Dragon requires a Dragon source in the actor's discard pile;
- Trickster-GX remains a GX attack for the player-global GX budget.

## Finding

The copy research stack can now be divided into two compiler layers:

1. copy-signature contracts describe source geometry and execution gates;
2. print-specific lowering turns supported contracts into executable kernel
   definitions.

Unsupported outer conditions remain visible at the compiler boundary instead of
being silently erased.

## Limits

The kernel still lacks first-class coin flips, hand-size predicates, and
Prize-count predicates for attack-use conditions. Adding those state channels
would make the six currently refused signatures candidates for full lowering.

Hidden-information procedures are still abstracted. Haughty Order's pre-event,
for example, records the reveal boundary but expects the selected revealed
source to already be represented in the kernel state.
