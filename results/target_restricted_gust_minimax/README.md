# The Serena target trap: prize-weighted and position-dependent gust value

## Question and motivation

[The Expanded Trainer gust catalog](../trainer_gust_catalog/) records that
Boss's Orders can choose any opposing Benched Pokemon, while Serena's gust
mode chooses only an opposing **Pokemon V-family** target. Does simply counting
the number of Pokemon V on the opponent's board predict whether replacing one
of two Boss gusts with Serena sacrifices a winning route?

A Serena card has an alternative discard-and-draw mode, which is useful in
other game states. This experiment **only evaluates the gust mode**. It does
not rank the cards' overall value.

## Typed, bounded minimax

Five public target classes are used:

| Abstract class | Prize reward | Serena-eligible | Representative card family |
| --- | ---: | --- | --- |
| N1 | 1 | No | Ordinary single-Prize Pokemon |
| N2 | 2 | No | Pokemon ex / Pokemon-GX |
| N3 | 3 | No | TAG TEAM Pokemon-GX |
| V2 | 2 | Yes | Pokemon V / VSTAR |
| V3 | 3 | Yes | Pokemon VMAX |

Every Pokemon takes exactly one attack to Knock Out, regardless of HP.
The opposing board has 2..6 Pokemon (including Active), a full eligible
potential of at least six Prize rewards, and adversarial next-Active choice
after each KO. The attacker needs six Prizes or can win by removing the last
opponent Pokemon. No further Pokemon enter play.

The available gust inventories are two Boss tokens, Boss + Serena, or two
Serena tokens. A token is considered already in hand and executable if its
target condition is met. Each attacker turn permits one attack and at most
one strategically meaningful gust. Serena's other mode, draw resources,
Supporter access, lock, healing, evolving and energy cost are excluded.

The 5-class multiset geometry generates **1,212 distinct initial boards**.

## Exact results

Across the 1,212 boards, the attack-turn regret from replacing one of two
Boss gusts with a Serena gust is:

| Extra attacks required with Boss + Serena | Structural boards |
| ---: | ---: |
| 0 | 1,086 |
| 1 | 116 |
| 2 | 10 |
| **Total** | **1,212** |

In **126 classes**, one Serena cannot substitute for the second unrestricted
Boss. These counts are a census of abstract board types, not real matchup
frequencies.

Breakdown by the total number of V-family Pokemon, including Active:

| V-family Pokemon in play | Board classes | Boss + Serena worse than 2 Boss |
| ---: | ---: | ---: |
| 0 | 146 | 55 |
| 1 | 301 | 46 |
| 2 | 315 | 18 |
| 3 | 240 | 6 |
| 4 | 140 | **1** |
| 5 | 58 | 0 |
| 6 | 12 | 0 |

Even with four V-family Pokemon among six opposing Pokemon, a meaningful
Serena targeting gap can remain.

## Witness A: same multiset, different Active target

Three opposing Pokemon: two N3, one V2. The opponent can provide two
three-Prize Knock Outs or a two-Prize Knock Out.

- If **V2 starts Active** and both N3 are Benched, two Boss gusts can select
  the two N3 for a two-attack six-Prize win. Boss + Serena requires
  **three** attacks because Serena cannot select an N3 target.
- If **N3 starts Active**, the attacker can take three Prizes naturally,
  and Boss can gust the other N3 next turn. Both inventories need
  **two** attacks.

Hence the total V-family count and the Prize multiset are identical, but
the target-position geometry changes the value of Serena.

## Witness B: high V density still leaves an inaccessible winning pair

Opponent Active V2, Bench N3 / N3 / V2 / V2 / V2.

This is a six-Pokemon board containing **four V-family Pokemon**, and both
three-Prize targets are non-V. Two Boss gusts can Knock Out the two N3
in two attacks for six Prizes. Boss + Serena needs **three attacks**
against adversarial promotion. An interpretation such as `4/6 targets
are Serena-eligible` overlooks that the *two highest-Prize targets*
are precisely the ones Serena cannot select.

This can represent, mechanically, a board with four two-Prize Pokemon V
and two three-Prize TAG TEAM Pokemon-GX, but it is a constructed
counterexample. No prevalence in competitive Expanded is claimed.

## Strategic interpretation

Target eligibility should be represented at the physical Pokemon level,
including whether the Pokemon is currently Active or Benched, rather than
as a scalar deck- or matchup-level gust strength.

The useful question is whether each gust target is **a Prize-relevant
accessible target at the time the effect can be used**. When target scope
narrows to Pokemon V, a numerically high V-family presence can still omit
the crucial route to six Prizes.

The experiment complements the Counter Catcher timing and lock-deadline
studies: identical scope with changing permissions, or identical
permissions with different scope, can each change the optimal gust line.

## Validation

- Model: `tools/target_restricted_gust_minimax.py`
- Independent Boolean deadline checker:
  `results/target_restricted_gust_minimax/reproduce.py`
- **3,636 initial board/inventory scenarios** checked independently
  (1,212 boards times three gust inventories).
- The regression verifies all census counts, all position/density
  witnesses, and no-V consistency against the original unrestricted Boss
  minimax.

## Limitations and next steps

The N1/N2/N3 and V2/V3 classes are illustrative and omit many real Pokémon
card distinctions, including actual HP, Weakness, defense, board evolution
and Prize modifiers. A card's current family and rules determine eligibility;
the abstract classification should never be inferred just from Prize value.

Serena's real draw mode could make it useful in states where its gust mode is
ineligible; both modes share a Supporter action. A stronger planner should
combine target-type restrictions, Supporter budgeting, drawn cards, current
Prize needs, and information about which Pokémon will actually be Benched.
