# Shoes-free Arc Phone to Peonia Prize reconnaissance

## Question and result

Can repeated Arc Phone observations improve Peonia's chance of recovering a known-Prized singleton **without Trekking Shoes**? Yes. Arc Phone's optional exchange moves an unknown Prize card onto the deck top. The next Arc Phone sees that card, and can return it to a known Prize position if valuable. Peonia may then select that position.

In a controlled K1 state with one target singleton T uniformly hidden among six face-down Prize positions, an inert-filler deck top, a held Peonia, and one expendable filler card to pay Peonia's replacement cost, the optimum depends on the number a of held, usable Arc Phone copies:

| a | Exact P(T recovered) |
|---:|---:|
| 0 | 1/2 |
| 1 | 1/2 |
| 2 | 2/3 |
| 3 | 5/6 |
| 4 | 1 |

**Four Arc Phones plus Peonia guarantee the rescue** in this conditional state, even though no Trekking Shoes is present. The first Arc Phone alone adds no K1 value.

## Source and feasibility

The card pool gives Arc Phone (\`swsh11-152\`) its look-at-top-then-optional-face-down-Prize-exchange effect and Peonia (\`swsh6-149\`) the take-up-to-three-Prizes/replace-with-hand effect. Both are legal under the BW-onward paper Expanded card-pool boundary. The supplied advanced player's rulebook permits multiple Items per turn and normally one Supporter (B-01 and B-03). Every policy respects the order of observations. None sees the exchanged Prize until the next Arc Phone inspects the deck top.

Peonia's hand payment is material. At least one expendable filler is assumed to be held **in addition** to the usable Arc Phones and Peonia. When selecting three Prize cards containing T, that filler and the other two retrieved cards can be returned, retaining T. With no spare payment after exhausting Arc Phones, this guarantee fails.

## Exact theorem and witness strategy

Let n be the number of exchangeable face-down Prize slots, d the number of deck positions, and a the usable Arc Phone copies, with one Peonia, sufficient hand payment, and only one valuable hidden T.

If T is known to be Prized (K1), the closed form is:

- a = 0: \`min(n,3)/n\`.
- a >= 1: \`min(n,a+2)/n\`.

The second expression equals the first when a=1. Arc Phone's initial top observation is known filler in this case.

If T is uniformly located among the n Prize positions and d deck positions (K0-like hidden composition), the closed form is:

- a = 0: \`min(n,3)/(n+d)\`.
- a >= 1: \`[1+min(n,a+2)]/(n+d)\`.

The extra 1 comes from the initial deck-top location. Deeper deck positions remain inaccessible without a draw. For six Prizes and 46 unknown deck cards, a=0..4 gives \`3/52,4/52,5/52,6/52,7/52\`.

**Achieving policy:** If an Arc Phone observes T on the deck top, exchange T into a known Prize position and use Peonia to select it. Otherwise, exchange the current filler top with an as-yet uninspected Prize. The next Arc reveals its former identity. Repeat as Arc copies allow; after observing only filler, let Peonia select up to three previously uninspected slots.

**Upper bound:** Before Peonia is spent, a Arc Phones can reveal at most a-1 new Prize identities because each unknown Prize must first be moved to the deck top and subsequently observed. Peonia can take three additional slots. In K0, the initial Arc observation covers at most one further deck-top location. No other action in the model acquires T.

## Verification

\`tools/arc_peonia_shoes_free.py\` implements a Fraction-based Bellman belief solver and a separate labeled-physical-world oracle that executes Arc exchanges and branches only on player-visible deck-top observations. An executable check evaluates all 240 combinations of n=1..6, d=1..4, a=0..4 and K1/K0 conditions, confirming both solvers equal the formula. Run \`python results/arc_peonia_shoes_free/reproduce.py\`.

## Conditional four-copy availability

To show why the 100% conditional result does not imply deck-wide reliability, a separate 60-card sampling model conditions on T already being Prized, Peonia and an expendable filler already being held, and four Arc copies occupying random locations among the remaining 57 cards. If h of those 57 locations are accessible, A is hypergeometric and

\`E[P(T recovered)] = 1/2 + [P(A>=2)+P(A>=3)+P(A>=4)]/6\`.

| h other accessible cards | Conditional recovery |
|---:|---:|
| 7 | 8674/16929 = 51.2375% |
| 10 | 7549/14364 = 52.5550% |
| 20 | 707/1188 = 59.5118% |
| 40 | 13580/16929 = 80.2174% |

Those are exact conditional hand-access probabilities. They exclude obtaining Peonia, initial Basic Pokémon legality, the spare filler condition, search costs, opponents, locks and Supporter contention. The result is a card-interaction and resource-availability study, **not** a competitive win-rate estimate.

## Relationship to existing work and next question

\`results/repeated_prize_probe/\` uses Arc/top observations after Peonia; \`results/arc_phone_chain_access/\` uses Shoes for acquisition. This finding isolates a shoes-free chain of successive Arc Phone reveals **before** Peonia. Next, compare this four-Arc route with fewer Arc Phones plus one or more Trekking Shoes under paid access, opener, and Prize constraints.
