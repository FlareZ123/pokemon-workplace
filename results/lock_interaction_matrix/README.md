# Expanded lock interaction matrix

## Question

How should lock effects in paper Pokémon TCG Expanded be represented so analysis accounts for what they deny, how their source remains active, and whether several locks can coexist on the same board?

The human prior in resources/human_concepts.md identifies lock interaction as a major source of state dependence. It calls out Ability lock, Item lock, Supporter lock, Active Spot contention, Stealthy Hood, and Garbotoxin. This result turns that qualitative idea into a reproducible card-pool catalog plus a structural interaction model.

## Scope

The catalog covers direct denial and suppression effects in the legal Black & White onward paper Expanded card pool. It includes card-play restrictions, Energy or Tool attachment restrictions, evolution restrictions, Ability suppression, Tool/Stadium/Special Energy effect suppression, and probabilistic Trainer-effect suppression.

It excludes ordinary attack denial, retreat denial, Special Conditions, damage prevention, hand disruption, discard effects, and other control mechanics outside this resource-denial model.

Legality follows tools/build_expanded_legality_baseline.py, including its card-level bans and current seven-print official-ban overlay. Effect grouping uses normalized effect text with source identity and structural tags. Gameplay-variant counts use the repository's conservative gameplay fingerprint.

Implementation: tools/lock_effect_catalog.py

Reproducer: results/lock_interaction_matrix/reproduce.py

## Catalog result

Against the bundled 2026-09-16 card snapshot and existing official-ban overlay:

| Quantity | Count |
| --- | ---: |
| Legal source prints with at least one cataloged lock effect | 177 |
| Conservative gameplay variants represented | 116 |
| Distinct lock-effect signatures | 109 |
| Print-effect instances | 181 |
| Attack-applied signatures | 51 |
| Active-dependent signatures | 26 |
| Passive signatures | 14 |
| Stadium-source signatures | 8 |
| Tool-attached-condition signatures | 5 |
| Bench-dependent signatures | 2 |
| Stochastic signatures | 4 |
| Exclusive-choice signatures | 1 |
| Self-vacating lock attacks | 1 |

The denied or suppressed dimensions can overlap:

| Dimension | Signatures |
| --- | ---: |
| Ability suppression | 31 |
| Item play | 25 |
| Stadium play | 13 |
| Supporter play | 9 |
| Special Energy play | 7 |
| Pokémon Tool effect | 7 |
| Pokémon Tool play | 6 |
| Evolution from hand | 5 |
| Trainer play | 4 |
| Ability-bearing Pokémon play | 2 |
| ACE SPEC play | 2 |
| All cards from hand | 2 |
| Energy attachment to a target | 2 |
| Special Energy attachment | 2 |
| Special Energy effect | 2 |
| Stadium effect | 2 |
| Pokémon Tool attachment | 1 |
| Probabilistic Trainer-effect suppression | 1 |

A broad Trainer lock remains represented as Trainer instead of being expanded into Item, Tool, Supporter, and Stadium rows. This preserves the source wording and avoids inflating the dimension counts.

Crobat's Echoing Madness chooses Item cards or Supporter cards, so those dimensions are alternatives. Vileplume's Allergy Storm reaches Item lock or Supporter lock by coin flip. The catalog records exclusive-choice and stochastic flags for those cases.

## Finding 1: activation geometry belongs in the lock state

Twenty-six signatures require the source Pokémon to occupy the Active Spot. Examples include Stoutland's Sentinel, Honchkrow-GX's Ruler of the Night, Galarian Weezing's Neutralizing Gas, Trevenant's Forest's Curse, and Iron Thorns ex's Initialization.

Those effects compete for one board position. A state representation that stores only desired denial dimensions can therefore propose impossible combinations. A useful minimum representation is:

    lock = (denied dimensions, activation geometry, target scope, conditions, persistence)

The 51 attack-applied signatures behave differently because their denial can persist into the opponent's turn after the attack resolves.

## Finding 2: Beheeyem creates a lock handoff primitive

Beheeyem's Mysterious Noise is the only cataloged lock attack whose own text removes the attacker from play while applying a lock. It shuffles Beheeyem and attached cards into the deck, then prevents the opponent from playing Item cards during their next turn.

The Item restriction is applied to the opponent while Beheeyem vacates the Active Spot. A replacement Active can supply another Active-dependent lock during that same opponent turn.

Mechanical examples include Stoutland with Sentinel for Item plus Supporter denial, Honchkrow-GX with Ruler of the Night for Item plus Tool/Special Energy/Stadium denial, and Galarian Weezing with Neutralizing Gas for Item denial plus Ability suppression.

These are board-geometry observations. Their competitive AMR still depends on evolution requirements, Energy, search access, promotion or switching, Bench space, Prize state, and opponent counterplay.

## Finding 3: Item lock does not stop current-rule Pokémon Tool play

The current Advanced Player's Rulebook separates Trainer cards into Items, Pokémon Tools, Supporters, and Stadiums. It also states that older Pokémon Tool cards which had Item printed on them are treated as Pokémon Tools under the current rules.

Vileplume's Irritating Pollen prevents Item cards from being played. Stealthy Hood is a Pokémon Tool. Irritating Pollen therefore does not stop Stealthy Hood by card class.

A Trainer-play lock is broader because Pokémon Tools are a Trainer-card type.

## Finding 4: Tool-effect suppression can defeat Hood while preserving a Tool-attached lock condition

Garbodor's Garbotoxin is active when Garbodor has a Pokémon Tool attached and suppresses other Abilities. Stealthy Hood prevents effects of the opponent's Abilities done to the Pokémon holding Hood, so it can protect Vileplume from an opposing Garbotoxin effect.

Jamming Tower makes attached Pokémon Tools have no effect. Its text does not discard those Tools. The general Tool rules also keep a Tool attached unless another rule or effect removes it.

Garbotoxin checks whether a Tool is attached. It does not require that Tool's effect to be functioning. Jamming Tower can therefore blank Stealthy Hood while the Tool attached to Garbodor still satisfies Garbotoxin's activation condition. Garbotoxin can then suppress Vileplume again.

A simulator needs two separate variables here:

- attachment state: whether a Tool card is physically attached;
- Tool effect state: whether that attached Tool's text is functioning.

Merging those states gives the wrong result for Garbotoxin under Jamming Tower or Lysandre Labs. The same distinction can matter for Genesect's ACE Nullifier and the Flareon, Jolteon, and Vaporeon Awakening Abilities because their source conditions inspect attached Tools or Memory Capsule.

## Finding 5: player locks and Pokémon protection have different targets

The Advanced Player's Rulebook classifies wording such as an opponent being unable to play Item cards from hand as an effect on a player. A Pokémon that prevents effects of attacks done to itself does not automatically stop an Item-lock effect applied to its player.

A stronger rules state should therefore separate player-level play restrictions, Pokémon-level Ability suppression, attached-card effect suppression, and board-slot requirements.

## Method and validation

tools/lock_effect_catalog.py scans every card file from sets marked Expanded legal, removes card-level banned prints and the seven officially banned prints already handled by the legality baseline, then inspects Abilities, attacks, and rule text for denial or suppression patterns.

Each effect records denied dimensions, source kind, activation geometry, target scope, stochastic branching, exclusive choices, self-vacating attacks, exact print IDs, and conservative gameplay fingerprints.

results/lock_interaction_matrix/reproduce.py checks fixed snapshot counts and structural invariants. It asserts that Beheeyem's Mysterious Noise is the sole self-vacating attack in the current catalog, Crobat's Echoing Madness is the sole exclusive-choice lock signature, and the source texts used for the Garbotoxin/Vileplume/Stealthy Hood/Jamming Tower and Beheeyem handoff cases contain the required predicates.

A second coverage audit searched legal Expanded text for opponent-facing forms of can't play, can't attach, no Abilities, no effect, and effects stop working that were absent from the parser. The remaining unmatched records were self-conditions such as Hero's Medal and Full Face Guard, so they were excluded intentionally.

## Limitations and next work

This is a text-structured catalog rather than a complete rules engine. Unusual wording outside the audited vocabulary can still require parser extensions. The current scope also omits attack lock, retreat lock, Special Conditions, damage prevention, hand disruption, and deck denial.

The strongest continuation is a semantic lock-state engine that evaluates a concrete board and resolves suppression dependencies. It should distinguish source activation, target scope, attached-card presence, attached-card effect state, Active Spot occupancy, player-level restrictions, and suppression dependencies. The present catalog can serve as its source inventory.

A second extension is to add attack and retreat denial and evaluate lock packages as constraint intersections.
