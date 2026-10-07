# Source-scoped Trainer transaction gating

## Question

The existing Trainer search transaction executor gates Items and Supporters through `PlayerChannels`. The source-scoped restriction work adds selectors that can depend on exact print identity and richer card semantics.

This result places the new permission model in front of a real transaction boundary while preserving the established executor.

Implementation:

- `tools/card_action_metadata.py`
- `tools/source_scoped_trainer_transaction.py`

Regression: `results/source_scoped_trainer_transaction/reproduce.py`

CI: `.github/workflows/validate-source-scoped-action-permissions.yml`

## Exact action metadata

The action metadata index derives the fields needed by restriction selectors from exact legal prints:

- action kind;
- ACE SPEC status;
- whether a Pokémon has an Ability;
- Team Rocket's Pokémon membership.

It also recognizes historical `Pokémon Tool F` subtypes as Tool actions.

The current bundled legal snapshot yields **14,827 classified exact prints**. Two records are deliberately left unclassified because their stored Trainer supertype conflicts with incomplete or Pokémon-like subtype metadata: `me55c-18` Misty and `me55c-69` Erika's Jigglypuff. A transaction that requires metadata for an unclassified print therefore fails at lookup instead of receiving an invented action kind.

## Transaction adapter

`execute_source_scoped_trainer_search_transaction` and its retrieval-first counterpart perform four permission steps before delegating to the established transaction executor:

1. verify that exact action metadata belongs to the compiled Trainer print;
2. project exactly representable active restrictions into temporary `PlayerChannels`;
3. evaluate any residual typed restriction against the exact hand action;
4. execute the established transaction only after the action is legal.

The projected channels are temporary. The returned transaction restores the caller's base channel state while preserving all zone and turn-budget changes produced by the underlying executor. Active restrictions remain an explicit input to the next action.

This ownership avoids leaving a stale `item_play=False` or `supporter_play=False` inside canonical state after an external lock source disappears.

## Card-grounded regression

The regression uses compiled profiles and exact metadata from the bundled resources.

### Secret Box

Secret Box `sv6-163` is identified as an Item and an ACE SPEC.

With no active restriction, its real three-card discard transaction succeeds and retrieves its four typed outputs.

Vileplume `xy7-3` / Irritating Pollen blocks the hand Item action.

Spiritomb `bw11-87` / Sealing Scream also blocks Secret Box because exact metadata supplies the ACE SPEC tag to the residual selector.

### Arven

Arven executes successfully while Irritating Pollen is the only active restriction, since the action is a Supporter play.

Darkrai & Umbreon-GX `sm11-125` / Dark Moon-GX blocks the same Arven action through its Trainer-wide hand restriction.

The successful Arven transaction still consumes the established Supporter budget.

## Validation

The focused GitHub Actions workflow runs:

- the 106-row source-scoped restriction audit;
- the 94/12 channel-projection regression;
- the Trainer transaction regression.

Workflow run `37583452032` completed successfully against the live shared repository.

## Finding

Source-scoped permission state can sit in front of an established transaction engine without forcing that engine to own every lock semantic.

Exact print metadata supplies card selectors. The projection bridge handles the common scalar cases. Residual predicates preserve the narrow cases. The transaction executor remains responsible for search legality, discard payment, zone movement, and turn-budget consumption.

## Limits

The adapter currently covers the repository's compiled Item and Supporter search transactions. Tool attachment, Stadium play, Pokémon play/evolution, and Energy attachment need equivalent transaction boundaries.

The adapter receives already-active restrictions. Activation geometry, duration, attack-applied effect memory, and Ability suppression are separate upstream concerns.

The exact metadata index intentionally leaves ambiguous database records unclassified. A later errata or card-identity layer can resolve those records if authoritative evidence supports an action class.
