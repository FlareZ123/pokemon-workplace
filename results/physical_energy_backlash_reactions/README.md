# Conserved physical Energy backlash from Abilities and Tools

## Question

Can the copied-attack post-damage reaction phase execute effects which remove
or relocate the **Attacking Pokémon's attached Energy**, while preserving the
physical Energy card instance and its correct owner, even when the defending
source Pokémon is Knocked Out?

The narrow source-backed adapter is
`tools/physical_energy_backlash_reactions.py`, with reproduction in
`results/physical_energy_backlash_reactions/reproduce.py`.

## Four source-card families

| Source print | Triggering text body | Physical effect |
| --- | --- | --- |
| Turtonator `me3-17`, Shell Spikes | discard an Energy from the Attacking Pokémon | selected Energy into its owner's discard pile |
| Klawf ex `sv3-120`, Counterattacking Pincer | discard an Energy from the Attacking Pokémon | same |
| Rugged Helmet `swsh6-152` / `swsh6-228` | put an Energy attached to the Attacking Pokémon into your opponent's hand | selected Energy into its owner's hand |
| Handheld Fan `sv6-150` | move an Energy from the Attacking Pokémon to one of your opponent's Benched Pokémon | selected Basic Energy retains its physical ID, with its `attached_to` binding transferred |

The compiler accepts the actual damage record and current source print.
For Abilities, it confirms the live Pokémon name, source location,
opponent-origin attack, positive final damage, and an enabled Ability
(supplied by the upstream lock engine). For Tools, it also requires the
physically attached Tool instance to match the printed source and its
Tool-effect flag to be enabled. The complete set legality and
card-specific banned overlay are checked.

In all supported cases the original Attacking Pokémon's physical ID is
used. A subsequent switch in the attack text cannot redirect the Energy
effect onto the replacement Active Pokémon.

## Test witness and conservation

A Haughty Order copy of Timeless-GX deals 150 damage to a 120-HP
Turtonator with Shell Spikes. Even though Turtonator will be Knocked Out,
its Ability is resolved before the physical disposal window: one chosen
Fire Energy leaves the attacker's original Pokémon for the owner's discard.
A second Water Energy remains physically attached. All card-class totals
are conserved.

With Rugged Helmet, the same physical Energy goes to the attacker's hand,
and the Tool itself stays attached to the defending Pokémon through its
Knock Out-trigger window. With Handheld Fan, the chosen Basic Fire Energy
is moved to a specified Benched Pokémon with the **same card instance ID**;
the attacker retains its other attached Energy.

The tests additionally cover Ability lock, Tool-effect suppression
(Jamming Tower-like), alternate-art Rugged Helmet print, missing Energy,
missing destination Bench, illegal destination choice, and reaction
attribution to a switched attacking Pokémon.

## Strategic implications

A source card that survives through the post-damage reaction window can
reduce or redirect a future attacker's Energy state even if the defender
is about to leave play. This makes “I can Knock Out the source” insufficient
for evaluating the attack's post-KO resource consequences. The attacker
must also consider the opposing player's selection of attached Energy
and destination Bench.

## Boundaries

- A legal source and target condition must already be provided or derived
  from current physical state. Ability suppression remains a caller fact.
- Handheld Fan currently moves **Basic Energy** only. Special Energy may
  have destination-specific attachment restrictions, which require a
  stronger receiver-binding model; attempting unsupported Special Energy
  movement is rejected.
- The model does not infer whether a chosen Energy is strategically
  disposable, automatically optimize the owner's target choice, or
  recompute HP from continuous attached-Energy-dependent Abilities
  after changing Energy state. It handles the physical attachment/zone
  transition exactly for the supported cases.
- All effects are resolved before Pokémon are physically discarded for
  Knock Out. The Prize, promotional, and terminal turn phases are
  modeled by downstream components.
