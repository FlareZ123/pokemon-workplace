# Knock Out trigger-order authority is source-scoped

## Question

Who chooses the order when several triggered effects activate around a Knock Out?

The repository had begun treating the Lost City + Reuniclus interaction as an
authoritative example where the Knocked Out Reuniclus's owner chooses the order.
Current source review shows that this cannot safely be generalized across paper
Expanded without identifying the governing rules source.

Implementation: `tools/ko_trigger_order_authority.py`  
Regression: `results/ko_trigger_order_authority/reproduce.py`

## Evidence as of 2026-10-07

Three source layers currently say different things or cover different scopes.

### TPCi Professor guidance, February 2026

The Pokémon Professor Community article **February 2026 Rule Book Updates -
What you need to know!**, published 2026-02-26, says that additional rulings
changes took effect with the February 20 rulebook update even though they were
not written into the rulebook itself.

Its summary says:

- during a turn, the current player chooses the order of multiple triggered
  effects when a Pokémon is Knocked Out;
- the same current-player rule applies when Energy is attached;
- during Pokémon Checkup, the player who will take the next turn chooses effect
  order;
- existing TCG Rulings Compendium entries on simultaneous-effect choice would
  need to be updated.

Source:
https://professorprogram.pokemon.com/news/11473085

### Pokémon Asia Lost City + Reuniclus Q&A

The Pokémon Asia Trainers Website currently serves a card-specific Q&A saying
that when Reuniclus's Persistent Cells and Lost City both apply, **Reuniclus's
owner** chooses their order.

Persistent Cells first sends Reuniclus to hand. Lost City first sends it to the
Lost Zone.

Source:
https://asia.pokemon-card.com/ph/rules/search/?keyword=Lost+City

The page exposes no publication or revision date in the retrieved result. From
the available evidence alone, it is unclear whether this is an intentional
regional rule difference, a legacy Q&A that has not been revised, or another
source-management issue.

### Bundled Advanced Player's Rulebook Ver. 3.4

The repository's bundled Advanced Player's Rulebook is dated 2025-01-08. It
states that when **several Pokémon are Knocked Out at the same time**, activating
several Knock Out effects in step 2, the player whose turn is being played
chooses their order.

That wording is narrower than the exact single-Reuniclus / two-effect case and
predates the February 2026 TPCi update.

## Result

The current evidence does not support one source-independent ordering authority
for paper Expanded.

For the exact Lost City + Reuniclus state:

| Selected rules source | Controller represented by the model |
| --- | --- |
| TPCi February 2026 Professor guidance | current player |
| Pokémon Asia card-specific Q&A | Knocked Out Reuniclus's owner |
| both admitted simultaneously | unresolved source conflict |

The tool therefore returns every applicable source claim and resolves an
authority only when all selected claims agree.

## Architectural consequence

The existing physical resolver
`tools/knockout_redirection_ordering.py` remains useful. Once a legal effect
order is supplied, its earliest-explicit-destination semantics can execute the
resulting physical movement.

The order-selection layer needs an explicit rules profile or tournament
authority. A simulator should not infer that controller from card ownership,
turn ownership, or an old Q&A without recording the source being applied.

A useful state pipeline is:

`rules profile -> ordering controller -> chosen trigger order -> physical destination resolution`

This also makes source-version changes auditable. If the Pokémon Asia Q&A is
later revised or TPCi publishes a more specific ruling, the authority layer can
change without rewriting physical conservation code.

## Confidence and limits

**High confidence** that the cited sources currently conflict in their literal
guidance for the relevant class of ordering question.

**Moderate confidence** that this reflects a true rules-authority/profile issue
rather than one source simply being stale. The available Pokémon Asia page
does not expose enough revision metadata to distinguish those possibilities.

This result therefore records divergence instead of declaring either source
globally superseded.
