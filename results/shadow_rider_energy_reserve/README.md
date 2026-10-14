# Aichi champion: Mysterious Treasure payment versus next-turn Psychic Energy

## Strategic question

Yasunori Kato's 2026 Aichi champion Shadow Rider Calyrex VMAX deck contains four Mysterious Treasure, 11 Basic Psychic Energy and four Shadow Rider VMAX. Mysterious Treasure's one-card discard can fetch the singleton Dragon-type Radiant Eternatus, whose Climactic Gate can immediately put two VMAX from the deck onto the Bench and then end the turn.

Shadow Rider VMAX's Underworld Door requires a Psychic Energy **still in hand** on a subsequent turn in order to attach it to a Benched Psychic Pokémon and draw two cards. A first-turn Treasure discarded Energy can consume the only retained copy in hand.

Previous exact research estimated **24.843972%** of Basic-valid going-second starts in which the Treasure -> Radiant -> two-VMAX route exists and one held Psychic Energy can pay its cost, but did not require another Energy to survive payment. This experiment quantifies that next-turn resource reservation.

## Source and method

The same exact published English-print 60-card baseline, restricted Radiant entry route, accepted Basic seven-card opener, six physical hidden Prizes, and first natural draw going second are retained from the earlier Treasure payability study. The exact source has 11 Psychic Energy within the prior 37-card "other" category.

For each physically possible opener/Prize/draw world that has a two-VMAX Treasure route, condition on its count h of visible "other" cards. The number X of held Psychic Energy within those cards has the exact hypergeometric distribution

P(X = x | h) = C(11,x) C(26,h-x) / C(37,h).

Two deliberately restricted discard policies are compared:

- **Spend one Psychic Energy:** reserve m Psychic cards after the payment only if X is at least m+1.
- **Spend Psychic or a spare Mysterious Treasure:** if at least two Treasure copies are held, one can pay for the other and preserve the Psychic cards; otherwise require m+1 Psychic as before.

This is an exact physical-card count event; the payment decision uses visible counts and does not need to know the hidden Prize cards.

## Exact probability frontier

All entries are probabilities among **Basic-valid opening sevens**, with six Prizes and one going-second natural draw. The underlying route also requires an eligible non-Radiant starting Active and two searchable VMAX.

| Basic Psychic Energy cards retained in hand after payment | Pay Energy only | Pay Energy or spare Treasure |
| ---: | ---: | ---: |
| At least 0 (original payment gate) | 24.843972% | 26.390182% |
| **At least 1** | **12.119811%** | **14.526379%** |
| At least 2 | 3.337460% | 4.670632% |
| At least 3 | 0.487134% | 0.812578% |

Under the Energy-only payment policy, demanding one additional held Psychic card reduces the modeled route mass by **12.724161 percentage points**. Only **48.783708%** of the original Energy-payable Treasure route states contain an additional Psychic Energy after payment.

Allowing a spare Treasure to pay the first Treasure's cost increases the at-least-one-retained-Energy endpoint by **2.406568 percentage points**, from 12.119811% to 14.526379%. The spare Treasure is a real physical second copy already in hand, not a hypothetical free discard.

## Competitive interpretation

The distinction matters for continuation planning: an early VMAX launch is more useful when the player's later Energy acceleration remains available. A search card that enables the first-turn Bench can simultaneously reduce the hand's ability to activate Underworld Door. In some opening hands, discarding a redundant Treasure instead of an Energy preserves a later acceleration opportunity.

A retained Psychic in hand is a **resource precondition**, not a demonstrated turn-two Underworld Door activation. The opponent could disrupt the hand or disable Abilities, the board may not have a legal target, and the next-turn draw or another search can alter the available resources. This model omits manual Energy attachments, later searches, the actual opponent, other Treasure discard targets, full-game policy, and Prize-taking or match results.

Consequently, these are constrained first-turn access-and-retention probabilities. They are no claim that Energy should always be retained or that a particular deck substitution raises win rate.

## Validation

tools/shadow_rider_energy_reserve.py computes the frontier in exact rational arithmetic using the earlier source-checked six-group physical-state enumerator. The zero-retention row exactly reproduces both baseline Energy-payment probabilities from tools/shadow_rider_treasure_cost_sensitivity.py.

The independent physical-card oracle labels every card in an eleven-card toy pool, explicitly distinguishes two Psychic filler copies, and enumerates 18,312 Basic-valid chronological opener/Prize/draw worlds. All six retained-Energy tests (three thresholds times two payment policies) agree exactly with the hypergeometric calculation.

Run results/shadow_rider_energy_reserve/reproduce.py, or manually dispatch the Windows workflow .github/workflows/validate-shadow-rider-energy-reserve.yml.
