# Optional-damage retaliation frontiers against Zamazenta

## Research question

Across all legal English paper-Expanded prints in the **fixed optional
damage-boost** text family, how many attack signatures can cause an attacker
to Knock Out itself through Zamazenta's Strong Bash reflection while the
lower-damage attack would both Knock Out Zamazenta and survive?

The parameterized scan is
`tools/optional_boost_reflection_frontier.py`, with a reproducible
regression in `results/optional_boost_reflection_frontier/reproduce.py`.

## Method

The existing optional attack-damage catalog identifies 71 effectively legal
print rows with the narrow `You may ... If you do, this attack does N more
damage` form. Ten have a variable multiplier and are excluded, leaving
**61 fixed-boost prints**.

For each eligible attacking print, use the current bundled card's HP and
types, and Zamazenta `sv10-146`'s current 130 HP, Fire Weakness x2 and
Grass Resistance -30. Calculate both branches using the existing exact
damage-calculation kernel. Retain only attacks where the **lower** branch
already Knocks Out Zamazenta.

For each such attack, enumerate all non-Knocked-Out starting damage values in
steps of 10. Keep those satisfying

`starting_damage + lower_damage < attacker_HP <=
starting_damage + boosted_damage`.

This gives the **complete damage-counter-aligned survival frontier** for the
specified no-other-modifier state. The print counts are grouped by identical
card name, attack text, current HP, and type, so reprints do not inflate the
distinct-signature count.

## Findings

Two distinct attack signatures, represented by four effectively legal prints,
have such a frontier against Zamazenta.

| Attacker | Base reflected damage | Boosted reflected damage | HP | Starting damage values that flip survival |
| --- | ---: | ---: | ---: | --- |
| Cetitan ex, Crushing Press | 140 | 280 | 300 | 20, 30, ..., 150 (14 values) |
| M Houndoom-EX, Inferno Fang | 160 | 320 | 210 | 0, 10, ..., 40 (5 values) |

Cetitan ex's two prints are `sv10-65` and `sv10-210`.
M Houndoom-EX's two prints are `xy8-22` and `xy8-154`.

Inferno Fang prints 80+ and can discard all Fire Energy to add 80.
Zamazenta's Fire Weakness doubles either branch, so the actual reflected
damage is 160 or 320. This is a useful example of why a mere comparison of
printed damage numbers misses real tactical frontiers.

## Strategic qualifications

The frontier represents **possible board states**, not their probability.
Strong Bash must actually be live from Zamazenta's prior turn, each attacker
must have the required attack Energy, the optional cost must be available,
and other damage modifiers must be absent. On a sequence where Zamazenta
attacked the same M Houndoom-EX for 70 damage last turn, the 0–40 existing
damage frontier would not arise without healing or another prior action.
For the Houndoom states, the attack's temporary switch, healing, or timing
history must therefore be considered before declaring an executable
Archetype-Line-Specific.

The lower branch already Knocks Out the defending Zamazenta, so higher
damage yields no additional Prize value in these states. However, the
higher branch's chosen cost may have independent strategic implications
when the game would continue. The data does not establish match frequencies
or archetype-level win-rate differences.

This result extends
[optional_overkill_reflection/](../optional_overkill_reflection/) from
one concrete terminal example to a complete fixed-boost attack-text census
against this defender in the specified conditions.
