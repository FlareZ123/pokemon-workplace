# Harto Raichu: Giratina Active choice changes real-deck Item payability

## Deck-derived question

This is a concrete first-turn resource contention extension for **Harto Miki's 13th-place Champions League Aichi 2024 Raichu/Electrode deck**, documented and partially analyzed in [the earlier zone-aware Raichu result](../raichu_prize_access/). The published source is [Limitless deck 11221](https://limitlesstcg.com/decks/list/11221).

The actual list contributes:

- 16 eligible starting Basic Pokémon, including **one Giratina `sm8-97`** that can be useful to discard because of its Distortion Door Ability;
- 11 Special Energy cards that the deck can use in its discard-powered Electrode-GX plan;
- 3 Ultra Ball, each requiring two other hand cards discarded;
- 1 ACE SPEC Computer Search, also requiring two other hand cards discarded;
- 29 remaining cards, treated as strategically protected for this narrow test.

These six categories are **mutually exclusive except for Giratina's deliberate membership in both the starting-Basic and acceptable-discard roles**. The 29-card remainder includes other search and game-plan resources outside this model. The counts are an abstract projection of an actual published 60-card deck, rather than a newly recommended list.

The earlier Raichu component study established that an opening count model incorrectly treating Giratina as disjoint from setup starters would overestimate usable discard resources. Here, the exact *Active selection* is itself a decision variable.

## Two legal setup policies compared

Both policies condition on the opening seven cards containing at least one of the 16 Basics. They place exactly one Active Basic, choose six uniformly random Prize cards, then take the first natural turn draw going second.

- **Preserve Giratina:** if another Basic was initially available, make that other Basic Active; if Giratina is the only starting Basic, it must become Active.
- **Lead Giratina:** whenever Giratina appears in the opening seven, make it Active; otherwise choose another Basic.

The first policy keeps Giratina available in hand as a potential discard where possible. Neither is a general recommendation for positioning a Raichu/Electrode board: later attacks, Abilities, Bench configuration and matchup demands could rationally favor a different Active.

## Exact conditional event probabilities

The two discard-safe sources are the 11 Special Energy and Giratina *only if it remains in hand*. The Item sources are physically held Ultra Ball (three copies) and Computer Search (one copy).

| Event after normal first draw | Preserve Giratina | Lead Giratina |
| --- | ---: | ---: |
| At least one Ultra Ball or Computer Search held | 43.321231% | 43.321231% |
| At least two acceptable discard cards held | **48.619573%** | 44.169718% |
| Either held Item payable, preserving all other Items | **18.395823%** | **16.589294%** |
| Either payable, also allowing spare Ultra Ball copies | 20.153978% | 18.376491% |
| Either payable, allowing sacrifice of the other search source | 21.758531% | 20.019049% |
| Either payable, also allowing extra non-Active Basics as payment | 36.086944% | 36.086944% |
| Both distinct Items sequentially payable from safe cards alone | 0.034749% | 0.025528% |

**Choosing another Basic as Active where possible raises strict payable-source presence by 1.806529 percentage points.** This is a causal consequence within the modeled opening policy because choosing another Basic leaves Giratina in hand, increasing the number of possible payment cards when it is present alongside a different opener.

The held-Item presence probability is unchanged between the policies, since both remove one Basic as Active and neither removes Ultra Ball or Computer Search. The extra-Basics-allowed policy collapses the difference to zero: if every spare Basic is deemed discardable, choosing Giratina rather than another Basic merely exchanges one equally spendable hand card for another.

The previous zone-aware Raichu model's **48.619573%** two-discard pool payability is independently reproduced by this preserve-Giratina policy. The new **18.395823%** value is narrower: it also demands a physically held Ultra Ball or Computer Search. It still stops before determining whether the searched target exists in the deck or whether the target access is useful.

## Treatment of two-Item resource competition

For independent individual playability, one Item is reserved and must be paid with two distinct eligible other cards. The two-Item sequential event reserves *both* Ultra Ball and Computer Search and requires **four** eligible payment cards available in the same post-setup hand, without recycling any search output or new draw. Where multiple Ultra Ball copies are held, the spare-copy policy can consume the extras after reserving one Ultra and one Computer as sources. Because Computer Search is singleton, it has no same-source spare.

All sources and opportunity costs are different: Computer Search can search for any card, while Ultra Ball can only search for Pokémon. A deliberately protected Computer Search might still be sacrificed to pay Ultra Ball if the stronger connector is inaccessible or would lose to a lock. The state-dependent policy should be selected by anticipated continuation utility.

## Reproduction

The [source engine](../../tools/raichu_multi_search_gate.py) uses exact `Fraction` arithmetic to enumerate Basic-valid seven-card category histograms and the next natural draw. It explicitly accounts for Giratina moving into the Active Spot before computing discardable cards.

The [independent physical-card reproducer](reproduce.py) exhaustively enumerates labeled openings, all disjoint Prize placements, each first natural draw and both Active-choice policies in **six toy regressions**. It compares 18 event probabilities in each. Additional tests vary the Special Energy count over thirty hypothetical compositions, verify policy dominance and monotonicity, and compare the baseline discard-two gate against the earlier [Raichu prize-access model](../../tools/raichu_prize_access.py).

A [manually dispatched Windows CI workflow](../../.github/workflows/validate-agent2-raichu-multi-search-gate.yml) runs the tests. This model is an empirically grounded card-count projection of a real tournament list, with explicit heuristic discardability of Special Energy and Giratina. The outputs are opening resource-access events, **not full combo-setup probabilities or match win rates**.

## Next practical step

Compose this jointly held and payable Item menu with Raichu's zone-aware target and Gladion access. An optimizer must preserve the competing modes of Computer Search and decide whether using it or Ultra Ball advances the real Electrode-GX energy/attacker sequence. That extension should include the deck's Quick Ball and Forest Seal Stone lines before recommending a change to the published list.
