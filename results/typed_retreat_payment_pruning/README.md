# When can a gust minimax safely prune nonminimal Retreat payments?

## Conditional theorem

The existing typed gust endgame simulator can safely restrict defending-player
normal Retreat payments to inclusion-minimal sufficient subsets of attached
physical Energy cards, while preserving its minimax attack-count objective.

This is a conclusion about the restricted mechanics in
tools/typed_retreat_gust.py. The legal Retreat action set is larger,
and exact physical simulators must still retain nonminimal payments.

## Proof

Given any legal payment P, repeatedly remove an included Energy card as
long as the remainder still meets the numeric Retreat Cost. The resulting
inclusion-minimal payment Q is a subset of P. After paying Q, the outgoing
Pokémon retains every physical Energy card it would retain after paying P,
plus possibly some additional Energy.

In this specific game model, attached Energy affects future normal Retreat
availability only. Attacks have fixed hit counts and Prize rewards; attached
Energy never causes a penalty, changes damage, or creates a new opponent
action. Energy discarded for Retreat is permanently removed from play
without a card-triggered bonus or alternative destination. Defender choices
remain optional and the defender maximizes attacks the opponent needs.

Therefore any continuation after P can be matched by one after Q; extra
retained Energy cannot reduce the defending player's continuation choices.
Induction over the finite remaining attack horizon establishes weak dominance.
Restricting to inclusion-minimal payment choices preserves the minimax value.

The argument assumes attached cards always provide positive Energy units,
and uses the physical payment convention that a positive Retreat Cost C
permits selecting no more than C physical Energy cards. A zero Retreat Cost
requires the empty payment.

## Independent finite verification

The new reproduction script constructs a separate full-payment enumerator
and independent memoized minimax, then compares it with the pre-existing
minimal-payment solver.

- All 107 legal full-payment remainders for zero through four attached
  Energy cards (one- or two-unit), with numeric costs from 0 through 4.
  Every full-payment remainder is a submultiset of an inclusion-minimal
  payment remainder.
- 4,608 two-Pokémon instances varying Prize values, hit counts,
  Retreat Costs, attached Energy, gust availability, Switch Item
  availability, and Item-play permission.
- 3,072 three-Pokémon instances with Prize values 2, 3, and 1,
  two-hit durability, costs 1 or 2, four Energy patterns per Pokémon,
  zero to two gusts, and zero or one Switch Item.

**All 7,680 tested minimax values agree exactly.** The bounded computation
supports the proof and checks the software implementation. It is not an
observational estimate of win rate or real-world matchup prevalence.

## Where the theorem stops applying

The board-level mechanism can invalidate payment dominance.
Dashing Pouch is a documented example: a greater legal Retreat payment
can return additional Energy to hand, changing future Energy-attachment
and hand-action availability. The result in
results/retreat_resource_allocation_frontier/ models a concrete witness.

Effects depending on low attached-Energy counts, changed attack damage,
or alternative destinations likewise fall outside this monotone model.
The full mechanics action enumerator in tools/retreat_action_enumerator.py
therefore correctly preserves all legal payment witnesses.

The distinction is **objective-preserving game-tree pruning** versus
**complete physical-action enumeration**.

## Evidence and reproduction

Bundled Advanced Player's Rulebook sections A-03, C-01, and C-03 cover
Retreat payment, discard, and switching. Existing
results/retreat_energy_payment_semantics/ documents the official Dashing
Pouch ruling allowing multi-card overpayment.

Run: python results/typed_retreat_payment_pruning/reproduce.py
