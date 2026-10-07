# Atomic Trainer search with hidden-state information

## Question

Can one Trainer search transition simultaneously enforce ordinary play legality, exact discard payment, typed target choice, K1 Prize inference, public target signaling, exact target movement, shuffle state, and observer-relative hidden information?

For a one-target revealed search, yes.

Implementation: `tools/trainer_search_hidden_state_bridge.py`

Regression: `results/trainer_search_hidden_state_bridge/reproduce.py`

## Concrete card witness

The bundled `swsh1-179` Quick Ball record is an Item whose local card text requires discarding another card from hand, searches the deck for a Basic Pokémon, reveals it, puts it into hand, and then shuffles.

The repository's legality baseline warns that database legality fields are not universally authoritative. Quick Ball is outside the identified missing-ban and tournament-exclusion corrections, and its card record itself marks Expanded legal. This result uses Quick Ball primarily as a concrete revealed single-target search pattern.

The regression now obtains Quick Ball directly from `single_output_search_profile_compiler.py`.

For `swsh1-179`, that compiler supplies:

- action class: Item;
- one Basic Pokémon search output;
- one-card discard requirement;
- the printed play condition retained as metadata and supplied to the transaction as satisfied.

## Composition

The bridge composes existing repository layers instead of reimplementing them.

`execute_trainer_search_transaction()` remains responsible for:

- Item or Supporter play permission;
- the turn-action budget;
- the exact discard witness;
- typed target legality;
- the resolving-Trainer zone;
- aggregate deck-to-hand target movement.

The hidden-state adapter is responsible for:

- deriving the actor's exact grouped Prize composition from physical truth;
- deriving the current deck-plus-Prize pool;
- conditioning other observers on the publicly revealed target policy;
- materializing the publicly known searched copy in hand;
- materializing one exact post-shuffle top branch;
- checking card-class conservation;
- requiring every observer posterior to retain positive support on exact truth.

The bridge currently requires deck and hand copies to be exchangeable before the search. Existing materialized Prize and board instances are allowed.

## Exact Quick Ball regression

The physical hidden pool contains:

- A in Prize;
- one filler in Prize;
- X Basic in deck;
- Y Basic in deck;
- two fillers in deck.

The player's hand also contains:

- Quick Ball;
- one discardable fodder card.

The typed target allocator exposes X and Y as Basic Pokémon and commits to X.

The exact transaction performs these mechanical moves:

- Quick Ball: hand -> resolving -> discard;
- fodder: hand -> discard;
- X: deck -> hand, then materialized as the publicly known searched instance;
- one exact Y branch: deck -> deck_top after shuffle.

The same synthetic target-selection policy from `deck_search_target_signal` is used. In the exact world A is Prized, so the actor's K1 state favors the X line.

## Information result

After target X is publicly revealed:

- actor P(post-shuffle top=Y) = 1/3;
- opponent P(post-shuffle top=Y) = 1/7.

Both beliefs retain positive support on the exact world:

- top=Y;
- Prizes=(A, filler);
- searched X in hand.

The numerical gap comes from information, while the physical transition is identical for both observers.

## Mechanical gates

The regression verifies:

- exact discard cost = 1;
- Quick Ball enters discard;
- the selected fodder enters discard;
- the searched X instance is in hand;
- the sampled Y instance is in `deck_top`;
- Item play does not consume the Supporter budget;
- per-card-class totals are conserved.

It then reruns the same action with `item_play=False`. The existing Trainer transaction rejects the action, so the hidden-state bridge cannot bypass Item lock.

## Strategic interpretation

This is a small end-to-end example of the repository's broader modeling direction.

A search connector has several simultaneous consequences:

- it consumes a playable action and possibly a discard resource;
- it selects an exact physical target;
- the deck inspection changes the acting player's hidden information;
- the public reveal can change the opponent's information;
- the shuffle changes future draw uncertainty.

Representing only "Quick Ball reaches X" loses all of those additional state transitions.

## Limits

The current bridge handles one revealed target. Multi-target searches need a public observation model over target sets or ordered reveal tuples.

The bridge materializes the searched target after the aggregate transaction has moved one exchangeable copy into hand. This is valid while copies of that class had no prior copy-specific history. A future hand-knowledge model may need richer identity and observer visibility for already-materialized hand cards.

The Quick Ball profile is derived from the separate conservative single-output revealed-search compiler. That compiler intentionally covers only a narrow literal family.

The synthetic X/Y target-selection policy is a controlled information witness rather than a claim about optimal Quick Ball play.

## Next work

Two directions are now especially useful.

The next major extension is to connect the target-selection policy to an actual line evaluator. That would let an opponent infer hidden Prize information from a policy generated by utility, AMR, connector contention, and board state rather than from a hand-written toy policy.

The single-output compiler can also expand through separately validated wording families such as deterministic multi-unit search and disjunctive target selectors.
