# Boss's Orders restores the value of the defender's Switch

## Research question

[Low-Prize promotion dominance](../low_prize_escape_dominance/) shows that a defender can force all three KOs, making switching useless, when the attacker has no gust in a six-Prize endgame involving a lower-Prize Pokémon. Does a single accessible Boss's Orders overturn this verdict and **make opposing Switch worth including**, and how does that depend on the timing of each player's draws?

A simple board provides an exact answer and a two-sided combinatorial formula.

## Controlled board and actions

Three opposing Pokémon all require **two attack hits**. The initially Active target pays three Prizes. The Bench consists of one three-Prize target and one two-Prize target. The attacker wins on six Prizes; damage persists, no Pokémon are replaced or healed, and every attack affects only the Active. The defender chooses all KO promotions and can play already drawn Switch Items between attacking turns. No normal Retreat, opponent attack, Energy, other Supporters, search/draw effects, or Prize-card draws. All other deck cards are inert.

The attacker has exactly one Boss's Orders randomly located in a finite draw pile of size `A>=6`. The defender has `S` Switch Items randomly located in an independent pile of size `D>=5`, with `0<=S<=D`. Both draw once before making their respective ordinary turn decisions. The model is exact chance/minimax for the number of attacker turns; card texts are confirmed from the bundled English `swsh2-154` Boss's Orders (Supporter) and `sv1-194` Switch (Item).

The general game-tree implementation discloses category-level opponent hand counts to both players. For the present theorem the constructive strategies are based on the visible gust and Switch opportunity, and the independent complete-physical-order oracle agrees in the enumerated cases. The claim remains bounded to the stated controlled board.

## Exact one-Boss, many-Switch theorem

Let `Q(k,D,S) = C(D-k,S)/C(D,S)`, interpreted as zero when `S>D-k`. This is the probability that **none** of the defender's Switch copies occurs within its first `k` draws.

The exact minimum expected number of attacker attacks is

`E(A,D,S) = 6 - (6/A) Q(3,D,S) - (1/A) Q(4,D,S).`

With no Switch, this reduces to `6 - 7/A`; with **no Boss in the attacker's deck**, the required count is **six** regardless of Switch quantity.

### Timing proof

If the attacker draws Boss in its **first three** draws, it can take the initial three-Prize KO and use Boss to bring the second three-Prize target Active, threatening a **four-attack win**. A defender Switch drawn by the **third defender turn** can reverse the gust and force the two-Prize Pokémon into the path, restoring a six-attack requirement. If Switch misses those first three defender draws, the four-attack line completes.

If Boss first appears on the attacker's **fourth** draw, the attacker has already spent an attack damaging the two-Prize Pokémon and could achieve a **five-attack win** after gust. Switch can prevent this only if the defender draws it by its fourth intervening turn.

If Boss first appears on draw five or later, the attacker cannot improve over the six-attack route.

Consequently, there are two mutually exclusive attack-saving cases: a first-three-draw Boss combined with **no defender Switch** in the first three (saves two attacks), or a draw-four Boss combined with no Switch in the first four (saves one). Their probabilities are `3 Q(3,D,S)/A` and `Q(4,D,S)/A`, giving the formula.

This supplies a precise **connector/response complementarity**: the defender Switch copies have exactly zero marginal attack-count value when the attacker lacks gust; once a Boss can access the high-Prize target, the same Switch becomes useful.

## Numbers from 12-card draw piles

One Boss in an attacker deck of twelve; independent defender deck of twelve:

| Switch copies | Expected attacks |
| ---: | ---: |
| 0 | `65/12` = 5.416667 |
| 1 | `401/72` = 5.569444 |
| 2 | `1127/198` = 5.691919 |
| 3 | `191/33` = 5.787879 |
| 4 | `17407/2970` = 5.860943 |

The first defender Switch adds `11/72` expected attacker turns when one Boss is present and remains worth exactly zero when there is no Boss.

The two-card package has a second subtle property. With one defender Switch hidden among twelve cards, increasing attacking Boss copies does **not** monotonically increase Switch's marginal attack delay:

| Boss in attacker draw pile | One-Switch delay relative to no Switch |
| ---: | ---: |
| 0 | `0` |
| 1 | `11/72` |
| 2 | `5/24` |
| 3 | `9/44` |
| 4 | `28/165` |

The Switch response grows in importance as Boss rises from zero to two copies and then weakens as additional Boss copies give the attacker more opportunities to gust around a spent Switch. This is an exact conditional observation under 12-card draw piles, separate from the one-Boss closed form.

## Reproducibility

[`reproduce.py`](reproduce.py) verifies the one-Boss formula against the exact independently established [two-sided Boss/Switch finite-deck solver](../../tools/two_sided_stochastic_escape.py) in **450 configurations** across `A=6..14`, `D=5..14`, and `S=0..4`. It verifies the all-no-Boss/any-Switch ablation and the nonmonotone Boss-count marginal differences.

An independent, fully ordered physical two-deck minimax enumerates **3,576 paired worlds**, using twelve attacker and twelve defender cards, one attacker Boss and one, two or three defender Switch cards. Each physical outcome exactly matches the timing rule above, and every outcome mean agrees with the exact Fraction chance/minimax law.

- [Reproduction script](reproduce.py)
- [GitHub Actions validation](../../.github/workflows/validate-gust-switch-critical-window.yml)
- [Low-Prize promotion dominance](../low_prize_escape_dominance/)
- [Switch-only deadline theorem](../switch_access_window/)

This is a controlled state-level tactical theorem, not a decklist or meta-win-rate claim. The next useful extension is to introduce attacker Supporter contention, defender retreat-payment costs, Item lock deadlines, and actual search access to Boss, then measure the value of the same response package in a selected paper Expanded archetype.
