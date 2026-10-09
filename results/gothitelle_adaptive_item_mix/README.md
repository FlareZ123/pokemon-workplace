# Adaptive Quick Ball, Nest Ball and Battle VIP Pass in one deck

## Why this experiment

The earlier two-turn Gothitelle studies compared one extra Nest Ball search
against one Battle VIP Pass. A real first turn may contain multiple copies
of both Item families. Their conditional success events overlap, and the
combination can also unlock states where neither family is sufficient alone.

This calculation evaluates **one fixed illustrative 60-card population**.
The game-level premise is inherited from
[`gothitelle_teleport_two_turn_bridge`](../gothitelle_teleport_two_turn_bridge/):
Quick Ball discards Sky Field on turn one, Gothita must be established alongside
four other ordinary Basics by the end of that turn (one ordinary Active, three
other ordinary Bench occupants, Gothita on the fourth Bench slot), and turn-two
Rare Candy + Gothitelle completes the setup. Six random Prizes, opening seven,
and one natural draw on each personal turn are represented exactly.

### Card access and action budget

The disjoint 60-card partition is G3 Gothita, T2 Gothitelle, C4 Rare Candy,
O8 other Basics, Q4 Quick Ball, S2 Sky Field, N4 Nest Ball, V4 Battle VIP Pass,
and 29 filler.

Quick Ball consumes Sky Field and searches at most one unprized Basic into
hand, which may be Benched. Each Nest Ball available on the first turn
can put one unprized Basic directly onto the Bench. Each Battle VIP Pass
available on that first turn can put up to two unprized Basics directly
onto the Bench. The search budget is thus `1 + N_seen + 2*V_seen`, capped
in use by the number of required missing Basics and open Bench slots.
Search and Prize-card access are modeled jointly. VIP Pass is played only
during its printed first-turn window.

- Exact model: [`tools/gothitelle_adaptive_item_mix.py`](../../tools/gothitelle_adaptive_item_mix.py)
- Independent physical-copy SFT: [`reproduce.py`](reproduce.py)
- Prior comparisons: [Nest](../gothitelle_quick_nest_joint_board/) and
  [VIP](../gothitelle_quick_vip_joint_board/)

## Same-deck exact results

| Eligible first-turn Items | P(setup access) per seven-card opening attempt |
| --- | ---: |
| Quick only | 0.001573353% |
| Quick + all seen Nest Balls | 0.007152285% |
| Quick + all seen Battle VIP Passes | 0.045206616% |
| **Quick + Nest + VIP adaptive** | **0.066523496%** |

The new model permits multiple Nest Balls and multiple VIP Passes where
naturally accessible. The single-family success probabilities therefore
exceed the earlier one-extra-Item results in this series.

An exact disjoint partition of the final adaptive outcome shows where
combination matters:

| Mutually exclusive policy reachability | Probability per opener |
| --- | ---: |
| Quick alone succeeds | 0.001573353% |
| Additional states only Nest family can satisfy | 0.005232763% |
| Additional states only VIP family can satisfy | 0.043287095% |
| Additional states both Nest-only and VIP-only can satisfy | 0.000346168% |
| **States requiring Nest and VIP together** | **0.016084116%** |

The final row captures states with a search requirement beyond the
capacity of either Item family acting separately. The extra shared row
measures overlap in their individual success sets.

In this fixed population the net nonadditive gain is

```text
adaptive - Nest-only - VIP-only + Quick-only
= combined-only contribution - additional shared contribution
= 0.016084116 - 0.000346168
= +0.015737948 percentage points
```

The adaptive event by Basics missing in the initial eight observed cards:

| Missing Basic targets | Probability per opener |
| ---: | ---: |
| 0 | 0.000020203% |
| 1 | 0.001553150% |
| 2 | 0.006865489% |
| 3 | 0.034972775% |
| 4 | 0.023111879% |

## Computation and validation

For every seven-card category multiset and first-turn drawn-card category,
the model uses exact hypergeometric weights and a conditional *joint*
Prize distribution over Gothita and other Basics. A search must leave
the necessary real copies unprized. The correct number of searched copies
is then removed from the physical deck before computing the second-turn
draw-to-evolution probability.

The independent SFT enumerates labeled opening sets, Prize sets, first
turn draws, physical searched Basic identities, and second-turn draws
for 12-card and 13-card toy populations plus a zero-Prize control.
It independently recomputes all four policy strata and five disjoint
reachability classes. The source card texts and legality of Quick Ball,
Nest Ball, VIP Pass and Sky Field are checked against the bundled database.

## Interpretation and limitations

The potential marginal benefit of Basic search Items is conditional on
how much **total typed search capacity** is available during the first
turn, the actual Prize configuration, and the Basic slots that remain
unfilled. Joint capacity can provide a genuine complementarity term,
even after accounting for double-counted individual successes.

The opponent's Collapsed Stadium and Ninetales lock, Gothita survival,
all later demanded Bench entrants, any extra drawing or searching,
specific Basic Pokémon Abilities, and broader matchups are exogenous.
This is an exact bounded access model for a hypothetical 60-card
population, with no claim of measuring win rates or an optimized deck.

Next: incorporate the discard-payment requirement for a second Quick
Ball alongside the free Nest and first-turn VIP searches. That will
require preserving turn-two evolution pieces while allocating discard
resources to first-turn setup.
