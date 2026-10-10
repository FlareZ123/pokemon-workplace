# Regidrago's Budew history-cover bottleneck: board promotion and exact inventory baselines

## Question

After Regidrago VSTAR declares `Apex Dragon -> Timeless-GX`, it receives a bonus turn. If it switches to Budew and attacks with `Itchy Pollen`, the opponent's Mimikyu cannot use Copycat to select the older Apex Dragon declaration. The canonical semantics were established in [the attack-history investigation](../regidrago_attack_history_evasion/README.md).

How plausible is the *physical promotion* to Budew on the bonus turn? This result separates the **card-presence opportunity** from actually executing the line.

## Empirical inputs

Nine published top-32 CL Aichi Open League (May 2026) Regidrago decklists were transcribed and checked at the following sources:

- 10th: https://limitlesstcg.com/decks/list/26816
- 12th: https://limitlesstcg.com/decks/list/26818
- 13th: https://limitlesstcg.com/decks/list/26819
- 14th: https://limitlesstcg.com/decks/list/26820
- 18th: https://limitlesstcg.com/decks/list/27424
- 20th: https://limitlesstcg.com/decks/list/27425
- 21st: https://limitlesstcg.com/decks/list/27426
- 27th: https://limitlesstcg.com/decks/list/27427
- 32nd: https://limitlesstcg.com/decks/list/27428

All 9 carry Budew, Guzma, and Latias ex. Across the nine: **12 Budew**, **19 Guzma**, **3 Prime Catcher**, and **9 Latias ex**. Only places 10, 18, and 27 include Prime Catcher. Each deck has 2–3 Guzma.

The nine lists do not include Switch, Escape Rope, Float Stone, or Jet Energy. This is a decklist observation, not a statement that those are the only possible switching effects or that these lists lack other conditional interactions.

`aichi9_counts.json` preserves the per-list counts for the cards directly evaluated.

## Rules-driven promotion geometry

- **Regidrago VSTAR has three Colorless Retreat Cost.** When it is the Active attacker after Apex Dragon, manual retreat must pay that cost, unless modified by another effect. Paying it can consume Energy needed to attack again. For example, with exactly Double Dragon Energy (providing two Energy) plus one relevant Basic Energy attached, retreat can discard both attached Energy cards.
- **Latias ex's Skyliner applies to Basic Pokémon.** It cannot make an evolved Regidrago VSTAR retreat for free. Although one Latias ex appears in all nine lists, do not count it as free retreat for the incumbent VSTAR.
- **Guzma requires the opponent to have a Benched Pokémon to satisfy its first switching clause.** Only if that succeeds does it switch one's own Active Pokémon with a Benched Pokémon. It occupies the turn's Supporter channel.
- **Prime Catcher has the analogous opponent-Bench condition**, with the advantage of being an Item. Three of the nine lists carry one.
- Budew must be on one's Bench before either effect can promote it. The Bench must have room to stage it, unless it was already there. Search Item access, discard payments, opponent's Bench, Item lock, and Supporter contention must be independently satisfied.

This gives a sharp **counterexample to counting Latias as a generic zero-cost escape**. Its favorable Basic-Pokémon mobility does not transfer to Regidrago VSTAR after evolution.

Relevant raw card entries in `resources/cards/en/`: `swsh12-136`, `sv8-76`, `sm3-115`, `sv5-157`, `xy6-97`, and `sv8pt5-4`. The rulebook's sections A-03, B-03, C-10 and D-10 govern retreat and Supporter execution; individual card text supplies the conditions.

## Exact, deliberately simplified probability experiment

The baseline abstracts `n` randomly observed and *retained* cards from an unconditioned 60-card list, then deals six Prize cards uniformly from the remaining 60 − n. It does **not** simulate how a Regidrago VSTAR reached the Active Spot. The abstract sample is not a literal opening hand or a forecast for a particular bonus turn.

Let `b` be Budew copies; `q` the combined count of Quick Ball, Nest Ball, and Net Ball; and `s` the combined count of Guzma and Prime Catcher. These card types are disjoint for counting.

- **Direct inventory pair:** a Budew and at least one Guzma/Prime Catcher occur among the `n` seen cards.
- **Search-assisted inventory pair:** at least one switch card is seen and either Budew itself is seen, or a named Basic/Grass search Item is seen and at least one Budew remains outside Prize cards.

The second event models **availability of card names**. It deliberately grants free discard fodder to Quick Ball, treats Bench capacity and Item locks as permissive, ignores Supporter contention, assumes the relevant card is still available to play, and requires an opposing Benched Pokémon for the eventual switch. It excludes VS Seeker, Tapu Lele-GX, draw engines, Battle VIP Pass pre-staging, other access effects, and retreat as additional routes. Thus these probabilities are **neither gameplay success estimates nor mathematically guaranteed bounds** on real turn readiness.

The direct event has closed form:

`1 - C(60-b,n)/C(60,n) - C(60-s,n)/C(60,n) + C(60-b-s,n)/C(60,n)`.

The search-assisted event is computed exactly by partitioning the seen cards into Budew/search/switch/other and conditioning on the disjoint six-card Prize set. A 10-card toy deck is exhaustively enumerated as an **independent oracle** for the implementation.

### Results: unconditioned inventory benchmark

| Abstract seen cards `n` | Mean direct pair across 9 lists | Mean search-assisted pair across 9 lists |
| ---: | ---: | ---: |
| 7 | 3.4915% | 10.8406% |
| 12 | 10.0042% | 26.3182% |
| 18 | 20.7064% | 45.1062% |

Equal-weight across the nine lists, not tournament-weighted. At `n=12`, direct rates range from **6.8147% to 17.0798%**, and search-assisted from **19.1219% to 32.9232%**.

The search-assisted event becomes materially more common than the strict direct pair. The difference is a property of the sampled card inventory and the specified connector pool, rather than a proven gain in executable lines.

### Prize distinction

A singleton Budew is among the initial six Prize cards with 10% probability. For two Budew copies, **both** are Prized with exact probability 1/118 = 0.847458%. Search-assisted inventory conditions must account for this: observing Quick Ball without Budew does not establish that a searchable Budew remains in the deck. The exact code explicitly integrates that collision.

## Reproduction

Run `python results/regidrago_budew_promotion_baselines/reproduce.py` from the repository root. Only Python standard-library modules are used.

The reproduction validates the nine deck rows, checks exact Prize probabilities, and independently checks the joint sample-plus-Prize formula against exhaustive partitions of a smaller toy deck.

Files:
- `aichi9_counts.json`: card count fixture with list URLs.
- `reproduce.py`: exact Fraction-based computation and oracle.

## Strategic implications and limitations

**Verified:** All observed lists contain two or more Guzma. Most lack Prime Catcher, and all rely on a retreat cost that is nonzero for Regidrago VSTAR even when Latias ex is active. The proposed zero-Energy Budew cover still has a potentially expensive and opponent-dependent promotion requirement.

**Mathematically verified under the stated abstraction:** The quoted inventory rates and Prize probabilities.

**Not established:** probability of actually executing the cover in a game; probability that Item lock is strategically preferable to another Apex Dragon; relative value of retaining an energized VSTAR versus accepting Mimikyu's response; any causal tournament win-rate effect.

The next meaningful upgrade is a conditioned post-Timeless game-state model: place a VSTAR in Active with attached Energy, Budew's true zone, remaining Switch/Guzma access, known Prize information, opponent Bench geometry, live Item lock, and current Supporter usage. Separating `can reach Budew` from `can promote and attack` is essential to avoid mistaking static access for AMR.
