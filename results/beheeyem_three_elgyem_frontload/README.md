# Turn-four Beheeyem continuity: recycled Basic search versus a preloaded third Elgyem

## Why the previous endpoint was incomplete

The [joint setup and reserved-Nest study](../beheeyem_joint_staging_reserve/) and the [Poffin eligibility crossover](../beheeyem_poffin_eligibility/) quantified a first-turn board with two Elgyem and a partner Basic, plus a live Nest Ball or Buddy-Buddy Poffin available by the beginning of own turn two. That live Item may be retained for own turn three, after a turn-two Beheeyem's Mysterious Noise shuffles its body into the deck, to re-Bench that returned Elgyem for an eventual turn-four evolution.

There is a different route: **pre-Bench three Elgyem on turn one**. With sufficient later Beheeyem evolution cards, Triple Acceleration Energy, and switching, those three mature Basics can support successive own-turn attackers on turns two, three, and four without needing to retrieve the first recycled Basic by own turn three. Evolution restrictions matter: an Elgyem fetched from the deck and newly Benched on turn three ordinarily cannot evolve during that same turn (Advanced Player's Rulebook A-05).

Earlier metrics only credited the recycled-Basic tutor route. This result enumerates the **union** of these two alternative Basic-access certificates. It remains a deliberately restricted *early access* study, not a proof that the three attacks can be executed.

## Exact model

The synthetic 60-card deck has four 60-HP `sm11-90` Elgyem, four partner Basics, exactly four search Item slots partitioned among Battle VIP Pass, Nest Ball, and Buddy-Buddy Poffin, and inert filler.

Open seven cards with Elgyem chosen Active; set six random Prizes; draw naturally once on own turn one and own turn two. The first-turn deadline requires the partner Basic and additional Elgyem to have been staged by that turn's end. Every searched Pokémon must actually be outside the Prize cards and available in the deck. The 70-HP-or-less predicate is applied to the exact partner print; Elgyem is always Poffin-eligible.

Two optional search-side continuation certificates are modeled:

- **Reserve route:** at least two Elgyem plus the partner Basic staged by turn one; an unspent Nest or Poffin in hand by the start of own turn two, which can be kept for turn-three use to Bench the recycled Basic.
- **Frontload route:** at least **three Elgyem** plus the partner Basic staged by turn one. The third early Basic can mature for a turn-four evolution without needing the turn-three recycled-Basic tutor.

The scored event is their union; overlapping hands count only once. Item sequencing is chosen to preserve live future tutors in the reserve branch, while a frontload branch may spend an additional tutor to reach its third Elgyem. Battle VIP Pass is turn-one-only. Poffin can obtain two Basics if each has 70 HP or less; when the partner is over 70 HP, Poffin can find Elgyem only.

This is a **necessary early search-capacity certificate for the specified two continuation routes**, conditional on a particular planned line. The model does not include turn-two Beheeyem, multiple evolution cards, Triple Acceleration Energy availability and recycling, ability lock, retreat/switch resources, opponents, other draw/search, or evolution/prize availability. It also excludes other recovery methods and naturally delayed alternative staging. Winning percentages must not be inferred from these access probabilities.

## Exact enumeration and independent validation

`reproduce.py` enumerates opening-hand categories, own-turn-one natural draw and six Prize counts, with integer combinatorial weights and exact rational probability. For a reserve branch, after searching missing Basics, the own-turn-two draw is sampled from the post-search deck of size `46 - missing Basics`. Counts across all opening/Prize/draw states conserve `C(60,7) * 53 * C(52,6)`.

`monte_carlo.py` independently shuffles physical 60-card decks, sets the six Prizes before the natural draw, checks actual deck-search supply, and shuffles the deck again after any search before drawing on turn two. It compares six representative configurations against exact values using 250,000 trials per case and seed 20261010.

## Results

| Four-Item package | Partner ≤70 HP: reserve route | Partner ≤70 HP: frontload | Partner ≤70 HP: either | Partner >70 HP: either |
| --- | ---: | ---: | ---: | ---: |
| 4 Poffin | 4.510096% | 9.637382% | **10.282682%** | 6.344508% |
| 1 VIP + 3 Nest | 3.181558% | 4.554281% | 5.020176% | 5.020176% |
| 4 VIP | 0.000000% | 9.637382% | 9.637382% | **9.637382%** |

All 15 four-Item splits were evaluated for both eligibility regimes; see the full emitted tables from the reproducer.

The best package **changes with the objective**. For eligible 60-HP Elgyem + 60-HP Lillipup, four Poffin remain uniquely optimal for the broader either-route event at **10.282682%**. The standalone frontload route already occurs in **9.637382%** of starts under this configuration; the reserve path contributes only **0.645300 additional percentage points** outside that set.

For a Poffin-ineligible partner Basic, the old reserve-only endpoint favored **VIP1/Nest3** (3.181558%). When the frontload alternative is admitted, **four VIP** uniquely maximize the either-route event at **9.637382%**, compared with **5.020176%** for VIP1/Nest3. This is a genuine objective-dependent ranking reversal within the synthetic model, caused by alternative available lines.

## Interpretation and next steps

A single mandatory search-resource assumption can distort deck optimization. Backup board topology matters: preparing an additional Basic can eliminate a future search deadline over the modeled horizon. Including a third Elgyem also introduces competing costs, especially evolution and Energy acquisition, which could reverse the mathematical preference when modeled.

A next useful experiment should combine these exact Basic-access states with literal turn-two, turn-three, and turn-four Beheeyem evolution/TAE search transitions, switching, Prize safety, and an opponent capable of disrupting the lock anchor. The current result provides a reproducible *necessary-condition component* for such a simulator.

To reproduce: `python results/beheeyem_three_elgyem_frontload/reproduce.py` and `python results/beheeyem_three_elgyem_frontload/monte_carlo.py`.
