# Historical Trainer semantic divergences

## Question

Can unresolved historical same-name Trainer prints be ruled out by current rules and direct reachable-state witnesses rather than by text distance?

## Result

Yes. Five unresolved Trainer families contain nine historical prints with direct semantic divergences from a legal Expanded print:

| Name | Historical prints | Axis | Distinguishing state |
| --- | ---: | --- | --- |
| Apricorn Maker | 1 | target domain | Ball Guy is a legal Expanded Supporter with `Ball` in its name. Historical Apricorn Maker can search a Trainer card with Ball in its name; the current print is restricted to Item cards. |
| Friend Ball | 1 | target domain | Restored Archen is neither Basic nor Evolution under the official rules. Historical Friend Ball cannot search it, while current Friend Ball can search any same-type Pokémon. |
| Pokémon Fan Club | 2 | material transition | With an open Bench and an eligible Basic Pokémon in deck, the historical effect puts the Pokémon directly onto the Bench; the current effect puts it into hand. |
| Super Potion | 2 | material transition | With exactly 60 damage and an attached Energy, the historical effect can remove at most four damage counters (40 damage), while the current effect heals all 60. |
| TV Reporter | 3 | material transition / playability | With an empty deck, another card in hand, and an unused Supporter action, the current print is explicitly unplayable. The historical text can resolve the unavailable draw as zero and still discard the other hand card, changing the game state. |

All nine historical source prints are therefore added to the resolver's `known_non_equivalent` evidence set.

## Rules basis

The current Advanced Player's Rulebook supplies the relevant semantics:

- Trainer cards include Items, Pokémon Tools, Supporters, and Stadiums, so a Supporter such as Ball Guy is still a Trainer card.
- healing damage means removing damage counters;
- card instructions can resolve the parts that are possible even when another part cannot be applied, subject to explicit dependency wording;
- when a specified quantity is unavailable, the closest possible quantity is applied;
- a Supporter cannot be played when resolving its effect would not change the game state.

The TV Reporter witness uses those rules together. Emptying the deck during a turn does not itself end the game because deck-out is checked when a player must draw at the beginning of their turn. Historical TV Reporter can therefore exist in a reachable empty-deck action window.

## Card-text evidence

### Apricorn Maker

Historical `ecard3-121` searches for up to two **Trainer cards** with Ball in their names.

Current `sm7-124` searches for up to two **Item cards** with the word Ball in their names.

`swsh45-57` Ball Guy is a directly legal Expanded Supporter and provides the distinguishing target.

### Friend Ball

Historical `ecard3-126` searches only for a Baby Pokémon, Basic Pokémon, or Evolution card matching the chosen opponent Pokémon's type.

Current `sm7-131` searches for any Pokémon matching an opponent Pokémon's type. Official Pokémon TCG rules for Restored Pokémon explicitly state that Restored Pokémon are neither Basic Pokémon nor Evolution cards, and that a generic search for a Pokémon can find them. Expanded-legal Fighting Restored Archen `bw3-66` therefore provides a direct distinguishing target when the opponent has a Fighting Pokémon in play.

Official rules source: `https://assets.pokemon.com/assets/cms2-nb-no/pdf/trading-card-game/rulebook/swsh5_rulebook_en.pdf`, Appendix S.

### Pokémon Fan Club

Historical `ecard2-130` and `pop4-9` put searched Basic Pokémon directly onto the Bench.

Current `sm5-133` puts the searched Basic Pokémon into the hand.

The same selected Basic therefore ends in different physical zones.

### Super Potion

Historical `base1-90` and `base4-117` remove up to four damage counters after discarding an attached Energy.

Current `xy1-128` heals 60 damage and then discards an attached Energy.

With six damage counters and an attached Energy, the historical and current effects necessarily leave different damage states.

### TV Reporter

Historical `ex15-82`, `ex3-88`, and `pop2-11` say only to draw three cards and then discard a card.

Current `sm7-149` adds an explicit prohibition when the deck has no cards.

With an empty deck and another hand card available, current rules let the historical effect apply the closest possible draw count, zero, and then perform the discard. The current print cannot be played at all.

## Evidence classes

**Current rule facts.** Trainer type hierarchy, healing semantics, partial resolution, closest-possible quantities, and Trainer playability conditions come from the bundled Advanced Player's Rulebook.

**Card-text facts.** The bundled card database preserves every source, target, and Ball Guy witness fragment used by the proof.

**State-model proofs.** Each family has an explicit state in which the reachable target set or resulting physical state differs.

## Tooling

`tools/trainer_semantic_divergence.py` stores the four audited cases, validates source and target identity, checks direct Expanded legality for the target prints, validates the Ball Guy and Restored Archen witnesses, and exposes compact distinguishing states.

The collector returns the eight historical source IDs as explicit negative reprint evidence.

## Reproduction

Run:

`python -m results.trainer_semantic_divergence.reproduce`

The regression validates all four families and checks that every source resolves as `known_non_equivalent` after integration.

## Limitations

This result proves state-model non-equivalence. It does not claim that a current tournament document has separately named these four families as official functional-reprint examples.

The analysis is deliberately narrow. It does not infer broader equivalence or non-equivalence for other historical Trainers from wording similarity alone.

## Next work

Several remaining semantic-review families are still promising:

- Friend Ball has a possible target-domain distinction involving Restored Pokémon and needs an explicit rules-backed classification check.
- VS Seeker, Lure Ball, Moomoo Milk, Maintenance, Energy Recycle System, and Pokémon Communication look more like positive semantic-equivalence candidates and should be handled with proofs that preserve public/private information and intermediate zones.
- Computer Search needs rule-category analysis because the current print is an ACE SPEC.
