# Low-Prize promotion can eliminate all defensive Switch value

## Structural insight

In a fixed three-Pokémon endgame with no opposing gust, one defender Pokémon taking fewer than three Prizes is sufficient to allow the defender to **force all three Pokémon to be Knocked Out** before the attacker can win a six-Prize game. Switching a damaged defender between Active and Bench therefore cannot further extend the attack count when damage persists, there is no healing or replenishment, and attacks deal one hit at a time.

This explains a failure mode for additive card-value models: a defender's switching Item may be strong on a board with three high-Prize targets, yet contribute exactly zero when a low-Prize sacrifice gives the defender an alternate route to delay winning.

## Assumptions and proof

- The defender has exactly three Pokémon. Each KO takes one, two or three Prize cards and requires an arbitrary positive integer number of hits (remaining durability).
- The attacker must collect six Prizes or Knock Out every opposing Pokémon to win; its attack only damages the Active by one hit, with damage persisting. It has no Boss or other gust.
- The defender chooses promotion after a KO, can use Switch between turns, and has no other way to modify damage or the board. No opposing attack, healing, Energy attachment or forced opponent switching exists.

With three defender Pokémon each granting at most three Prizes and **at least one worth fewer than three**, the opponent can ensure that the first two KOs pay fewer than six Prizes:

1. If the starting Active is worth fewer than three Prizes, its first KO pays at most two; the next KO pays at most three, so the attacker remains short of six.
2. If the starting Active is worth three Prizes, at least one Benched Pokémon must pay fewer than three. After the first KO the defender promotes that low-Prize Pokémon. The two KOs again pay fewer than six.

The attacker must then KO the third Pokémon. Without any defensive Switch, the player already needs **the sum of all three Pokémon's remaining hit counts** to finish. This is the absolute upper bound when damage cannot be healed, so any Switch strategy can do no better.

The result applies even if there exists an apparently decisive 3-Prize + 3-Prize two-KO route on the defender's board. The defending player's control of post-KO promotion denies that route while the attacker has no gust available.

## Exact 252-board census

An exhaustive [reproduction script](reproduce.py) enumerates distinct states with one distinguished starting Active and an unordered Bench of two. The cards' Prize rewards are 1/2/3 and remaining hits are 1/2/3. Only configurations with at least six total Prize value are included. Each board is tested under a 12-card defender draw pile containing 0..4 Switch Items (other draws inert), with the attacker having no Boss.

| Board family | Distinct structural boards | Switch improves expected attack count |
| --- | ---: | ---: |
| At least one Pokémon worth fewer than 3 Prizes | **234** | **0** |
| All three Pokémon worth 3 Prizes | **18** | **9** |
| **Total** | **252** | **9** |

All 234 mixed-reward boards have an exact expected attack count equal to the sum of their HP hit thresholds, for every tested Switch-copy count. Among the all-three-Prize boards, only half exhibit a Switch benefit under this limited durability census, demonstrating that high Prize value alone is insufficient.

An independently checked combinatorial argument verifies all 26 ordered reward triples with at least one reward under three: their starting Active plus at least one choice of the next promoted Pokémon yields fewer than six Prizes.

### Controlled contrast

All three defender Pokémon have `(3 Prizes, 2 hits)`, with 12 defending draws:

- Without Switch, attacker needs four attacks.
- One hidden Switch raises the expectation to `17/4 = 4.25` attacks.
- Change only one Benched Pokémon's reward from three to two Prizes; attacker now needs six attacks regardless of whether the defender has zero, one, two, three or four Switch copies.

The new low-Prize Pokémon makes ordinary promotion alone sufficient to force a three-KO route. This effect concerns attack-count outcomes against an optimal adversary, rather than an actual tournament recommendation to Bench low-Prize liabilities.

## Context and limitations

[The exact two-sided draw engine](../../tools/two_sided_stochastic_escape.py) supports the enumeration; [switch_access_window](../switch_access_window/) provides the positive all-three-Prize access theorem. The script's full-board survey is a deterministic and stochastic regression check, while the prize-sum argument provides the general proof for the stated fixed three-Pokémon conditions.

The conclusion depends strongly on the absence of gust, attacks affecting Benched Pokémon, multi-KO attacks, defensive Prize-modification rules, and opposing knockouts. Introducing any of these can overturn the dominance. The structural-board counts are unweighted and do not describe how often such boards occur in paper Expanded.

- [Reproduce exact census](reproduce.py)
- [CI workflow](../../.github/workflows/validate-low-prize-escape-dominance.yml)

Further analysis could quantify how one accessible Boss's Orders restores a shorter two-KO route and thus restores conditional value to the defender's switching resources.
