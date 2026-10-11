# Joint Prize rescue with Arc Phone, Trekking Shoes, and Peonia

## Result: one acquisition Item alleviates a multi-target Peonia bottleneck

Extending [Arc-only multi-target reconnaissance](../arc_peonia_multi_target/), this study permits held Trekking Shoes to recover target cards that Arc Phone has displaced onto the deck top, and permits Peonia to be used at any point in the same turn.

One, two or three strategically required singleton cards are all known to be among six face-down Prize cards. All deck cards are inert filler, including the original deck top. The player holds exactly four usable Items in some combination of Arc Phone (A) and Trekking Shoes (S), plus one Peonia and ample hand filler for its Prize replacement payment. Success requires **all target singleton cards in hand by the end of this turn**.

The exact optimal probabilities are:

| Four-Item mix | One target | Two targets | Three targets |
|---|---:|---:|---:|
| 0 Arc / 4 Shoes | 1/2 | 1/5 | 1/20 |
| 1 Arc / 3 Shoes | 2/3 | 2/5 | 1/5 |
| 2 Arc / 2 Shoes | 5/6 | 2/3 | 1/2 |
| 3 Arc / 1 Shoes | **1** | **13/15** | **3/5** |
| 4 Arc / 0 Shoes | **1** | 4/5 | 2/5 |

For q=2 the fourth Item being Shoes rather than Arc improves joint retrieval by **1/15 = 6.6667 percentage points**. For q=3 the improvement is **1/5 = 20 percentage points**. Both packages guarantee access to a lone known-Prized target, so the multi-target objective exposes value invisible to a one-target analysis.

## Physical action mechanism

Arc Phone (\`swsh11-152\`) looks at the deck top and may exchange it with a face-down Prize. A target displaced from an unknown Prize to the deck top cannot be moved directly into hand by Arc Phone. Another Arc can inspect it and return it to a known Prize slot, where Peonia can retrieve it.

Trekking Shoes (\`swsh10-156\`) can instead put a target directly from deck top into hand after observing it. That means Peonia (\`swsh6-149\`) can use its three acquisitions on *other* hidden targets. The value is especially pronounced when several singleton cards must all be recovered. Shoes can also be played after Peonia to collect a target left inaccessible to Peonia, provided Arc Phone can expose it on top.

Every relevant card text is within the BW-onward paper Expanded card pool. The model preserves the rule that a player normally plays only one Supporter per turn and allows multiple Items, which are used with their actual observation timing.

## Exact adaptive policy and validation

\`tools/arc_peonia_multi_target_shoes.py\` is a physically exact finite-world \`Fraction\` Bellman optimizer. It tracks:

- an exchangeable joint posterior over the physical Prize and deck-top positions of all remaining target cards;
- each optional Arc Phone look-then-swap choice, with the swapped Prize initially unobserved;
- each Trekking Shoes top observation and target acquisition;
- a Peonia selection of up to three physical Prize slots, revealing and transferring target cards to hand;
- target-card conservation and the number of remaining accessible Items.

The solver branches only on observations legitimately available at the time and conserves probability masses even when several initial target configurations merge after acquisitions.

Its regression checks four-Item mixes, one to three targets, and n=3..6 Prize positions. Boundary checks compare the no-Shoes cases against the separately developed multi-target combinatorial/physical oracle and the singleton cases against the independently implemented Arc/Shoes solver.

Run \`python tools/arc_peonia_multi_target_shoes.py\`; the common Windows CI workflow validates the same comparisons.

## Strategic interpretation and limitations

This is a quantified instance of **joint acquisition capacity versus positional knowledge**. When several separate Prized cards are mandatory, the optimal number of information-revealing Items need not be the maximum possible. A card which physically moves a revealed target into hand can be more useful than another search Item because it preserves a limited downstream acquisition channel.

The model conditions on the target cards being Prized, already holding Peonia and all relevant Items, enough expendable filler, and an otherwise inert filler deck. It omits opening-hand acquisition, opponent locks, actual deck card composition, ordinary Prize taking and the differing tactical utilities of distinct singleton cards. The numerical results do not constitute competitive match-winning probabilities.
