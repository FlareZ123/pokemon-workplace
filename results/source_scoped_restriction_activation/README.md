# Source-scoped restriction activation and duration geometry

## Question

The source-scoped permission predicate answers whether an already-active restriction blocks a concrete card action. A separate problem is deciding when that restriction exists.

This result compiles activation geometry, application gates, and duration for the same 106 print-level direct restrictions.

Implementation: `tools/source_scoped_restriction_activation.py`

Regression: `results/source_scoped_restriction_activation/reproduce.py`

## Activation families

The current bundled legal snapshot produces:

| Activation family | Print-level rows |
| --- | ---: |
| Attack-applied | 77 |
| Active Spot Ability | 22 |
| General in-play Ability | 4 |
| Relative Pokémon-count Ability | 1 |
| Tool-attached Ability | 1 |
| Stadium-required Ability | 1 |

All 29 Ability restrictions are continuous effects. They require their source to remain in play and its Ability to remain effective.

The 77 attack-applied restrictions are stored independently of the attacking source after the attack applies them. Their later legality therefore should not be recomputed from whether the attacker remains in play.

## Duration families

The duration audit yields:

| Duration | Rows |
| --- | ---: |
| Opponent's next turn | 76 |
| Continuous | 29 |
| Until end of the user's next turn | 1 |

Vanilluxe `xy8-45` / Frigid Breath is the unique longer attack window in this family. It prevents both players from playing Supporters or Stadiums from hand until the end of the attack user's next turn.

This duration is materially different from the common opponent-next-turn lock. A turn-state kernel must retain the effect across the opponent's turn and the attack user's following turn.

## Application gates

Attack text also determines whether a pending restriction is created:

| Gate | Rows |
| --- | ---: |
| Unconditional attack application | 71 |
| Continuous Ability condition | 29 |
| Heads-only coin gate | 3 |
| Stadium discard followed by "if you do" | 1 |
| Player-selected exclusive branch | 1 |
| Coin-selected exclusive branch | 1 |

The three heads-only restrictions are Psyduck `sm9-26` / Headache, Shuppet `sv1-87` / Enveloping Shadow, and Krookodile `xy1-71` / Bother.

Chi-Yu `me1-31` / Scorching Earth applies its hand restriction only after its Stadium-discard prerequisite succeeds.

Crobat `sv4-112` / Echoing Madness uses a player-selected Item-or-Supporter branch. Vileplume `swsh11-3` / Allergy Storm uses a coin-selected Supporter-or-Item branch. These application gates compose with the separate exclusive-branch resolver from the source-scoped restriction compiler.

## Continuous Ability witnesses

The audit preserves several distinct continuous geometries:

- Vileplume `xy7-3` / Irritating Pollen is a general in-play restriction.
- Team Rocket's Arbok `sv10-113` / Potent Glare requires the source to be in the Active Spot.
- Genesect `sv6pt5-40` / ACE Nullifier requires a Pokémon Tool attached to the source.
- Barbaracle `xy10-23` / Hand Block requires a Stadium in play.
- Omastar `sm9-76` / Fossil Bind depends on having fewer Pokémon in play than the opponent.

These conditions belong upstream of transaction legality. A caller should derive the currently active restriction set from board state and Ability-suppression state, then pass that set to the permission layer.

## Finding

Source-scoped restriction state has at least four separable layers:

1. source activation geometry;
2. attack application or continuous-effect gate;
3. branch resolution where card text offers mutually exclusive restrictions;
4. action-level source, selector, and target legality.

Keeping these layers separate prevents several common modeling errors. A continuous Ability lock should disappear when its source or Ability stops functioning. An attack-applied player restriction can persist after the attacker leaves play. A coin or player choice must be resolved before an exclusive restriction is projected into scalar channels.

## Limits

The compiler classifies the represented direct restriction family. It does not execute attack costs, check whether an attack itself was legal, flip coins, choose branches, or mutate the board.

For continuous Abilities, this result records the condition family rather than owning a complete board evaluator. Causal Ability-lock resolution from the existing Ability-lock kernels remains the natural upstream source for whether the Ability is effective.

The duration labels still need a turn-window owner that advances and expires pending attack restrictions at the correct event boundary.
