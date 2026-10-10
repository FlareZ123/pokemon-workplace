# Poké Ball: historical reprint permission versus reachable target domain

## Concrete counterexample

Six historical pre-Black & White Poké Ball printings permit a search
for "a Basic Pokémon or Evolution card." The Black & White-onward
version permits a search for "a Pokémon." This is a genuine difference
in which targets the **printed effect sentences** describe under the
Pokémon rules governing Restored Pokémon.

The official Pokémon rulebook's Restored Pokémon appendix explicitly
states both facts needed for the witness:

- Restored Pokémon are neither Basic Pokémon nor Evolution cards.
- An effect searching for **a Pokémon** can find Restored Archen.

Source: https://assets.pokemon.com/assets/cms2/pdf/trading-card-game/rulebook/sm5_rulebook_en.pdf
(appendix N; similar text also occurs in the earlier Plasma Storm
rulebook).

For example, with an `Archen bw3-66` among cards in the deck, a
Poké Ball with the broad wording may select it after a heads,
whereas a literal resolution of `ex10-87` cannot. This distinction
exists even if a Basic Snivy and a Stage 1 Servine are available as
ordinary shared targets. With the only Pokémon left in the deck
being Archen, the literal broad wording can find it on heads
(probability 1/2) while the narrow wording has no eligible target.

The bundled card archive contains **13** Expanded-set Restored
Pokémon printings, all of which provide the same target-domain
counterexample. The six historical IDs are
`base2-64`, `base4-121`, `ex1-86`, `ex6-95`,
`ex10-87`, and `ex14-82`. That yields **78** physically
distinct print/witness pairs. Other pre-Black & White Poké Ball
printings already say "Pokémon" and do not exhibit this difference.

## Important policy nuance

The official **March 13, 2012 Modified-Legal Reprint List** expressly
included all six historical Poké Ball prints as usable with
"Reference Required: No." The official document also explains that
some reprinted cards received wording changes and could be played
using more recent text when a reference was required.

Source:
https://assets.pokemon.com/assets/cms/pdf/op/tournaments/2012/2012_modified_legal_reprints.pdf

Therefore, the source-text counterexample is **not** a unilateral
declaration that these six physical prints are currently illegal.
The 2012 list is affirmative historic tournament-policy evidence,
while literal card text and the Restored rules produce a distinguishable
reachable effect. Reconciling this with the 2026 tournament handbook's
functional-identity policy requires explicit official evidence about
old-print treatment and whether the historical permissions persist.

For precisely this reason, the central reprint resolver currently
labels these cards `historical_official_reprint_candidate`.
We preserve that state, flag the underlying effect-domain divergence,
and recommend a separate **official permission** axis alongside
**mechanical equivalence** when interpreting that category.

A search/optimizer which mechanically interprets the old print's
literal text should implement its narrower target domain unless
the applicable card erratum or tournament policy instructs it to
substitute the later wording.

## Reproduce

`python -m results.pokeball_restored_counterexample.reproduce`

The test uses `tools/pokeball_restored_counterexample.py`
and the card archive. It validates every historical source print
and all 13 Restored witnesses, with Basic and Stage 1 controls.

## Boundaries

This is a deterministic, one-Item conditional target-domain proof.
It is independent of deck consistency, opponent matchups, or
post-search shuffling, all of which can affect whether the
distinction matters in a complete game. The test implements
only the Basic, Stage 1, Stage 2, and Restored domain relevant
to the concrete counterexample, and deliberately refuses to
infer classifications for other special stages.
