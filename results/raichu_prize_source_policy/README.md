# Raichu's exact prize-aware, source-specific discard-policy frontier

## A real deck, a concrete goal, and a surprising dominated route

This extends [Harto Miki's 2024 Aichi 13th-place Raichu/Electrode access study](../raichu_prize_access/) and the [dual-search payment gate](../raichu_multi_search_gate/) into one exact, prize-aware *Alolan Raichu into hand* endpoint.

The published [60-card tournament list](https://limitlesstcg.com/decks/list/11221) is represented by exact count categories: 1 singleton Alolan Raichu (non-Basic target), 2 Gladion, 3 Ultra Ball, 1 Computer Search (ACE SPEC), 1 Giratina discard-favorable Basic, 15 other starting Basics, 11 Special Energy discard-favorable nonstarters, 26 other protected cards. These classes sum to 60 without double-counting the Giratina role overlap.

The tested card interactions are:

- Ultra Ball costs two **other** cards discarded and can search the deck for the Stage 1 target if it is in the deck.
- Computer Search costs two **other** cards discarded and can search for any card. On inspecting the deck, it can find Raichu directly or, if Raichu is missing because it was Prized, search for Gladion.
- A held Gladion can retrieve a Prized singleton; when Computer Search obtains it and the ordinary Supporter play remains available, the same target access line can proceed.
- Giratina is a Basic Pokémon needed for setup if it is the only opener, yet its discard-pile Ability makes it a potential discard resource otherwise.

This models legal Basic-valid first-hand setup, exactly one Active choice, six face-down Prizes and the first normal draw going second, plus only the above one-item/one-Supporter line. Extra Pokémon access, Tools, Forest Seal Stone, other Supporters, Quick Ball, draw Abilities, Energy acceleration, actual evolution and attack use are omitted. The output is a conditional early resource-access event, not a match-winning probability.

## Four physically grounded source-payment policies

Each policy applies the same 2-card payment to a *specific selected Item source*, reserving that source card before counting other hand cards.

1. **Strict:** only the 11 Special Energy and held Giratina are acceptable payment.
2. **Spare Ultra:** additionally use surplus Ultra Ball copies to pay a played Ultra Ball. Preserve Computer Search.
3. **Computer may use Ultra:** also allow a played Computer Search to discard held Ultra Ball cards. Preserve Computer Search when playing Ultra Ball.
4. **Any source sacrifice:** additionally allow Ultra Ball to discard a held Computer Search, if its two-card cost can then be paid. This hypothetical expensive choice consumes the ACE SPEC.

All policies assume the **preserve-Giratina Active choice** by default (select a different Basic for Active when available). The opposite choice is also calculated.

## Exact probabilities of Alolan Raichu access

| Source-payment policy | Preserve Giratina Active policy | Lead Giratina whenever held |
| --- | ---: | ---: |
| Strict | **30.578700%** | 29.097533% |
| Spare Ultra | **31.975260%** | 30.520438% |
| Computer may use Ultra | **33.390969%** | 31.973613% |
| Any source sacrifice | **33.390969%** | 31.973613% |

With the conservative Active policy, the two source-aware changes increase the modeled exact target endpoint from **30.578700% to 33.390969%**, a gain of **2.812269 percentage points**. This gain reflects physically accessible payment routes for existing search sources. It does not imply that the required cards should actually be sacrificed in every state.

The unchanged final row is an instructive exact **connector-domination** result: allowing Ultra Ball to discard Computer Search can increase an *Ultra-only* target route, but cannot improve total target access beyond the already allowed Computer-Search-discarding-Ultra policy.

At the baseline, Ultra-plus-held-Gladion access rises from **28.360702% to 29.630284%** when Ultra can discard the singleton Computer Search. Total adaptive Ultra-or-Computer-plus-Gladion access remains identically **33.390969%**.

## Why sacrificing Computer Search to Ultra Ball is dominated here

Consider any hand where Ultra Ball can only pay its second discard by sacrificing Computer Search (while Computer Search itself remains held). Its payment comes from:

`safe cards + surplus Ultra copies + Computer Search >= 2`.

Computer Search can instead be used as the played source, with a held Ultra Ball providing payment:

`safe cards + all held Ultra copies >= 2`.

The latter is payable whenever the former newly becomes payable. With the same two source cards consumed, Computer Search can search for the same Pokémon as Ultra Ball, and it also has the adaptive Gladion route when the singleton is Prized. For this **one-step target objective**, all newly enabled Ultra Ball events are already covered by the paid Computer Search action. Therefore the incremental adaptive event mass is exactly zero.

This is a structural proof about the modeled goal and payment policies. It is not a general ranking of Ultra Ball versus Computer Search under all future-resource opportunity costs, card locks, source-specific restrictions, or competing action objectives.

## Exact hidden-Prize integration

The [exact engine](../../tools/raichu_prize_source_policy.py) uses an eight-category multivariate-hypergeometric distribution to condition on legal Basic starts and first draw. After the draw, the six Prizes occupy a uniformly chosen six-card subset of the remaining 52 unseen cards. The target is either held, in those six Prizes, or in the deck.

For a target absent from hand, `P(target Prized) = 6/52`. For Computer Search to retrieve Gladion once the target is known to be Prized, at least one remaining Gladion must not also be Prized. If `g` Gladion copies are among the other 51 unseen cards after conditioning on Raichu occupying one Prize, the probability at least one Gladion survives in deck is

\[
1-\frac{\binom{51-g}{5-g}}{\binom{51}{5}}
\]

for `0 <= g <= 2`, using zero for impossible binomial selections.

This conditional inventory is combined with the physical *source-specific* ability to pay Computer Search in the actual hand. No player is assumed to know Prize composition before initiating a legal search.

## Reproduction and crosschecks

The [independent labeled physical oracle](reproduce.py) enumerates actual initial hands, Active choice, all possible disjoint Prize sets, and natural draws, then directly tests the target/Gladion/source availability in each physical game state. It validates all **24** exact event probabilities across four source policies in three small decks and both Active-selection policies, for six complete toy regressions.

The *strict* full Harto baseline reproduces four earlier independently calculated quantities to floating precision:

| Metric | Exact fraction solver |
| --- | ---: |
| Raichu initially held | 12.874837% |
| Ultra + held Gladion target access | 26.964142% |
| Add nonadaptive Computer direct target access | 30.126094% |
| Add Computer adaptive Gladion fallback | **30.578700%** |

The tests also compare per-source paid actions with the new [Raichu dual-search gate](../raichu_multi_search_gate/) and establish that `computer_can_use_ultra_adaptive == any_source_adaptive` **exactly**, across both Active policies and multiple disposable-Energy counts. [Manual Windows CI](../../.github/workflows/validate-agent2-raichu-prize-source-policy.yml) runs the validation without any per-commit trigger.

## What this establishes

This is a concrete convergence of three earlier research themes: **K0→K1 Prize information**, **discard-cost AMR/DCI**, and **connector domination under competing alternative source uses**. It demonstrates that carrying exact physical costs and Prize zones through a real deck can change the target-access estimate without introducing any new copies or changing the printed deck.

Future work should assign continuation value to spent Special Energy, sacrificial Ultra Ball and Computer Search, then integrate Quick Ball/Forest Seal Stone and the Energy/Electrode-GX combo. A full deck swap should only be considered after those opportunity costs and matchup-specific lines are modeled.
