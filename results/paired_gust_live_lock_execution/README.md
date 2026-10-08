# Prime Catcher unlocks a live Stoutland Supporter restriction

## Research question

A timed-gust model can treat Supporter lock as a fixed future denial.
The actual Expanded card Stoutland (`bw7-122`) has the Sentinel Ability,
which prohibits the opponent from playing Supporters from hand only
while Stoutland is **Active**. Does a physically executable gust change
that denial immediately enough to permit a Supporter afterward in the
same turn?

**Yes, conditionally.** Prime Catcher is an Item and can gust another
opponent Bench Pokemon Active first. That sends Stoutland to the Bench
and deactivates Sentinel. A previously blocked Guzma then becomes
playable, provided its own Supporter quota and source cards are still
available.

The result demonstrates a dynamic permission-source feedback loop
rather than assuming lock status remains frozen throughout a turn.

## Integrated implementation

`tools/paired_gust_live_lock_execution.py` combines:

1. `board_derived_continuous_restrictions.active_restrictions_from_boards()`,
   which derives the current opponent restriction sources from physical
   boards, source print IDs, their Active positions, the required
   ability-lock causal snapshot and any temporal attack windows;
2. `paired_gust_source_permissions.execute_permissioned_paired_switch()`,
   which checks print-specific Item/Supporter restrictions, commits
   selected physical Trainer hand-to-discard movement, and performs the
   two-sided physical switch program;
3. `ability_lock_causal_state.advance_lock_state()` and a new
   board-derived restriction query after the two-sided transition.

The returned result preserves both the restrictions **before** the
action and those **after**. A caller can use the resulting lock state
and boards for the next action without keeping stale global booleans.

The source restrictions may have attack-duration windows. Those remain
separate from continuous Pokémon source positions and are passed in
explicitly.

## Real-card line

In the validated fixture:

- Opponent Active is **Stoutland `bw7-122`** with Sentinel active.
- Opponent Bench has one ordinary Pokemon.
- Player has an Active and a Benched Pokemon, one Prime Catcher, and
  two distinct Guzma cards in hand.
- Player has not yet spent the normal Supporter play.
- Both player Pokemon are physically represented with persistent
  object identities.

Then:

1. Playing Guzma directly is rejected by the Stoutland-derived live
   Supporter restriction.
2. Playing Prime Catcher from hand is legal because Sentinel blocks
   Supporters, while Prime is an Item. Prime moves the opponent Bench
   target Active, sending Stoutland to the Bench, and switches the
   player's Active with their own Bench.
3. Recomputing continuous restrictions on the new boards shows that
   the Stoutland restriction has disappeared. The first Guzma remains
   in hand; Prime is in discard.
4. Playing Guzma from hand is now legal. It gusts Benched Stoutland
   back Active and switches the player's Active back.
5. Sentinel immediately becomes active again. The player already
   used their normal Supporter quota. Even if that quota were raised
   to two, a **second distinct in-hand Guzma** is blocked by
   reactivated Sentinel.

This is a closed physical turn-level permission cycle:

`Supporter locked -> Prime Item gust -> Supporter unlocked -> Guzma
Supporter gust -> Supporter locked`.

The supported claim is mechanical reachability of that sequence,
with source card and attached-card conservation. Its strategic value
depends on how Guzma is used and which attacks and board endpoints
matter. An optimal player would not usually restore an adversarial
Supporter lock without a compelling target or Prize reason.

## Counterfactuals

**Passive Vileplume Item lock:** If opponent Bench also contains
Vileplume `xy7-3` with Irritating Pollen enabled, the opponent can
apply Item lock and Active Stoutland Supporter lock simultaneously.
Prime cannot initiate the unlocking line. Guzma is already denied by
Sentinel.

**No opposing Bench:** Even though Prime is an Item, it has no
opposing Benched Pokemon to switch in. Its targeted first step cannot
execute, so it cannot remove Stoutland from Active. The Supporter
lock persists.

These branches capture why a single abstract global lock bit fails
to describe the board-dependent set of responses.

## Validation and provenance

`results/paired_gust_live_lock_execution/reproduce.py` uses the real
bundled Expanded English card print metadata and activation profile
compiler for Stoutland and Vileplume. The active restrictions are
calculated from the board, with source print IDs and up-to-date causal
Ability-lock state, before and after each action.

The regression checks:

- initial Guzma denial;
- Prime Item authorization and both own/opponent switches;
- exact hand-to-discard movement of source instances;
- deactivation and reactivation of Sentinel as the physical Active
  changes;
- ordinary Supporter quota consumption;
- denial of a second physical Guzma copy despite artificially raised
  quota when Sentinel returns;
- joint Stoutland plus Vileplume lock;
- empty opponent Bench blocking the unlock.

Reproduce with:

`python -m results.paired_gust_live_lock_execution.reproduce`

## Important bounds

The implementation assumes all relevant Ability activation effects
are represented by the existing source-scoped restriction compiler
and causal Ability-lock state. Only current action permissions are
derived; exact Pokemon attacks, prize values, and opponents' tactical
replies are outside this test. A real Stoutland lock could also be
broken by attacking, changing abilities, or other switching cards.

The example is a concrete legal action-sequence witness in the stated
board context. It does not claim that the particular action order
is always strategically profitable.
