# Realistic discard costs depend sharply on the protected-resource policy

## Question

The [exact shared-hand Item study](../joint_item_payment/) treats only explicitly designated filler cards as strategically acceptable discards. How sensitive is apparent Item access to the discard-preservation policy? This result formalizes five nested **hypothetical state-dependent discard policies** for the *same physical hands* and evaluates whether Quick Ball, Ultra Ball and Secret Box can pay their printed costs. It quantifies a material component of AMR/DCI without proposing a universally correct policy.

## Source-grounded constructed baseline

A common 60-card category deck consists of B12 starting Basic Pokémon, Q4 Quick Ball `swsh1-179`, U4 Ultra Ball `swsh9-150`, S1 ACE SPEC Secret Box `sv6-163`, F8 designated safe filler and P31 protected other cards. Source card texts require 1, 2 and 3 **other** cards discarded, respectively. These exact prints are marked Expanded-legal in the attached card corpus. Hypothetical F/P categories do not establish a fully playable 60-card list.

After Basic-valid seven-card setup, place exactly one Basic Active, deal six face-down Prizes and draw one ordinary card going second. All Item copies still in hand can potentially become strategically acceptable discards, depending on policy.

Each modeled action reserves **one physical copy of each Item to be played**. For a chosen set of source types `A`, the discard cost is the sum of source-specific printed quotas, and that many *other* physical cards must be available under the chosen policy. No generated search output or new hand draw is recycled to pay later Items.

Five nested discard acceptance rules, from most protective to least protective:

1. **Filler only:** use F cards and preserve everything else.
2. **Same-source spares:** allow F plus excess copies of the source types being played, after reserving one of each.
3. **Non-ACE sources:** allow F plus any unused Quick Ball or Ultra Ball copies; protect singleton Secret Box except when actually playing it.
4. **All sources:** allow F plus unused Quick, Ultra or Secret Box copies, even discarding the unique ACE SPEC to pay another source.
5. **All sources and extra Basics:** additionally allow Basics still in hand after placing the mandatory Active. This sacrifices potential Bench/evolution resources.

Policies 4 and 5 can be poor real-world decisions. Their role is to expose sensitivity to relaxing strategic preservation constraints.

## Exact probability frontier

All numbers are conditional on accepted Basic-valid openings, with the full physical shared-Item deck and one natural turn draw.

| F | Discard policy | Any Item payable | Two distinct Items sequentially payable |
| ---: | --- | ---: | ---: |
| 0 | Filler only | 0.000000% | 0.000000% |
| 0 | Same-source spares | 7.874678% | 0.030543% |
| 0 | Non-ACE sources | 21.966762% | 0.030543% |
| 0 | All sources | 25.126481% | 0.065267% |
| 0 | All sources and extra Basics | 45.479047% | 1.278335% |
| 8 | Filler only | **34.398664%** | **0.409984%** |
| 8 | Same-source spares | **39.781720%** | **1.174009%** |
| 8 | Non-ACE sources | **45.265001%** | **1.174009%** |
| 8 | All sources | **47.619123%** | **1.484689%** |
| 8 | All sources and extra Basics | **61.377440%** | **4.906439%** |
| 20 | Filler only | 63.751517% | 5.485250% |
| 20 | Same-source spares | 65.533420% | 7.594228% |
| 20 | Non-ACE sources | 66.392658% | 7.594228% |
| 20 | All sources | 67.159460% | 8.236499% |
| 20 | All sources and extra Basics | 71.716577% | 13.448545% |

At F8, allowing excess copies of the *source itself* as a cost increases first-item payability by **5.383056 percentage points** relative to F-only. Allowing other non-ACE search copies adds a further **5.483282 percentage points**. Sacrificing any other search Item raises it to **47.619123%**, and counting extra Basics as disposable raises it to **61.377440%**. Those are five precise answers to *different* strategy assumptions about card preservation.

For Secret Box specifically at F8, strict and same-source policy give **0.453336%** payability. Letting it discard unused Quick/Ultra sources raises it to **3.018977%**; allowing extra Basics raises that to **6.512671%**. Its theoretical access edges cannot be assigned one stable probability without specifying which other valuable resources may be consumed.

**Conservation limit:** even the most permissive modeled policy cannot pay all three source costs from the original first-draw seven-card hand. Three reserved Items plus six distinct payment cards require at least nine physical hand cards. Search outputs, card draws and other effects might make a legal sequence possible in a longer turn; they are intentionally outside this snapshot.

## Mathematical and computational validation

[Python exact solver](../../tools/joint_discard_policy_frontier.py) enumerates the conditional Basic-valid first seven cards using multivariate-hypergeometric composition and adds one natural draw. An action set `A` is executable under a policy when all required source copies are present and the count of physically eligible nonreserved hand cards is at least `sum(cost[i] for i in A)`. The model computes individually payable Q/U/S, three named sequential source pairs, all three, any source and any pair under each of the five policies, **45 distinct event probabilities**.

[Independent labeled physical oracle](reproduce.py) exhaustively enumerates actual card identities in opener, disjoint Prize subsets, natural draw and chosen Active Basic for four small decks, including a larger-hand toy with a nonzero all-three sequential witness. All 45 exact event probabilities match.

Additional regressions verify nested policy monotonicity, monotonicity as F grows from zero to 31, exact correspondence of strict events to the older [shared-hand Item solver](../joint_item_payment/) and independently modeled same-family-spare marginal payability to [the earlier isolated-Item quota solver](../basic_valid_discard_quota/). A manually dispatched [Windows CI workflow](../../.github/workflows/validate-agent2-joint-discard-policy-frontier.yml) runs the complete reproducer.

## Consequences for deck evaluation

The result formally demonstrates that a search connector's effective first-turn availability is highly dependent on state-dependent opportunity costs. Static association graphs that simply connect a held search Item to its targets overcount access; equally, a model that protects every duplicate Item can undercount physically executable high-urgency lines.

The policies intentionally isolate *feasibility*, not rational optimality. A future action evaluator should assign continuation value to protected resources and compare the expected payoff of the proposed search against the best use of each sacrificed card. This is particularly important for the singleton ACE SPEC and for extra Basics that might otherwise establish required attackers. The distinct search-output categories also need to be valued by the exact deck and matchup.
