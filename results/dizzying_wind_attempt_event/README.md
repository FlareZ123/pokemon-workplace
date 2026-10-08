# Venomoth's failed Trainer gate preserves ordinary Supporter quota

## Sources and mechanics

Venomoth from Phantom Forces (`xy4-2`) has *Dizzying Wind*, an attack that requires the opponent to flip a coin upon playing a Trainer from hand on the following turn. On tails, that Trainer has no effect and is still discarded.

The [official Japanese Pokémon Card Q&A](https://www.pokemon-card.com/rules/faq/search.php?freeword=%E3%83%A2%E3%83%AB%E3%83%95%E3%82%A9%E3%83%B3&page=2&regulation=all&regulation_faq_main_item1=all) explicitly resolves three important cases:

- If Professor Sycamore is suppressed by tails, the card is discarded and **another Supporter can be used** that turn, with another Dizzying Wind coin flip.
- When two Poké Drawer+ Item cards are played simultaneously, **only one Dizzying Wind coin flip** is required.
- For Ultra Ball, the Dizzying Wind coin is flipped **before Ultra Ball's discard-two payment**.

These rulings separate source-card movement, pre-use prevention, successful card effects, and normal turn quotas.

## Implementation

The existing [trainer_play_attempt_budget](../trainer_play_attempt_budget/) had already formalized a closely related coin gate from Seismitoad's new Quaking Fist. This work reuses that two-phase physical transition because the official Venomoth Supporter retry ruling agrees with its accepted/failure Supporter mechanics.

`tools/dizzying_wind_attempt_event.py` wraps that producer for the **Supporter-specific Venomoth outcome**. On heads, it emits the existing `CommittedPlayEvent`, consumes one ordinary Supporter use, and leaves a successful-use record. On tails, it sends the card to discard while retaining the Supporter quota, and emits a distinct `FailedTrainerAttempt` with the attempted card's physical identity.

`CausalEventJournal` now stores these failed attempts separately from its committed uses. Its `queried_play` is a query over **successful, resolved plays**, so failed Professor Sycamore does not count even though its physical card left hand for discard. Previously recorded successful Item source batches remain unaffected.

## Regression

The test constructs an exact two-card Supporter hand and resolves:

1. Professor Sycamore attempted under Dizzying Wind, flips tails, goes to discard and spends zero Supporter quota.
2. Colress is subsequently attempted, flips heads, goes to discard and consumes exactly one Supporter use.

It checks that the physical discard contains both cards, the journal has one committed Supporter and one separately recorded failed attempt, and a Supporter-play-history query recognizes Colress while excluding Sycamore.

Negative tests reject forged failed-attempt witnesses, duplicate classifications, and attempts to reuse already discarded cards.

Reproduce: `python results/dizzying_wind_attempt_event/reproduce.py`.

## Simultaneous two-card Items

The official Q&A directly covers **Poké Drawer+**, which is an older simultaneous two-card Item. Cross Switcher's present-day text also requires two copies played together for one effect. These structures support a strong **analogy** that Dizzying Wind checks a single simultaneous Cross Switcher action once. I did not find a ruling directly naming Cross Switcher, so the bridge does not silently promote this transfer inference into verified card-specific execution semantics.

The failed-Supporter model above is directly supported by the Venomoth ruling. A general gate for all Trainer kinds and multi-source Item actions remains a separate integration task.
