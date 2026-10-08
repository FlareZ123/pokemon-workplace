# Zone-dependent discard value: Ultra Ball feeds Teleport Room

## Question

Can a Stadium become **more executable after being discarded** than while held
in hand? Can the order of an Item search and an existing Pokémon Ability
change how many Bench entrants succeed?

Yes, in a tightly specified paper Expanded state. This result composes the
canonical Trainer transaction (`trainer_search_transaction`) with the
physical Stadium-entry/Bench-capacity bridge
(`bench_teleport_capacity_bridge`).

- Implementation: [`tools/teleport_discard_payload_line.py`](../../tools/teleport_discard_payload_line.py)
- SFT: [`reproduce.py`](reproduce.py)
- Successful CI: [run 37771391083](https://github.com/FlareZ123/pokemon-workplace/actions/runs/37771391083)

## Grounding

- **Ultra Ball** `swsh9-150` requires discarding two *other* cards from hand
  to search the deck for a Pokémon.
- **Gothitelle** `xy3-41` / Teleport Room can discard the Stadium in play,
  then puts one differently named Stadium from **your discard pile** into play.
- **Sky Field** `xy6-89` allows eight Benched Pokémon.
- **Collapsed Stadium** `swsh9-137` limits each Bench to four Pokémon.
- The normal Stadium play action is limited to once per turn; effects that
  move a Stadium into play do not automatically spend that quota.

Card text, general Trainer action timing, and the no-replacement Teleport
resolution are established in the source files and the prior
[`stadium_entry_channels`](../stadium_entry_channels/) investigation.

## Controlled starting state

An already established Active Gothitelle has an unused Teleport Room Ability.
Collapsed Stadium is in play; four ordinary Pokémon fill the Bench; the
ordinary Stadium-play quota for the turn is already spent. Hand contains one
Sky Field, one Ultra Ball, two arbitrary available discard cards, and one
Basic entrant. One more eligible Basic entrant is in the deck.

The model does **not** assume anything about drawing or evolving into this
state. These resources and positions are specified rather than sampled.

The physical Trainer representation tracks Sky Field, Collapsed Stadium, Ultra
Ball, both junk cards, and the two entrant identities across hand, deck,
discard, Stadium-in-play and Bench zones.

## Executed comparison

| Same resources and Ultra Ball usage | Teleport result | Required entrants Benched |
| --- | --- | ---: |
| Ultra Ball discards Sky Field + junk A, searches second Basic, then Teleport | Sky Field moved from discard into play (capacity 8) | **2** |
| Ultra Ball discards junk A + junk B, searches second Basic, then Teleport | No eligible differently named discard replacement (capacity 5) | **1** |
| Teleport first, then Ultra Ball discards Sky Field + junk A | Teleport already used, Sky Field stranded in discard (capacity 5) | **1** |
| Successful Sky Field payload while opposing Roadblock remains live | Sky Field enters play but Bench still capped at 4 | **0** |

These are exact, deterministic branch results for the fixed state, rather than
estimated deck-wide frequencies.

Every Ultra Ball branch pays exactly two other cards and retrieves exactly one
Basic Pokémon. The canonical transaction correctly moves the played Item to
the discard pile and preserves the ordinary Stadium-play budget. A strict
projection compares the physical Sky Field and Collapsed Stadium copy zones
with the Trainer's card-class zone counts before and after reconciliation.
After the successful line, both entrants move from hand to Bench; all
represented card-class totals are conserved.

The regression also confirms that Item lock rejects Ultra Ball. It tests the
ordering counterexample with a correctly synchronized counted Stadium state,
including Collapsed Stadium's earlier removal.

## Strategic meaning

In the tested position, **Sky Field is a valuable discard target**, despite
normally being a valuable Stadium to hold. Its destination changes which
action channel can access it:

- Hand -> ordinary Stadium play, whose quota has expired.
- Discard -> Gothitelle's live Teleport Room, whose independent once-per-turn
  Ability has not been consumed.

This is a specific counterexample to any static discardability score or
connector graph that ignores physical zones, action bandwidth, and order.
Choosing two low-opportunity-cost junk cards for Ultra Ball can fail a Bench
objective that succeeds after discarding the seemingly more important Sky
Field. There remains a distinct cost to consuming Sky Field as discard; the
comparison is conditioned on its resulting Teleport use.

Another counterexample is **premature Teleport**: even though a later Ultra
Ball makes Sky Field physically accessible in the discard pile, the source's
once-per-turn Ability was already consumed. Access arrives after the action
deadline.

## Evidence class and scope

This is a verified bounded legal transition witness, with a direct card-text
anchor for Ultra Ball and previous grounding for the Stadium/Bench effects.
The repository CI run is successful.

It is **not** evidence that including Gothitelle or discarding Sky Field is
generally optimal. The state assumes an established Stage 2, two usable
discard resources, a known searchable Basic, an available Ultra Ball and the
absence of relevant locks except in the negative tests. It does not model
draw probability, hidden deck information, evolution setup, Prize cards, or
alternative legal lines using other cards.

The repair from CI run 2 to run 3 added strict zone projection and synchronized
the early-Teleport branch before resolving Ultra Ball. This prevents a
physically removed Collapsed Stadium from remaining incorrectly in the counted
in-play zone.

## Next work

1. Quantify how often discarding a Stadium into a live Teleport channel is
   preferable in real hand distributions and with realistic setup costs.
2. Add multi-copy Stadium choice and other discard-capable connectors, with
   card-specific legality and hand-reservation constraints.
3. Combine the branch with competing needs for Ultra Ball's searched Pokémon
   and alternate uses of the single Teleport Room activation.
