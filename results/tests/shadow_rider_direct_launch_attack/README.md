# Full Aichi champion: direct Radiant VMAX launch to next-turn Max Geist

This is a **deck-specific, exact but restricted** paper Expanded opening/attack calculation. The source 60 is the [published 2026 Aichi champion Shadow Rider Calyrex list](../../decks/shadow-rider-calyrex/), previously print-checked in this repository. It has 1 Radiant Eternatus, 13 other Basic Pokémon, 4 Shadow Rider Calyrex VMAX, 11 Psychic Energy, 1 Float Stone, and 30 other cards.

## Precisely defined line

Start with an accepted Basic-containing opening seven. Select a non-Radiant Basic as Active, so Radiant Eternatus can be played from hand onto the Bench. Draw one natural card on the first turn going second, set six Prizes before that draw, and require Radiant in hand by this point **without search**. Its Climactic Gate must find at least two VMAX still in deck, put them both on Bench, shuffle and end the turn. Allow an uninterrupted opponent turn and one next-turn natural draw. Use two live Underworld Door Abilities to attach Psychic Energy to the same initially uncharged Benched VMAX and draw two cards per successful Ability; use one manual hand attachment last. Require enough attached Energy to use Max Geist. Pivoting the charged VMAX to Active is an additional gate.

The method separately evaluates a **Float Stone-only pivot route**: one physical copy starts in hand or is found through the natural/Ability draws, the Basic Active has a free Tool slot, playing Tools is legal, and Float Stone's no-Retreat-Cost effect permits promotion. Other routes via Latias ex, Guzma, switching, search or retreat Energy are not counted. No Ability lock or opponent disruption is modeled.

### Exact probabilities, conditional on an accepted starting hand

| Milestone | Normal Max Geist (3 Energy) | Reduced-cost Max Geist (2 Energy) |
| --- | ---: | ---: |
| Direct hand/draw Radiant launch of 2 VMAX | 12.017840120% | 12.017840120% |
| Launch followed by enough next-turn attack Energy | **4.455846832%** | **6.978303011%** |
| Launch + enough Energy + accessible Float Stone | **0.768862128%** | **1.288246138%** |

These are unconditional with respect to the defined accepted-opening/Prize/draw sample, and conditional on the declared structural/action assumptions. The two-Energy column requires **Dimension Valley** to be in play; its availability and Stadium-replacement cost are **not sampled**. The normal three-Energy column does not assume a cost-reduction effect. The first line exactly matches the earlier independently computed [direct Radiant launch baseline](../../shadow_rider_radiant_launch/) of 12.017840120%, providing a useful cross-check.

For normal three-Energy Max Geist, conditional on already achieving this direct double-VMAX launch, the model gives **37.076936%** Energy readiness and **6.397673%** readiness with this particular Float Stone pivot. These ratios are within the restricted continuation only.

## Exact method and tests

The script at [tools/shadow_rider_direct_launch_attack.py](../../../tools/shadow_rider_direct_launch_attack.py) groups the actual 60 into six print-grounded classes, enumerates opening seven and six Prizes by exact multivariate combinatorial multiplicity, handles the first draw and two VMAX removed from deck by Climactic Gate, then enumerates the next natural draw. Each resulting hand/deck Psychic and Float Stone count is fed into the existing exact [post-launch Energy/pivot kernel](../shadow_rider_post_launch_energy/README.md). Full probabilities are rational fractions; there is no Monte Carlo approximation. The default state enumeration collapses to 148 distinct residual hand/deck resource configurations.

The [reproducer](reproduce.py) checks the four key exact fractions and deck print counts. Its **independent labeled physical-card oracle** enumerates opening, Prize and two natural draw choices and every remaining small-deck order, resolving individual Ability draw windows and attachment actions for four smaller toy deck populations and both attack costs. All tests passed offline on 12 October 2026. No CI result or full-game match result is claimed.

## What these numbers do not prove

The first-turn hand/draw branch omits the deck's many strong search connectors and may substantially undercount reachable Radiant launches. The exact route model does not include early hand manipulation, the already-available Energy attachment on other Pokémon, prize rescue, opponent's intervening turn, possible first-turn Ability lock, the actual source and cost of a pivot, Supporter action contention, Sky Field versus Dimension Valley conflict, attack damage/KO breakpoints or any modeled match win rate. The conditional two-Energy scenario is a cost-reduction counterfactual pending exact Dimension Valley access modeling, and should never be reported as an unconditional two-Energy launch-and-attack chance.

Next best work: compose richer source-aware launch routes (Mysterious Treasure, Quick Ball, Heavy Ball, Forest Seal Stone), keeping the actual Psychic Energy spent to pay discards and the availability of Latias/Float/retreat routes. Test whether early energy payoff survives Bench-space contraction and actual opponent attacks.
