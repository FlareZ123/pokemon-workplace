# Judge and Ace Trainer change the Beheeyem hand-reset frontier

## Question and correction to the earlier candidate set

The [N/Iono/Marnie comparison](../beheeyem_supporter_reset/) established that Marnie minimizes the isolated Beheeyem second-packet probability when zero or one Prize is taken, whereas N wins at two Prizes, **among those three Supporters**. It did not assess two further legal paper Expanded replies: **Judge** and **Ace Trainer**.

The supplied card database identifies Judge `sm6-108` as "Each player shuffles their hand into their deck and draws 4 cards" and Ace Trainer `xy7-69` as usable only if its player's remaining Prizes exceed the opponent's, then shuffling both hands into their decks and redrawing 6 for its player, **3 for the opponent**. These are Supporters, so Beheeyem's Mysterious Noise Item prohibition does not stop them.

The opponent is modeled as having six remaining Prizes, while the Beheeyem player has `6-r` after the first attack's hypothetical KO awards `r` Prizes. Ace Trainer is consequently **unavailable at r=0 and available at r=1,2**. This models a counterplay unlock caused by Prize progress itself.

## Exact conditional results

Same controlled setup as the previous studies: three mature-board Basics fixed, six T2 residual cards from 57, six Prizes from the remaining 51, direct Beheeyem plus Triple Acceleration Energy (TAE) or a paid one-copy tutor rescue, shuffling Beheeyem+TAE+Elgyem back into 48/47 cards, and one T3 blind draw after the opponent's reset. Four Beheeyem, four TAE, one Computer Search; all neutral filler is assumed disposable.

| T2 Prizes awarded | Iono | N | Marnie | Judge | Ace Trainer |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | 3.675774% | 3.475483% | 2.019569% | **1.899188%** | Ineligible |
| 1 | 2.820953% | 2.647861% | 2.019569% | 1.890141% | **1.198389%** |
| 2 | 2.019569% | 1.881457% | 2.019569% | 1.881457% | **1.192659%** |

These are **joint first-and-second attack packet access probabilities**, conditional on the staged board, the hypothetical number of T2 Prizes, the opponent choosing the named Supporter, and all other model assumptions. They are *not* actual game win rates, T2 KO probabilities, or a meta-game prescription.

Judge and Ace Trainer physically **shuffle the old hand and newly earned Prizes into the deck**, rather than bottoming them as Marnie does. Judge draws 4 for Beheeyem. Ace Trainer draws 3 for Beheeyem and requires the opposing player to be behind on Prizes. N draws `6-r`. Hence at r=2, **Judge and N have exactly the same probability distribution and result** under the fixed opponent-Prize model.

## Complete finite census and policy significance

The exact Python engine traverses **1,152 configurations**: 16 Beheeyem/TAE copy-count pairs, four one-copy tutor classes (Computer Search, Mysterious Treasure, Ultra Ball, Guzma & Hala), six T3 draw budgets `d=0..5`, and three awarded-Prize counts `r=0..2`.

Across all configurations, checking both **direct-first-packet** and **paid-tutor-rescued-first-packet** contributions separately:

- Judge has equal or lower second-packet success mass than Marnie and N for every configuration and route.
- At r=1 or r=2, Ace Trainer has equal or lower second-packet success mass than Judge for every configuration and route.
- Judge and N agree exactly at r=2. This follows from their matching hand-replacement rule and draw quota, rather than a numerical coincidence.
- Observing that the Beheeyem player publicly used a tutor to rescue their first packet changes the conditional risk but does not reverse this five-Source optimal ordering in the enumerated model.

This corrects an overbroad reading of the three-Supporter candidate comparison: the stronger **conditional adversarial action** is Judge if neither player has taken a Prize, then Ace Trainer if Beheeyem takes a Prize while its opponent stays on six. The optimizer must first filter physically legal actions based on the Prize race. Whether the opponent actually *holds* these Supporters, can reach them, and should use their Supporter action remains a separate problem.

The opportunity to use Ace Trainer can disappear later if the opponent also takes Prizes, even with the same Beheeyem packet state. A full opponent solver must represent both players' remaining-Prize counts and Supporter access instead of selecting the response with the lowest conditional packet rate.

## Reproducibility

- [Generalized exact Supporter engine](../../tools/beheeyem_supporter_reset.py): the pre-existing physical hand-and-Prize enumerator now accepts Judge and Ace Trainer. It rejects Ace Trainer at r=0 under the specified Prize state, retaining the existing N/Iono/Marnie semantics.
- [Exact regression](reproduce.py): checks 1,152 parameter configurations, both first-packet-route components, Prize gates, action-order rankings, equivalence to N at r=2, selected exact rational anchors, and conservation of the direct/rescued decomposition.
- [Independent physical Monte Carlo](monte_carlo.py): constructs individual 57-card residual decks, six-card hands and six Prizes, executes a first packet or actual tutor rescue, returns all recycled cards, shuffles the complete hand back under Judge or Ace Trainer, draws the card-text quota plus `d`, and checks the next packet. It uses five seeded 200,000-trial cases and a six-standard-error tolerance.
- [CI workflow](https://github.com/FlareZ123/pokemon-workplace/actions/workflows/validate-beheeyem-judge-ace-response.yml) runs the exact and independent checks.

A separate independent local physical simulation ran four 400,000-shuffle cases, with observed rates within one standard error of the exact probabilities for B4/TAE4/Computer Search/d1.

## Assumptions and unresolved work

The Beheeyem model starts with two evolution-ready Elgyem and an anchor already on board, ignores actual damage/KO feasibility, and treats the number of T2 Prizes taken as an exogenous event. The opposing player is assumed to have taken no Prizes yet. The opponent's Supporter is made available without searching, draw/discard/Ability action budgets outside these packets remain abstract, and `d` is an additional arbitrary future draw budget. There is no whole-turn cost, opponent win-condition model, or belief-constrained hand observation in the payoff. The 0-Prize branch makes Ace Trainer unavailable only because the opponent also has exactly six left.

Priority next step: introduce opponent Supporter **access probabilities and both-sided Prize state**, then optimize legal reachable responses rather than a free menu of hypothetical Supporters. Analyse Ace Trainer when its restriction disappears as the Prize race changes. Preserve the important distinction between source availability, mechanical effectiveness, and effect on true game wins.
