# Retreat overpayment creates strategically distinct resource futures

## Question

If an Active Pokémon has sufficient Energy to Retreat by discarding a
single Double Colorless Energy, can a planner discard that option's
nonminimal physical-card supersets without losing strategically
meaningful game states?

## Rules basis

The official Japanese Pokémon card Q&A for Dashing Pouch directly
permits a Pokémon with Retreat Cost 2 and two attached Double Colorless
Energy cards to discard both copies for Retreat. Both copies then
return to hand under Dashing Pouch. Thus a rule that discards only an
inclusion-minimal sufficient subset would incorrectly reject a
documented legal case. This official ruling is also recorded in
[retreat_energy_payment_semantics](../retreat_energy_payment_semantics/).

Official ruling search:
https://www.pokemon-card.com/rules/faq/search.php?freeword=%E3%83%80%E3%83%83%E3%82%B7%E3%83%A5%E3%83%9D%E3%83%BC%E3%83%81

## Exact conserved scenario

The Active Stage 1 Pokémon has Retreat Cost 2, one Double Colorless
Energy (DCE), one Basic Psychic Energy, and Dashing Pouch
`sm4-92`. It has one damage counter. Its Bench contains one Pivot.

The board-derived legal-action generator produces **two different
physical payment witnesses**:

| Payment | Returned to hand | Still attached to outgoing Pokémon |
| --- | --- | --- |
| DCE only | DCE | Basic Psychic Energy |
| DCE + Basic | DCE and Basic Psychic Energy | None |

Both Retreats are legal. The larger payment spends two Energy cards
for a Retreat Cost of two, supplying three Energy units, and Dashing
Pouch redirects the discarded cards to hand.

The outcomes have opposing resource implications. Retaining the Basic
Energy on the previous attacker can preserve future attack readiness
after it returns to the Active Spot. Returning that same Basic Energy
to hand can instead support a different Pokémon's upcoming Energy
attachment or other hand-based actions. Neither branch universally
dominates the other without the continuation plan.

The two branches are confirmed to preserve physical Energy copy
totals and consume precisely one Retreat action.

## Counterplay and source interactions

An enabled opposing Mr. Mime `sm9-66` with Scoop-Up Block, while the
holder is damaged, prevents Dashing Pouch returning the selected
Energy to hand. The exact same two payment choices then send the
selected cards to discard; the Basic Energy remains attached only
in the smaller-payment branch.

Jamming Tower `sv6-153` also disables Dashing Pouch. The paid Energy
then goes to discard without Scoop-Up Block. The Tool remains attached
and retains its baseline effect flag in the physical successor,
allowing the effect to be rederived if the Stadium later leaves play.

These are mechanically distinct action outcomes. A policy optimizer
should evaluate them using current and future board needs rather than
choosing automatically by the number of cards discarded.

## Reproduction

`results/retreat_resource_allocation_frontier/reproduce.py` constructs
the exact physical attachments and checks every committed Retreat
transition, destination record, attached-card remainder, zone
conservation, and Retreat quota. It compares unblocked Dashing Pouch,
opposing Scoop-Up Block, and Jamming Tower.

The validation workflow
[37840584350](https://github.com/FlareZ123/pokemon-workplace/actions/runs/37840584350)
passed the reproducer and the preexisting Retreat payment, destination,
and action enumeration regressions.

## Modeling consequences and limits

The older `tools/typed_retreat_gust.py` toy minimax enumerates only
inclusion-minimal Energy payments. That is an explicit approximation
for its bounded endgame model. It may collapse multiple legal physical
payment branches whose downstream resources differ. The newer
`tools/retreat_action_enumerator.py` preserves the branches by executing
each exact physical selection.

No win-rate or empirical metagame claim follows from this case.
Hand usability, deck composition, Energy attachment quota, Item locks,
and opponent response affect the strategic ranking. The example
establishes a concrete non-domination mechanism and a verified
successor-state distinction, not the optimal selection in a real match.
