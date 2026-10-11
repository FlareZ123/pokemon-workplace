# No hand-reset Supporter can outperform the strongest hand-reset response

## Why include the no-action alternative?

An exact [expanded Supporter response study](../beheeyem_judge_ace_response/) found that Judge is at least as disruptive as N and Marnie for the modeled Beheeyem attack packet, and that Ace Trainer is stronger still once the Beheeyem player takes a Prize. But **best among hand-reset Supporters** need not equal **best available opponent response**.

The adversary can choose to spend its one Supporter action on something other than a hand reset, or play no Supporter. In this isolated test, the candidate called **No hand reset** means Beheeyem's surviving hand is unchanged during the opponent's reply. The model deliberately excludes all other opponent actions and their own value.

Under severe draw starvation, giving the Beheeyem player a fresh random hand can help them recover their recycled Beheeyem and Triple Acceleration Energy (TAE), even if the replacement hand contains fewer cards than another reset would provide.

## Exact worked example: four Beheeyem, four TAE, one Computer Search

Two evolution-ready Elgyem and an anchor Basic are already in play. The player receives six T2 residual hand cards from the remaining 57, six original Prizes are set, and the first attack uses a directly held Beheeyem+TAE or pays a real one-copy tutor to find one missing piece. Beheeyem, TAE and its underlying Elgyem return to the shuffled 48/47-card deck. The first attack is **assumed** to award r=0,1,2 Prizes. One additional T3 draw is modeled.

The opposing player starts with six Prizes remaining, so Ace Trainer is available only after the Beheeyem player has taken at least one.

| T2 Prizes awarded | Keep hand intact | Strongest eligible hand reset | Lower next-packet access |
| ---: | ---: | ---: | --- |
| 0 | **0.662553%** | Judge: 1.899188% | Keep hand |
| 1 | **1.125764%** | Ace Trainer: 1.198389% | Keep hand |
| 2 | 1.679597% | **Ace Trainer: 1.192659%** | Ace Trainer |

All percentages represent **joint T2+T3 packet-access rates conditional on the fixed three-Basic board and exogenously awarded Prizes**, rather than actual Knock Out probabilities or match win rates.

The response switches from preserving the depleted hand to Ace Trainer only after the second Prize in this particular configuration. A blanket policy of playing the most disruptive available hand-reset Supporter would be suboptimal even for the narrow objective.

## Complete 1,152-configuration comparison

Using the two existing independently developed exact enumerators, `beheeyem_prize_packet.exact_prize_take` for unchanged hands and `beheeyem_supporter_reset.exact_supporter_reset` for changed hands, the study enumerates:

- 16 physical copy-count combinations of Beheeyem and TAE (each 1–4).
- Four one-copy tutor families, with actual discard-filler payment and search target eligibility.
- Six alternative T3 draw budgets (0–5).
- Zero, one or two earned Prizes.

**945 of 1,152** configurations favor leaving the hand intact; **207** favor the best eligible hand reset. There are no aggregate ties in this finite grid.

| T2 Prizes awarded | Keep hand better | Reset better |
| ---: | ---: | ---: |
| 0 | 384 | 0 |
| 1 | 374 | 10 |
| 2 | 187 | 197 |

The first packet can be executed directly from the T2 hand, or by playing a tutor to rescue one missing card. Because the tutor is an explicitly played Item or Supporter, this branch may be publicly observable. The results split cleanly:

| First attack route and awarded Prizes | Keep hand better | Reset better |
| --- | ---: | ---: |
| Direct, 0 Prizes | 384 | 0 |
| Direct, 1 Prize | 323 | 61 |
| Direct, 2 Prizes | 99 | 285 |
| Paid tutor rescue, 0 Prizes | 384 | 0 |
| Paid tutor rescue, 1 Prize | 384 | 0 |
| Paid tutor rescue, 2 Prizes | 384 | 0 |

The last three rows are revealing. Whenever the first attack **consumed its single available tutor and its discard payment**, even Ace Trainer consistently improves Beheeyem's packet supply relative to leaving its depleted residual hand untouched in this model. The opponent may rationally avoid the hand reset upon observing the tutor expenditure.

An exact, finite-model public-signal effect is therefore present: the best narrow resource-denial decision can change after the opponent sees how the attack was assembled. The study assumes the first attack follows a fixed canonical policy: direct if both packet cards are held, tutor rescue otherwise when feasible. An actual player could use a tutor unnecessarily for deck thinning, and the opponent may not infer the exact internal state from the public action alone.

## Evidence and reproducibility

- [Full exact census](reproduce.py) asserts all 1,152 aggregate comparisons, every direct/rescue branch comparison, two exact no-reset rational anchors and first-packet equality between the independently constructed models.
- [Physical no-reset simulation](../beheeyem_prize_packet/monte_carlo.py) creates and shuffles physical card categories, awards face-down Prizes, and checks the next attack packet without changing the hand.
- [Physical Judge/Ace Trainer simulation](../beheeyem_judge_ace_response/monte_carlo.py) independently reconstructs the full-deck hand reset and card-text redraw quotas.
- [CI workflow](https://github.com/FlareZ123/pokemon-workplace/actions/workflows/validate-beheeyem-optional-supporter-response.yml) runs all three checks.

The internal comparison is **not an unconstrained optimal gameplay policy**. It ignores damage, how frequently Beheeyem's weak first attack earns any Prizes, opponent's available Supporters, the opponent's board and own tactical incentives, opponent knockouts or gust, next-turn actions to draw `d` cards, strategic value of held filler, and board position. Opponent actual Prize count is fixed at six.

## Strategic implication and next step

A card's isolated denial strength is a poor proxy for action value. The resource source reshuffled into the attacker's deck matters; a redraw can unblock a stalled attacker. A solver should always retain a no-hand-reset action in the reply policy, as well as other non-reset opponent actions.

The next useful experiment is to include **opponent Supporter access** and **both players' changing Prize counts**, allowing a genuine information-limited policy to decide which legally reachable response to take. Until then, these exact results serve as a targeted regression benchmark for avoiding automatic "hand disruption must be helpful" assumptions.
