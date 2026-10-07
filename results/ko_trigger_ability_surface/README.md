# Immediate Knock Out Ability trigger surface

## Question

What semantic work can effectively legal paper Expanded Abilities create at the
immediate Knock Out trigger boundary?

Implementation: `tools/ko_trigger_ability_catalog.py`  
Regression: `results/ko_trigger_ability_surface/reproduce.py`

## Method

The catalog scans effectively legal cards in Expanded-legal sets using the
repository's current legality baseline. It conservatively recognizes Ability
clauses whose condition says a Pokémon **is Knocked Out**.

It deliberately excludes nearby wording families that belong to different
timing semantics:

- damage-trigger text containing `(even if ... Knocked Out)`;
- prevention/replacement text saying a Pokémon `would be Knocked Out`;
- prior-turn memory such as `were Knocked Out during your opponent's last turn`;
- Abilities whose effect causes their own Pokémon to be Knocked Out.

The bundled Gengar ex typo `Knocket Out` is normalized exactly as in the earlier
cascade catalog.

## Surface

The current bundled card pool yields **82 legal print rows across 50 card
names**, representing **54 distinct Ability-name/text/trigger-scope
signatures**.

Trigger scope by print:

| Trigger subject | Prints | Distinct signatures |
| --- | ---: | ---: |
| this Pokémon | 56 | 43 |
| another/allied Pokémon | 11 | 5 |
| opponent's Pokémon | 14 | 5 |
| Pokémon carrying this card after Shedinja becomes a Tool | 1 | 1 |

The effect-family tags are intentionally nonexclusive because one trigger can
change more than one state axis.

| Consequence family | Prints | Distinct signatures |
| --- | ---: | ---: |
| Prize modification | 29 | 14 |
| Energy relocation/recovery | 11 | 7 |
| Deck search | 9 | 7 |
| Damage counters | 9 | 8 |
| Attacking Pokémon Knock Out | 7 | 5 |
| Pokémon destination redirection | 7 | 5 |
| Deck mill | 4 | 3 |
| Hand disruption | 3 | 3 |
| Energy disruption | 2 | 1 |
| Promotion control | 1 | 1 |
| Special Condition | 1 | 1 |

Every matched print falls into at least one of these consequence families.

## Scheduler consequence

The earlier KO cascade result studied the narrow subset that can create an
additional Knock Out. This audit shows that the immediate trigger window is a
much broader state-transition surface.

Representative branches include:

- Gengar ex Fainting Spell: can add the Attacking Pokémon to KO membership;
- Huntail Diver's Catch: reroutes attached Basic Water Energy before disposal;
- Reuniclus Persistent Cells and Tyranitar-GX Lost Out: redirect physical card
  destinations;
- Gastly Swelling Spite and Radiant Jirachi Entrusted Wishes: search the deck;
- Shedinja Vessel of Life, Mega Gengar ex, Togekiss, Lugia-EX, and others:
  alter Prize awards;
- Hypno Hypnotic Pendulum: changes who controls the opponent's replacement
  Active choice.

A general KO scheduler therefore needs to preserve more than a growing set of
doomed Pokémon. Trigger semantics can mutate resources, hidden information,
Prize amounts, destination routing, board position, and future trigger
eligibility before the common disposal/Prize boundary.

## Representation consequence

A useful architecture is:

`trigger discovery -> authority/ready scheduling -> card-specific transition -> trigger discovery again -> stable KO batch -> disposal -> Prize handling -> promotion`

The card-specific transition layer cannot be reduced to a single `mark another
Knock Out` callback. The catalog gives a finite, auditable set of consequence
families for expanding that layer incrementally.

## Limits

This is a conservative literal-text catalog rather than a complete natural
language parser. It only classifies Ability text in the bundled English
snapshot. The family labels describe state axes touched by the text and are not
claims that two cards in one family have identical semantics.

Counts are print-level except where explicitly labeled as distinct signatures.
A future compiler should preserve eligibility predicates, optionality, coin
flips, targets, quantities, and ownership rather than executing from these
coarse family labels alone.
