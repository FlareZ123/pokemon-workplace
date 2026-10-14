# Quick Ball policy oracle across hidden deck and Prize allocations

**Verified against pinned Twinleaf `3348ebdc898f175a2ed8f999133cd13d1afd01f5`.**
[Green manual GitHub Actions run 38608719207](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38608719207).
The finding concerns native bot decisions, not paper Expanded card legality
or full-game win rates.

## Why it matters to playable decks

The published [Aichi fifth-place Mew VMAX / Genesect V](../../decks/mew-genesect/)
plays four Quick Ball, and the [tenth-place Regidrago VSTAR](../../decks/regidrago-vstar/)
plays three. Quick Ball searches the full remaining deck for a Basic Pokémon,
conditional on discarding another card from hand. Its actual result depends on
whether eligible Basics are in the deck rather than hidden Prizes.

Twinleaf's native `PlayTrainerTactic` chooses Item actions by evaluating
them on a cloned authoritative state. Consequently, it can learn the actual
search result before deciding whether to commit the Item and its discard.

## Controlled regression

[Reproducer](../../../simulation/twinleaf/test-hidden-prize-search-oracle.cjs):
52 complete two-player fixtures under the pinned TypeScript engine, each
conserving exactly 60 physical cards for each player. The actor holds
Quick Ball and six Grass Energy, has a Regidrago V Active and no occupied
Bench spots, and has 46 cards in deck plus six face-down Prizes. Exactly one
additional Regidrago V is in those 52 hidden locations. The other hidden
cards are Grass Energy. The opponent and all public state remain unchanged.

The test checks every possible location for the second Basic. The combined
unseen deck-and-Prize multiset is identical, and `publicObservation`
serializes identically for all 52 worlds.

| Secret Basic location | Native `PlayTrainerTactic` result | Worlds |
| --- | --- | ---: |
| One of the 46 hidden deck positions | Plays Quick Ball | 46/46 |
| One of the six face-down Prize positions | Holds Quick Ball | 6/6 |

The full `SimpleTacticsAi.decodeNextAction` with native validity simulation
reproduces the difference, yielding `PLAY_CARD_ACTION` for the deck target
and `PASS_TURN` for the Prized target.

If the location were uniformly distributed across the same 52 positions,
an ordinary K0 player would see no difference between the 52 states before
a first deck search. The native decision pays Quick Ball's cost only
in the 46 worlds where the search succeeds. This is another demonstrable
pre-decision information advantage. The fixture is a purpose-built synthetic
60-card state and does not represent a measured tournament opening frequency.

## Methodology and evidence boundary

The test pins the exact engine revision, executes its native card, tactic,
prompt resolver, simulator and bot, asserts legal-sized physical state and
public-equivalence conditions, and exhaustively enumerates all hidden placements.
It is run by the manual-only workflow
[`validate-twinleaf-hidden-prize-search-oracle.yml`](../../../.github/workflows/validate-twinleaf-hidden-prize-search-oracle.yml)
to avoid unnecessary CI budget.

This extends the previous
[top-of-deck search oracle](../twinleaf_hidden_topdeck_oracle/) to a
distinct information channel: **which cards are secretly Prized**. A fixed
top-seven/top-four policy patch does not repair Quick Ball's deck-versus-Prize
foresight. In K1, a player may legitimately infer Prize composition after a
deck search; a complete observation-consistent policy must represent that
information state and the visibility of each search. No competitive win-rate
claims follow from these diagnostic fixtures.

## Next action

Apply actor-observation consistency checks to entire-deck search Items
(Quick Ball, Ultra Ball, Mysterious Treasure) with exact discard payment and
K0/K1 information states. Route native `evaluateAction` through an information
safe expectation or an observation-limited policy before ranking decks.
