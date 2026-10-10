# Early Beheeyem attack packet: adding Stage 1 plus Triple Acceleration Energy to the continuation frontier

## Question

Earlier results proved a significant optimization reversal among four Battle VIP Pass / Nest Ball / Buddy-Buddy Poffin slots when a Beheeyem control deck can either reserve a recycled-Elgyem tutor or preload a third Elgyem. See [third-Elgyem frontloading](../beheeyem_three_elgyem_frontload/) and [Poffin eligibility](../beheeyem_poffin_eligibility/).

Those access certificates did **not require any Beheeyem or Energy in the hand**. This study imposes an additional *independent card-access condition* to make the synthetic endpoint more informative: by the beginning of own turn two, the player must have at least one **Beheeyem Stage 1** and at least one **Triple Acceleration Energy** in hand, alongside the previously modeled board line.

Source prints from the bundled English card snapshot:

- `sm11-90` Elgyem is a 60-HP Basic.
- `sm11-91` Beheeyem evolves from Elgyem and uses **Mysterious Noise**, requiring three Colorless Energy, dealing 90 damage, shuffling itself plus attachments into deck, and restricting the opponent from playing Items from hand on their next turn.
- `sm10-190` Triple Acceleration Energy supplies three Colorless Energy to an Evolution Pokémon and is discarded at the end of the turn.
- `sv5-144` Buddy-Buddy Poffin fetches up to two Basic Pokémon of 70 HP or less and puts them directly on the Bench.
- `bw7-120` Lillipup is a 60-HP possible lock-anchor pre-evolution; a separate modeled regime has a partner Basic over 70 HP.

Rulebook A-05 forbids ordinary evolution on the first player's turn or on the turn the Basic was just put into play, and sections B-01/C govern ordinary Item and Energy timing. The access test selects an Elgyem as opening Active and allows a T2 evolution and TAE attachment if the required pieces are in hand.

## Exact experiment

Synthetic 60-card deck contains four Elgyem, four partner Basics, four Beheeyem, four Triple Acceleration Energy, four additional search-Item slots divided among VIP/Nest/Poffin, and 40 neutral cards.

A randomly dealt opening seven must contain an Elgyem selected Active; six random Prizes are set; the player takes a T1 natural draw. Search Items can stage the required Basics on T1, provided the Pokémon were not Prized. A further T2 natural draw may add the missing packet card or a reserved live Basic tutor.

The event requires:

1. **Either** (A) two Elgyem plus the partner Basic staged by T1, with an unused or T2-drawn Nest/Poffin to retain for a later recycled-Basic retrieval, **or** (B) three Elgyem plus the partner Basic staged by T1.
2. At least one Beheeyem and one TAE among the first eight drawn cards **plus the single natural T2 draw**, after the appropriate T1 Basic searches and deck shuffle.

The two paths overlap; only their union counts toward the headline event. If the T2 draw must supply the first live Basic tutor, that exact same draw cannot simultaneously supply a missing Stage 1 or Energy. This distinction is essential for accurately treating competing access channels.

No further draw, Stage1/Energy tutoring, repeated TAE access for later turns, multiple Beheeyem evolution supply, switch/retreat, anchor evolution, opponent, Prize exchange, or lock response is included. The result is a **constrained early card-access event**, not an executable full-turn attack probability or win rate.

## Conditional exact-factorization method

The older exact enumerator already counts opening-seven composition, T1 draw category, and six Prize composition for five categories: Elgyem, partner Basic, VIP, Nest, Poffin, and a neutral filler of `F` cards. Here Beheeyem and TAE are four physical copies of each, uniformly assigned within that filler.

Conditioned on `k` filler cards among the first eight seen, the exact probability that both required categories are represented is:

`q_F(k) = 1 - 2 * C(F-4,k)/C(F,k) + C(F-8,k)/C(F,k)`.

This is inclusion–exclusion for two disjoint four-card groups and directly accounts for their competition for hand slots. When T2 draws another filler card, the conditioned packet probability becomes `q_F(k+1)`; otherwise it stays `q_F(k)`.

A Prize count aggregated across VIP and filler does not reveal how many filler cards were Prized. Its conditional expected unprized filler count can be computed exactly by hypergeometric exchangeability, yielding the exact probability that the post-search T2 natural draw belongs to filler. This calculation preserves Prize depletion and the search-dependent deck size of `46 - searched Basics`.

For a reserve line that has a live tutor already in hand, condition on its T2 packet probability. For a line where the sole T2 draw must supply a tutor, multiply the tutor-draw probability by `q_F(k)` (packet already acquired in the first eight). The frontload line computes packet probability after its own number of searched Basics. If frontloading is reachable, that route is chosen for the union; otherwise the reserve route applies.

The program uses `fractions.Fraction` end-to-end, verifies the combinatorial sample space `C(60,7) * 53 * C(52,6)`, and scans all 15 four-Item allocations per HP-eligibility regime.

An **independent materialized 60-card Monte Carlo** (`monte_carlo.py`) includes literal `B` and `T` card identities, sets physical Prizes, consumes actual Basic search targets, reshuffles after searches, draws from the residual deck, and checks each event. Six representative configurations use 300,000 decks each and a fixed seed, with bounded sampling error.

## Main results for four Elgyem and four partner Basics

| Search-Item allocation | Partner ≤70 HP: union + packet | Partner >70 HP: union + packet |
| --- | ---: | ---: |
| 4 Buddy-Buddy Poffin | **1.438726%** | 0.846528% |
| 1 Battle VIP Pass + 3 Nest Ball | 0.632183% | 0.632183% |
| 4 Battle VIP Pass | 1.344844% | **1.344844%** |

The **eligible-partner optimum remains Poffin4**. The **ineligible-partner optimum remains VIP4** at four Elgyem. In the eligible regime, the earlier Basic-only union rate of 10.282682% drops to 1.438726% after the T2 Beheeyem/TAE hand-access condition. Only **13.9917%** of the earlier Basic-access events also satisfy this extra gate. For the high-HP VIP4 winner, 1.344844% versus Basic-only 9.637382% similarly represents **13.9545%** of that broader early-access event.

The reserve route with Poffin4 and eligible partner meets the packet condition in **0.562608%** of starts; the third-Elgyem frontload plus packet is **1.344844%**. Their union, correctly accounting for overlap, is 1.438726%. The first-turn two-Elgyem board staging probability is still 18.483546%.

## Redundancy sensitivity

Across Elgyem counts 3–4 and partner Basic counts 1–4, exact 16-configuration scans preserve the qualitative regime:

| Elgyem | Partner ≤70 HP | Partner >70 HP |
| ---: | --- | --- |
| 3 | Poffin4 is best at every tested partner count | VIP3/Poffin1 is best at every tested partner count |
| 4 | Poffin4 is best at every tested partner count | VIP4 is best at every tested partner count |

The packet condition drastically reduces absolute success incidence without changing these finite-scan winners. All results are specific to this synthetic deck class and first-two-turn draw policy.

## Reproduction and next steps

- `python results/beheeyem_turn_two_attack_packet/reproduce.py`: exact rates and selected maximizers.
- `python results/beheeyem_turn_two_attack_packet/monte_carlo.py`: six independently sampled materialized-deck checks.
- `python results/beheeyem_turn_two_attack_packet/robustness.py`: 16-case Basic-line redundancy scan.

Follow-up work should model guaranteed T2 evolution legality and **TAE attachment/expiration**, use extra Beheeyem and TAE copies or retrieval paths over subsequent turns, preserve Supporter contention, and account for retreat/active anchor behavior. The essential research lesson is that board-only access overstates even this modest multi-card setup condition.
