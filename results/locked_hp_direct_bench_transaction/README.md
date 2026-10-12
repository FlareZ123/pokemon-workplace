# Poffin HP-limited direct-Bench Item under source-scoped play locks

## Question

Can a card-grounded 70-HP search and its physically conserved Bench placement
be rejected before Item play when an opponent's lock prevents that hand
action, while permitting Poffin under an unrelated restriction?

**Yes.** The wrapper composes three already validated semantic layers:

1. source-scoped permission projection for a concrete Item played from hand;
2. exact legal print and printed-HP authentication of every search candidate;
3. existing atomic direct-Bench Trainer lifecycle with a conserved identity ledger.

Implementation: `tools/locked_hp_direct_bench_transaction.py`  
SFT regression: `results/locked_hp_direct_bench_transaction/reproduce.py`  
[Green CI run 38240763350](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38240763350)

## Exact restriction outcomes

The deterministic witness uses Buddy-Buddy Poffin `sv5-144`, a 60-HP
Elgyem `sm11-90` in deck, and two initially occupied Bench slots.

| Active source-scoped restriction on the player | Result of attempting Poffin |
| --- | --- |
| None | Allowed |
| Spiritomb `bw11-87`, ACE SPEC-only Sealing Scream | Allowed: Poffin is an ordinary Item |
| Vileplume `xy7-3`, Irritating Pollen Item lock | Prohibited |
| Umbreon & Darkrai-GX `sm11-125`, Dark Moon-GX Trainer lock | Prohibited |
| Spiritomb plus Vileplume | Prohibited |

The regression obtains actual compiled restrictions from the bundled legal
card-text database and confirms that Poffin's action metadata has Item kind
without the ACE SPEC tag.

The exact restriction collection is supplied as an already-active, correctly
player-targeted set. The wrapper checks the attempted **hand-origin** action,
so it preserves the separate semantic rule that Item play from another
zone need not be blocked by a hand-only restriction.

## Physical invariant

An allowed Poffin moves from hand to discard, with the Elgyem card moved
from deck into an in-play Bench object. Card totals and the Item turn budget
are conserved by the established transaction.

A prohibited attempt raises before card movement. The original immutable
state retains Poffin in hand and Elgyem in deck. The base
`PlayerChannels` are unchanged by a successful action, because active lock
projection is ephemeral and recomputed for each attempt.

The direct-Bench full-capacity refusal also remains enforced.

## Strategic consequence

Potential search connectivity is insufficient when active lock restrictions
remove the hand Item edge. Poffin remains usable under a restriction that
selectively prevents ACE SPEC play, but an actual Item lock removes it even
with fully eligible targets and vacant Bench slots.

This is a critical distinction for matchup-oriented setup evaluation,
including early Item-lock and Trainer-lock archetypes. The result is a
tested rules/transaction boundary; it does not quantify matchup prevalence
or competitive game outcomes.

## Limits and next steps

The wrapper accepts already-active restrictions and does not itself evaluate
whether Vileplume, Spiritomb, or an attack-applied lock is currently live.
Position, Ability suppression, temporal effect expiry, and owner/target scope
belong to the upstream source-activation layer. It also does not resolve
deck shuffle/K1 observation: use the HP-bounded hidden direct-Bench bridge
for that dimension. A future all-in-one adapter can join these two wrappers
without duplicating physical card movement.

The test has one successful searched target. The underlying Poffin HP adapter
also has a separately validated two-target Bench transaction.
