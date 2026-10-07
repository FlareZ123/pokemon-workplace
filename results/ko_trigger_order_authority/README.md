# Knock Out trigger-order authority is source-scoped

## Question

Who chooses the order when several triggered effects activate around a Knock Out?

Current evidence cannot be collapsed into one source-independent answer for
paper Expanded. The physical destination resolver can execute a supplied order,
while the authority that chooses that order depends on the rules source and
scope being applied.

Implementation: `tools/ko_trigger_order_authority.py`  
Regression: `results/ko_trigger_order_authority/reproduce.py`

## Evidence as of 2026-10-07

Four source layers currently say different things or cover different scopes.

### TPCi Professor guidance, February 2026

The Pokémon Professor Community article **February 2026 Rule Book Updates -
What you need to know!**, published 2026-02-26, says additional rulings changes
took effect with the February 20 rulebook update.

Its summary says:

- during a turn, the current player chooses the order of multiple triggered
  effects when a Pokémon is Knocked Out;
- the same current-player rule applies when Energy is attached;
- during Pokémon Checkup, the player who will take the next turn chooses effect
  order;
- when one effect triggers another, finish the initial effect before handling
  the newly triggered effect.

Source:
https://professorprogram.pokemon.com/news/11473085

### Pokémon Asia Lost City + Reuniclus Q&A

The Pokémon Asia Trainers Website currently serves a card-specific Q&A saying
that when Reuniclus's Persistent Cells and Lost City both apply, **Reuniclus's
owner** chooses their order.

Persistent Cells first sends Reuniclus to hand. Lost City first sends it to the
Lost Zone.

Source:
https://asia.pokemon-card.com/sg/rules/search/?keyword=Lost+City

### Pokémon Japan Lost City Q&A

The current Japanese official Q&A search gives the same owner-choice answer for
Lost City + Reuniclus. It also contains a second card-specific interaction:

- Lost City + Tyranitar-GX Lost Out;
- the owner of the Knocked Out Pokémon chooses the effect order;
- Lost Out first sends the Pokémon and attached cards to the Lost Zone;
- Lost City first sends the Pokémon to the Lost Zone while non-Pokémon attached
  cards are discarded.

Source:
https://www.pokemon-card.com/rules/faq/search.php?freeword=%E3%83%AD%E3%82%B9%E3%83%88%E3%82%B7%E3%83%86%E3%82%A3&regulation_sidebar_form=all

The Japan and Asia Reuniclus answers therefore agree with one another. The
Japanese database supplies an additional same-family owner-choice witness.

### Bundled Advanced Player's Rulebook Ver. 3.4

The repository's bundled Advanced Player's Rulebook states that when **several
Pokémon are Knocked Out at the same time**, activating several Knock Out effects
in step 2, the player whose turn is being played chooses their order.

That wording is narrower than either single-Pokémon Lost City conflict above.

## Result

For the exact Lost City + Reuniclus state:

| Selected rules source | Controller represented by the model |
| --- | --- |
| TPCi February 2026 Professor guidance | current player |
| Pokémon Asia card-specific Q&A | Knocked Out Reuniclus's owner |
| Pokémon Japan card-specific Q&A | Knocked Out Reuniclus's owner |
| Asia + Japan together | Knocked Out Reuniclus's owner |
| TPCi + Asia/Japan | unresolved source conflict |

The current Japanese Lost City + Lost Out Q&A creates the same source-profile
conflict against the broad TPCi during-turn statement.

The tool therefore records every applicable source claim and resolves an
authority only when all selected claims agree.

## Relationship to the shared effect-order authority work

The repository also contains `tools/effect_order_authority.py` and
`tools/effect_order_authority_overlap.py`. Those modules model evidence-backed
timing cases after an upstream semantic layer has decided which cases apply.

This source-profile result answers a different question: **which currently
served source family is supplying the ordering rule?**

A safe integration order is:

`rules source/profile -> applicable authority cases -> concrete chooser or conflict -> chosen effect order -> physical execution`

The source-profile layer should therefore feed, rather than replace, the shared
authority-case resolver.

## Architectural consequence

The existing physical resolver
`tools/knockout_redirection_ordering.py` remains useful. Once a legal effect
order is supplied, its earliest-explicit-destination semantics can execute the
resulting physical movement.

A simulator should retain the rules source or tournament authority used to
select an ordering policy. That provenance lets future rule updates change the
authority layer without rewriting physical conservation code.

## Confidence and limits

**High confidence** that the cited official source families currently expose
different literal chooser guidance for these states.

**Moderate confidence** about why. The evidence available here does not prove
whether TPCi intends a global override, whether the Japan/Asia card-specific
answers are exceptions, or whether current regional rules differ.

This result therefore preserves the divergence explicitly instead of declaring
one currently served official source silently obsolete.
