# One Trainers' Mail in two English Iron Thorns ex candidates

**Status:** Reproducible paired Monte Carlo of first-turn resource access. This is an optimistic restricted-line experiment and is **not** a game simulator, an empirical win-rate comparison, or a recommendation to replace the published Japanese 2026 Aichi list.

## Research question

Previous exact models compared two complete [paper Expanded legal English-print Iron Thorns ex adaptations](../../decks/iron_thorns_aichi_english/) of Kazuma Kashi's Aichi 2026 sixth-place deck:

- Speed: **2 Double Colorless Energy / 1 Tropical Beach**.
- Recovery: **1 Double Colorless Energy / 2 Tropical Beach** ([decklist](../../decks/iron_thorns_aichi_beach/)).

The previous [matched-cost exact calculation](../../decks/iron_thorns_aichi_beach/frontier.md) omitted Trainers' Mail effects despite the deck playing four copies. This study isolates **one Mail activation** and asks how often its top-four Trainer search can repair an otherwise failed named Thunder Mountain + DCE attack resource route or a failed Tropical Beach fallback.

## Card text and actual inventory

- Trainers' Mail (Roaring Skies 92) examines four cards and takes **one Trainer other than Trainers' Mail** into hand. Energy, including DCE, is not selectable. The other revealed cards return to the randomized deck.
- Guzma & Hala (Cosmic Eclipse 193) searches a Stadium; it may additionally search Special Energy and a Tool by discarding **two other hand cards**.
- Tag Call (Cosmic Eclipse 206) can find G&H in the deck. Thunder Mountain ◇ (Lost Thunder 191) discounts one Lightning from the attack cost of Iron Thorns ex's Lightning/Colorless/Colorless Volt Cyclone; DCE supplies the remaining two.
- Tropical Beach (Black Star Promo BW28) can be played as a Stadium and used to end the turn drawing to seven, with symmetrical access for the opponent.

Named categories in the complete 60-card paired decks: Iron Thorns 4; Tag Call 2; Guzma & Hala 2; Thunder Mountain 1; Mail 4; additional designated safe cards 8; DCE 2/1; Beach 1/2; residual protected cards 36. The eight hypothetical safe cards are four Crushing Hammer, two Enhanced Hammer and two Camping Gear. Together with **unplayed** Mail copies, these reproduce the prior **12-safe strict** discard hypothesis. The cards are not universally expendable in actual play.

## Model and rules boundary

1. Sample seven physical opening cards, conditioning on at least one Iron Thorns ex, which becomes Active. Deal six unobserved Prizes, draw the first going-second card, and reveal an ordered next four only if choosing to use Mail. No opponent mulligan bonus cards.
2. Check the previous strict attack-ready event: held DCE plus held/searchable Thunder Mountain through G&H/Tag Call, or G&H with two designated held discards for a needed DCE. A held Stadium plus Special Energy also meets the named resource package directly. The baseline has precedence over Tropical Beach.
3. If attack access fails, check whether Beach is held or accessible through G&H or Tag Call into G&H.
4. Under the **one-Mail extension**, compare skipping Mail against playing **one** held Mail. If played, exactly that Mail leaves the hand before evaluating G&H discard payability. Choose at most one of G&H, Tag Call, Thunder Mountain or Beach among the four revealed cards; the selected copy leaves the deck for hand. Re-evaluate attack and fallback and keep the lexicographically best outcome (attack > fallback > neither).
5. The Mail branch optimistically observes complete hidden Prize/deck allocation when making its selection. It is therefore a **perfect-information envelope for this restricted menu**, above what a real K0 decision policy necessarily accomplishes. No second Mail, draw Supporter, Speed Lightning draw, Item hand depletion, opponent decisions, Stadium replacement, extra draws from Beach or subsequent turns.

The physical experiment uses an identical random sequence of 18 labeled card positions for the two variants. The one-card DCE/Beach substitution is made in the same card slot. Fixed seed **20261014**; **300,000 Basic-valid starting hands** per variant and **747,957 attempted openings**. Each top-four search is from the actual Prize-excluded deck after the first natural draw.

## Results

| Basic-valid setup endpoint | 2 DCE / 1 Beach | 1 DCE / 2 Beach |
| --- | ---: | ---: |
| Prior strict attack, no Mail play | 20.910667% | 16.275333% |
| Prior failed attack, Beach fallback | 26.930333% | 39.532333% |
| Attack, with optimal one-Mail choice | **24.179000%** | **18.736000%** |
| Failed attack, Beach with one-Mail choice | 31.069000% | **44.982333%** |
| Newly gained attack cases | **3.268333 percentage points** | 2.460667 points |
| Newly gained Beach fallback cases | 4.480000 points | **5.919667 points** |
| Prior Beach cases promoted to attack | 0.341333 points | 0.469667 points |
| Initial hand contained Mail | 41.169000% | 41.169000% |

The attack and failed-attack Beach rows partition outcomes; there is no double counting. Newly gained fallback cases exclude formerly available fallback. The "promoted to attack" row records prior fallback states that became attack-accessible. Thus the net Beach change is smaller than the newly gained fallback column.

**Sampling precision:** The 95% normal Monte Carlo intervals for newly gained attack probability are approximately **3.205%–3.332%** (two DCE) and **2.405%–2.516%** (two Beach). These intervals quantify random sampling only; they do not account for model bias or opponent behavior.

The no-Mail attack/fallback rows agree within a predeclared **0.2 percentage point absolute tolerance** with the independent earlier exact grouped hypergeometric solver, which reported 20.953811% / 27.046351% and 16.293836% / 39.657754%, respectively. Those reference values are exact *for that restricted opening model*.

## Interpretation and next work

Trainers' Mail increases the modeled probability of satisfying the immediate resource or Beach fallback action, after charging the spent Mail as unavailable for G&H payment. The two-DCE build retains a higher **restricted attack-access** rate, while the two-Beach build retains higher **restricted Beach fallback** access. The gap is sensitive to what the first draw engines and disruption Supporters actually accomplish.

The result is deliberately silent on the number and value of cards drawn by Beach, on the opponent's Beach use, on activation when a rival Stadium is already present, and on actual match win probability. A valuable next model is a **K0 information-respecting** Mail selection policy followed by a two-turn continuation that accounts for Beach draw, Tool/Item payments and opposing Stadium/Ability locks. Such a model could meaningfully challenge the one-Mail oracle.

## Reproduction and validation

- Model: [tools/iron_thorns_mail_frontier.py](../../../tools/iron_thorns_mail_frontier.py).
- Runnable test: [reproduce.py](reproduce.py), with fixed-seed exact count checks, synthetic target and discard-payment regressions, and independent prior exact-baseline comparison.
- Windows runner: [validate-iron-thorns-mail-frontier.yml](../../../.github/workflows/validate-iron-thorns-mail-frontier.yml).

Run the module \`python -m results.tests.iron_thorns_mail_frontier.reproduce\` from repository root on Python 3.12. Uses only the standard library. Sample counts and the random seed appear in the test for direct reproduction.
