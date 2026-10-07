# Simultaneous Knock Out conservation

## Question

How should a state engine conserve physical cards when several Pokémon are
Knocked Out at the same time, especially when the Active and a possible
promotion target are both in the Knock Out batch?

Implementation: `tools/simultaneous_knockout_conservation.py`  
Regression: `results/simultaneous_knockout_conservation/reproduce.py`

## Rule-derived phase boundary

The Advanced Player's Rulebook resolves Knock Outs in phases. Effects activated
by those Knock Outs are applied before the Knocked Out Pokémon are discarded.
After those effects resolve, every Pokémon whose remaining HP is zero is
discarded with all attached cards. Promotion occurs afterward when needed.

That ordering makes a one-at-a-time `remove -> promote -> remove` model unsafe.

## Representation

The adapter introduces `PendingKnockOutBatch`.

Preparing a batch does not mutate the physical state. All Pokémon in the batch,
their evolution stacks, and their attachments remain present, which gives a
later trigger layer a stable pre-discard snapshot.

`discard_pending_knock_out_batch()` then performs one atomic disposal boundary:

- all stack cards in the batch leave `in_play`;
- all attachments in the batch leave `attached`;
- those physical instances enter discard and dematerialize into exchangeable
  discard counts;
- promotion, if necessary, must choose a Pokémon that survives the entire batch.

## Regression

The test constructs:

- Active `a`: Bulbasaur -> Ivysaur with Double Colorless Energy;
- Benched `b`: Bidoof with Muscle Band;
- Benched `c`: Squirtle.

Pokémon `a` and `b` are prepared as one simultaneous Knock Out batch.

Before disposal, the pending state still contains both Knocked Out objects, both
Evolution cards on `a`, and the Tool on `b`.

Attempting to promote `b` is rejected because `b` belongs to the same
Knock Out batch. Promoting surviving `c` succeeds.

After the batch disposal:

- Bulbasaur, Ivysaur, Bidoof, Double Colorless Energy, and Muscle Band each have
  one exchangeable discard-pile copy;
- Squirtle remains the only materialized card and is bound to the promoted
  Pokémon object;
- every card-class total is unchanged.

A later terminal batch disposes Squirtle and leaves no board-bound instances.

## Finding

Simultaneous Knock Out is a batch state transition with a trigger window, not a
sequence of independent single-Pokémon deletions.

Sequential processing can create an impossible promotion by temporarily
promoting a Benched Pokémon that should be discarded in the same batch. The
batch representation prevents that by deriving promotion eligibility only after
the complete Knock Out set is known.

## Limits

The adapter provides the pre-discard trigger window but does not execute
card-specific Knock Out triggers itself.

It also does not yet model:

- both players' boards in one batch;
- the rulebook's ordering choice when both Active Pokémon are Knocked Out;
- Prize-card taking after disposal;
- replacement effects that redirect a Knocked Out card or attachment;
- win/loss resolution.

Those are downstream phases and can be layered onto the same pending-batch
boundary.
