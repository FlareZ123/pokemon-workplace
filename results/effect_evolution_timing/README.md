# Effect-based evolution has separate first-turn timing

## Question

When a card effect puts an Evolution Pokémon onto another Pokémon to evolve it, should a simulator apply the ordinary first-turn and same-turn evolution prohibition before resolving the effect?

## Finding

No global evolution gate is sufficient. The Advanced Player's Rulebook gives effect-based evolution its own timing rule in C-12. Unless the card specifies otherwise, an effect that says to put an Evolution Pokémon onto another Pokémon to evolve it can do so during the player's first turn or on the turn that Pokémon entered play. Ordinary evolution in A-05 remains prohibited in those windows.

This creates separate timing dimensions. The compiler records the player's first-turn policy, the target's entry-turn policy, and the source action's own availability.

The conservative legal-card scan finds **115 print-level direct-evolution profiles across 53 card names**. For the player's first-turn axis, **76 rely on C-12's default permission**, **9 state an explicit permission**, and **30 explicitly block the window**. For the target-entry-turn axis, the counts are **76 default**, **10 explicit**, and **29 blocked**.

A text scanner that searches only for phrases such as "during your first turn" misses most of this surface. A simulator that applies one ordinary-evolution boolean to every evolution transition rejects legal effect-based lines.

## Rules basis

The bundled Advanced Player's Rulebook separates the cases:

- A-05 says neither player can evolve normally during their first turn, and a Pokémon just put into play cannot evolve that turn.
- C-12 covers effects that put an Evolution Pokémon onto another Pokémon to evolve it. It states that, unless specified otherwise, this kind of effect can evolve during the first turn or on the turn the Pokémon was played.

The ordinary source action still matters. Official Pokémon TCG rules state that the player going first cannot play a Supporter on their first turn. An effect such as Salvatore can therefore use C-12 timing when the source Supporter is legal, which gives it a structural first-turn window going second under the ordinary rules.

Official corroboration:

- Pokémon TCG Rules, evolution notes and first-player Supporter restriction: https://assets.pokemon.com/assets/cms2-fi-fi/pdf/trading-card-game/rulebook/swsh9_rulebook_en.pdf
- Official March 2026 strategy article uses Salvatore to evolve and attack on the first turn when going second: https://www.pokemon.com/us/features/pokemon-trading-card-game-live-starter-deck-strategies-march-2026

## Method

tools/effect_evolution_timing.py scans the bundled English card pool after the repository's effective Expanded ban overlay. It intentionally compiles a narrow literal semantic island. An effect qualifies only when its text directly matches one of these forms:

- put ... onto ... to evolve
- put ... on/onto ... . (This counts as evolving ...)

The compiler records the card, effect source, source channel, first-turn policy, entry-turn policy, source-action first-turn window, and the composed structural first-turn window.

The scan does not infer strategic executability from that structural window. Energy requirements, attack costs, card availability, search targets, locks, coin flips, Bench state, activation prerequisites, and other effects remain separate gates.

## Card-pool result

| Measure | Count |
| --- | ---: |
| Direct-evolution print profiles | 115 |
| Unique card names | 53 |
| First-turn: C-12 default permission | 76 |
| First-turn: explicit permission | 9 |
| First-turn: explicitly blocked | 30 |
| Entry-turn: C-12 default permission | 76 |
| Entry-turn: explicit permission | 10 |
| Entry-turn: explicitly blocked | 29 |
| Attack sources | 61 |
| Ability sources | 22 |
| Item sources | 20 |
| Supporter sources | 11 |
| Stadium sources | 1 |
| Structural first-turn window for both players | 20 |
| Structural first-turn window going second only | 65 |
| No structural first-turn window | 30 |

There are **41 unique card names** in the C-12-default group. Nine of those names have a source channel that is structurally available to either player on their first turn in the modeled base rules: Caterpie, Clefable, Duskull, Eevee, Inkay, Karrablast, Metapod, Pidove, and Skiploom.

## Concrete counterexamples

### Eevee, Energy Evolution (sm1-101)

Energy Evolution says that after attaching a matching Basic Energy, the player may search for a card that evolves from Eevee and put it onto Eevee to evolve it. The text contains no explicit first-turn permission. C-12 supplies that permission by default. Since the source is an Ability rather than an attack or Supporter, its structural first-turn window is available to either player, subject to its own Energy-attachment trigger and all other live restrictions.

This is the cleanest counterexample to a text-only exception scanner.

### Salvatore (sv5-160)

Salvatore explicitly allows the target to be a Pokémon put down during setup or put into play that turn, while the first-turn permission itself comes from C-12. Its source is a Supporter, so ordinary first-player Supporter timing narrows the structural first-turn window to the player going second.

This demonstrates why effect timing and source timing need separate state dimensions.

### Technical Machine: Evolution (sv4-178)

The attack puts searched Evolution cards onto up to two Benched Pokémon to evolve them. Its evolution body receives C-12's default first-turn permission. The attack source normally leaves a first-turn window only for the player going second. A model that sees only the evolution timing would overstate access for the player going first.

### Exeggcute, Precocious Evolution (sv8-1)

Precocious Evolution says the attack can be used during the first turn even when going first, then directly evolves Exeggcute. Both layers are open, so the structural first-turn window is available to either player.

### Phantump, Spiteful Evolution (me4-38)

Spiteful Evolution explicitly blocks the Ability during the player's first turn. Its text does not block the turn Phantump entered play, so C-12 still supplies entry-turn permission on a later turn. This is a direct counterexample to collapsing the two timing axes into one boolean.

### Rare Candy and Grand Tree

Rare Candy (sv1-191) explicitly says it cannot be used during the first turn or on a Basic Pokémon put into play that turn. Grand Tree (sv7-136) similarly blocks evolving a Basic during the player's first turn or during the Basic's entry turn. These texts override C-12's default permission on both axes.

## Modeling consequence

A reusable transition model should encode evolution origin and source-action timing separately. A compact representation can carry at least:

- ordinary_evolution, which uses A-05 timing;
- effect_evolution first-turn policy;
- effect_evolution entry-turn policy;
- the source action channel and its own turn restrictions.

A planner may project these dimensions to a simple executable edge only after all relevant gates are known for the current state.

## Limitations

The compiler is deliberately conservative and English-text based. It does not claim to capture every semantically equivalent historical wording. It also does not evaluate prerequisites beyond the source channel's basic first-turn timing. The counts describe the bundled snapshot under the repository's current legality overlay, so later card releases, bans, errata, or broader semantic normalization can change them.

The structural_first_turn_window field should therefore be read as a timing upper bound for the represented source and evolution rules. It is not a probability of executing the line and is not evidence that the necessary cards or resources are available.

## Reproduction

Run:

    python results/effect_evolution_timing/reproduce.py

The regression checks the aggregate counts, representative default-permitted, explicit-permitted, and blocked cases, plus a negative example that mentions evolution in a trigger without directly evolving the card put onto the Bench.

## Confidence

High confidence in the rules distinction and in the compiled literal family. Moderate confidence that this literal family captures every strategically relevant direct-evolution wording in the bundled pool, because the scan intentionally avoids speculative normalization of ambiguous historical text.
