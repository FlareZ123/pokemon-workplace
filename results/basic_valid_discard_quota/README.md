# First-turn payability collapses as Item discard quotas increase

## Scope

The [one-discard Basic-valid Item gate](../basic_valid_item_payment_geometry/) is generalized to arbitrary integer additional-card discard quotas. The printed paper-Expanded card corpus provides three examples: **Quick Ball** swsh1-179 requires one other card discarded, **Ultra Ball** swsh9-150 requires two, and the ACE SPEC **Secret Box** sv6-163 requires three. All three are Expanded-legal in the supplied database; Secret Box is restricted to one ACE SPEC copy. The model records only presence and payability, with card-search output and future retained-resource costs excluded.

The constructed 60-card decks all contain 12 Basic starters and exactly F designated disposable filler cards, with other cards protected. The modeled Item's number of copies is Q=4 for Quick Ball and Ultra Ball and Q=1 for Secret Box; the protected remainder makes the total 60. The player goes second, draws an initial seven containing at least one Basic, places exactly one Basic Active, deals six Prizes and draws one normal card.

For source count Q and required additional discard cards m, compare three conditional hand gates:

- **Strict:** at least one source and at least m disposable filler cards F.
- **Spare-copy fallback:** at least one source and at least m cards among filler F plus the Q−1 excess sources held.
- **Extra-Basic fallback:** additionally allow Basic starters still in hand after putting one Active.

The extra-Basic fallback is a hypothetical DCI relaxation. It would often be strategically undesirable in an actual game, because extra Basics may be necessary to establish the Bench or evolution chain.

## Source-grounded exact example with F=8

| Item | Copies Q | Extra discard m | Physically held | Strictly payable | Spare-copy fallback | Extra-Basic fallback |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Quick Ball | 4 | 1 | 42.738824% | **27.619222%** | 30.693460% | 38.788363% |
| Ultra Ball | 4 | 2 | 42.738824% | **9.453070%** | 12.786962% | 26.718521% |
| Secret Box | 1 | 3 | 12.659263% | **0.453336%** | 0.453336% | 2.695779% |

Conditional on holding the source, **64.62%** of Quick Ball hands, **22.12%** of Ultra Ball hands, and **3.58%** of Secret Box hands satisfy the *strict* disposable-filler policy at F=8.

These values quantify the gap between theoretical Item presence and strategically acceptable discard payment. A singleton Secret Box can be in hand while the three additional disposable cards it needs are extremely unlikely in the same hand. Broad search reachability does not measure practical action realism.

## How availability changes with the disposable pool

Strict-payability percentages for F=4,8,12,20,28:

| F | Quick Ball | Ultra Ball | Secret Box |
| ---: | ---: | ---: | ---: |
| 4 | 16.753450% | 2.532121% | 0.039070% |
| 8 | 27.619222% | 9.453070% | 0.453336% |
| 12 | 34.389431% | 17.721156% | 1.461210% |
| 20 | 40.661646% | 31.877983% | 4.932276% |
| 28 | 42.391235% | 39.592885% | 8.818308% |

With B and Q fixed, increasing F simply reclassifies previously protected cards as acceptable payment, so strict-payability is mathematically nondecreasing. A coupling argument establishes this property, and exact regression checks every feasible F count for all three Item types.

A model based only on Item presence would ignore these very large differences. Likewise, a flat discardable fraction could overlook the fact that one source copy is consumed as the Item and cannot also count as its own payment.

## Exact implementation and verification

The [general discard-quota engine](../../tools/basic_valid_discard_quota.py) enumerates exact category counts in the Basic-valid initial hand, subtracts one Active Basic, marginalizes Prize placement and incorporates the following natural card draw. The code counts source copies separately from their additional discard payment and preserves the remaining protected-card class.

The [independent physical reproducer](reproduce.py) explicitly deals labeled card identities into openings, Prizes and the natural draw in **936** small-case parameter combinations, then checks the four exact source/payability probabilities. It also cross-validates every one-discard result against the earlier closed-form avoidance/inclusion-exclusion model. [Windows CI](../../.github/workflows/validate-agent2-basic-valid-discard-quota.yml) runs Python 3.13.

These calculations concern a constructed payment-resource class, not actual match frequencies or deck recommendations. Their practical role is to identify false-positive search edges in card-interaction graphs and motivate state-dependent discard-cost modeling before a simulated Item is assumed playable.
