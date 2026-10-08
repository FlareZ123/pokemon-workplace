# Two-Tool access through Secret Box -> Guzma & Hala

## Question and rules

Secret Box (sv6-163) discards three other hand cards and fetches up to one Item, Tool, Supporter and Stadium. Guzma & Hala (sm12-193) searches a Stadium; after optionally discarding two other cards it can additionally search a Tool and a Special Energy. Both are marked Expanded legal in the local English card snapshot, subject to current regional, ban and release overlays.

Can a Secret Box Supporter output become a second Tool search, and how much starting discard stock does this composed route need?

Model: tools/secret_box_gnh_tool_pipeline.py.
Independent tests: results/secret_box_gnh_tool_pipeline/reproduce.py.

## Exact state-local model

One Secret Box is held and played first. Its payment discards three *other* cards. It may fetch up to one of each supported class. If a Supporter action remains, the player may play the fetched or already-held Guzma & Hala. That Supporter may spend two *other* cards to fetch a Tool and Special Energy, and it can also fetch a Stadium.

The goal is to have two different Tools A and B, one Stadium S and one Special Energy E in hand after payments. A variant additionally requires retaining Item I. Protected hand cards P are never used as payment; disposable D and any useful-but-replaceable cards can be spent. Search copies actually leave the deck and enter hand.

Canonical state: Box + one protected Basic + D in hand; one A, one B, one Guzma & Hala and one E in deck. Item I and Stadium S counts vary. All classes represent cards available in the searchable deck, excluding any Prize cards.

| Item copies | Stadium copies | Keep Item? | Minimum upfront D |
| ---: | ---: | :---: | ---: |
| 1 | 2 | No | **3** |
| 1 | 1 | No | **4** |
| 1 | 2 | Yes | **4** |
| 1 | 1 | Yes | **5** |
| 0 | 2 | No | **4** |
| 0 | 1 | No | **5** |
| 0 | 2 | Yes | Impossible |
| 1 | 0 | No | Impossible |

**Three-D witness:** Secret Box pays all three original D, obtains I+A+G+S. Guzma & Hala pays with the newly obtained Item and Stadium, then fetches B+E+another S. Final hand includes A+B+E+S. With one Stadium searchable, sacrificing it would destroy the Stadium end-goal; an additional original D must pay for Guzma & Hala instead.

**Reacquisition witness:** with only two original D but one G held, the Box can spend D+D+G and fetch a *second* G from the deck. The downstream sequence still succeeds. The same hand fails if no replacement G remains. This makes discardability continuation-dependent even for cards essential to the intended sequence.

## Exact initial-hand gate probabilities

These are *payment-stock probabilities*, not complete line success: condition on Box among the initial seven cards, with 12 protected Basic starters, 20 D, and 27 protected other cards among the other 59. Also condition that the other six cards include at least one starter.

For k initial D, calculate:

    P(D >= k | Box held, valid Basic start)
      = sum_{s>=1,d>=k,s+d<=6} C(12,s) C(20,d) C(27,6-s-d)
        / [C(59,6)-C(47,6)]

| Required D | Exact conditional probability |
| ---: | ---: |
| 3 | 26.688765798013% |
| 4 | 6.047797165848% |
| 5 | 0.542099465846% |

The three-D gate occurs 49.23223 times as often as the five-D gate in this abstract opening composition. This is **not** a 49-fold win-rate claim, since Prize availability and downstream execution are excluded.

## Validation

The category-count solver enumerates exact payment subsets and all legal Box/Guzma & Hala search choices. A separately written enumerator uses physically labeled individual card copies, independently selecting literal three-card and two-card payment sets and typed outputs.

The two solvers agreed in **1,536 states**, varying Item/Stadium availability, Tool and Supporter copies initially held, copies remaining searchable, Item preservation and Supporter permission. Regression fixtures pin all cost frontiers, the G reacquisition witness, and exact hypergeometric figures. No Monte Carlo sampling was used.

## Limits and next research

The endpoint is *acquisition in hand*. Playing a Stadium, attaching each Tool to an eligible Pokémon, Energy use, evolution, opposing locks, Prize randomization, alternative prior Supporter actions, and matchup-dependent utility are omitted. This Box-first model requires Item play permission and one Supporter play after Box, such as on the first turn going second. The box costs are paid literally; searched cards may fund downstream payments.

The next layer should compose this pipeline with physical Prize configurations and end-of-turn execution restrictions. Compare results/aichi_secret_box_output_dependencies/ for another concrete terminal objective where one immediate Secret Box category can drive a downstream multi-axis connector chain.
