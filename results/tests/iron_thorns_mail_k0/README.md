# Iron Thorns: K0-aware Trainers' Mail policy and exact Prize posterior

**Status:** Fixed-seed paired 300,000-valid-opener physical experiment plus exact posterior-computation regression. This compares restricted one-Mail **resource access** in two [legal English-print Aichi Iron Thorns deck variants](../../decks/iron_thorns_aichi_english/). It does not measure matches or optimize opponent interactions.

## Why K0 policy is consequential

The preceding [one-Mail experiment](../iron_thorns_mail_frontier/) allowed a perfect-information observer to view the four Mail cards and all hidden Prize locations before deciding whether to play Mail at all. In paper play, observing Mail's four cards requires **playing that Item first**. If a player holds exactly two eligible discard cards and plays one of them as Mail, Guzma & Hala can no longer pay its optional two-card cost for Double Colorless Energy.

The relevant decision is made before the first full-deck search, while the player is in **K0**. This study separates pre-commitment from the later choice of a revealed Trainer.

## Mechanically constrained policies

All policies retain the previous exact resource definition and hypothetical 12 safe cards: four Trainers' Mail, four Crushing Hammer, two Enhanced Hammer and two Camping Gear. The named setup needs Thunder Mountain ◇ plus DCE, optionally routed via Guzma & Hala / Tag Call; an unavailable attack can pivot to Tropical Beach. One Iron Thorns ex begins Active. Only one Mail can be played.

1. **No Mail:** previous strict attack-versus-Beach endpoint using the physical hand, Prizes and deck.
2. **Always Mail (K0):** play a held Mail on any hand not already guaranteed to attack by holding DCE plus Thunder Mountain. Select a revealed target using exact K0 posterior probabilities.
3. **Preserve payment (K0):** same policy, but decline Mail if **DCE is missing, exactly two acceptable discards remain, and G&H or Tag Call is held**. This prevents using a needed discard as Mail. This decision uses the hand alone, before seeing the Mail reveal.
4. **Oracle upper envelope:** preceding restricted study's best of skipping Mail and retrieving one named target with hidden Prizes/deck known in advance.

After playing Mail, both K0 policies can select **one of Thunder Mountain, G&H, Tag Call or Tropical Beach** if revealed, or take no card. They can never select DCE or another Mail. Their choice maximizes the posterior expectation of attack access first, with Beach fallback as tie-breaker. The policy knows the 60-card deck composition, its current hand, the Active Iron Thorns, and Mail's four revealed cards. It does not see the six hidden Prize cards.

## Exact posterior calculation

Given seven original opening cards, one natural draw and four revealed Mail cards, **48 physical cards remain unobserved**: six Prizes plus 42 others in the deck. Every set of six among those 48 is equally likely to be Prized.

The relevant hidden events are whether all unseen copies of G&H, Thunder Mountain, DCE or Tropical Beach have been Prized. For a subset S of those categories with a total of r unseen physical copies, the numerator of the probability all copies in S are Prized is

\[
\binom{48-r}{6-r},
\]

with denominator \(\binom{48}{6}\), and zero probability when \(r>6\). Four-category inclusion-exclusion recovers the exact distribution of all 16 unavailable/available patterns. Each candidate Mail selection is then evaluated under the strict G&H discard rule. The [independent test](reproduce.py) recomputes the same decision by enumerating actual multivariate hypergeometric Prize counts, without the inclusion-exclusion shortcut.

## Physical experiment

- Same 60 cards as the prior [2 DCE / 1 Beach](../../decks/iron_thorns_aichi_english/) and [1 DCE / 2 Beach](../../decks/iron_thorns_aichi_beach/) validated variants.
- Seven-card Basic-valid opening, one Iron Thorns promoted to Active, six hidden Prizes, one natural going-second draw and potential Mail top-four reveal.
- RNG seed **20261014**; 300,000 accepted hands per list, using paired physical positions; 747,957 candidate openings.
- No opponent mulligan bonus, other Item chains, damage, opponent turn, Beach's subsequent draw, hand optimization beyond the named lines, or match-win outcomes.

## Results

| Endpoint (% of Basic-valid starts) | 2 DCE / 1 Beach | 1 DCE / 2 Beach |
| --- | ---: | ---: |
| Attack, no Mail | 20.910667% | 16.275333% |
| Attack, **always Mail K0** | 19.364333% | 14.009000% |
| Attack, **payment-preserving K0** | **24.179000%** | **18.736000%** |
| Attack, clairvoyant restricted oracle | **24.179000%** | **18.736000%** |
| Beach fallback, payment-preserving K0 | 31.066667% | 44.978000% |
| Beach fallback, clairvoyant oracle | 31.069000% | 44.982333% |
| Initially available attack lost by always playing Mail | 4.814667 points | 4.727000 points |
| Initially available attack lost by payment-preserving policy | **0** | **0** |

The always-play policy also rescues **3.268333** or **2.460667** attack-percentage points through Mail, but sacrifices more previously payable setup states. Its net attack access consequently declines. The payment-preserving policy obtains the sampled oracle's complete attack improvement while avoiding that damage.

The absolute fallback gap from the oracle is tiny: **7 out of 300,000** states for two DCE, and **13 out of 300,000** for two Beach. These small differences arise in fallback resource contention and are not evidence of a matchup-strength advantage.

## Structural reason attack access matches the oracle

There is a case-based result for this particular restricted action menu.

If the baseline can attack with both DCE and Thunder Mountain held, playing Mail is unnecessary. If DCE is held and Mountain must be obtained, no optional two-card G&H payment is required, so playing Mail cannot disable that route. If DCE is missing, any successful baseline paid-search route needs both an existing G&H/Tag Call access and two acceptable held discards. When exactly two exist, preserving Mail retains that route; when at least three exist, playing one leaves the required two.

For **new** attack access obtained by Mail, the named cases are narrower. With DCE held, retrieving a revealed Thunder Mountain directly guarantees the package, and taking revealed G&H dominates taking Tag Call where both could supply the same route. With DCE missing, Mail cannot fetch the Energy, so the only useful new source is G&H or Tag Call, with G&H dominating Tag Call if both are revealed. These dominance relations are visible from the hand and Mail's reveal; hidden Prize information does not change their direction. Thus the payment-preserving K0 rule and the posterior target policy have a structural explanation for matching oracle **attack availability** in the defined model.

This reasoning does not apply to expanded actions involving additional Trainers, recovery, other costs, future turns or opponent-dependent card value. The small fallback gap also shows that attack equality does not imply full policy equivalence.

## Reproduction

- [K0 and inclusion-exclusion policy](../../../tools/iron_thorns_mail_k0.py)
- [Prior physical resource model](../../../tools/iron_thorns_mail_frontier.py)
- [Single runnable regression](reproduce.py), checking all paired fixed-seed counts, a physically conserved two-discard counterexample and independent exact-posterior choices
- [Windows CI](../../../.github/workflows/validate-iron-thorns-mail-k0.yml)

Use \`python -m results.tests.iron_thorns_mail_k0.reproduce\` from repo root. Standard Python 3.12 only.

**Next:** replace the attack-first lexicographic preference with opponent-dependent utility and explicit Beach draw continuation, retaining information-appropriate timing. Do not treat the percentages above as demonstrated win probabilities.
