# Redeemable Ticket stopping policy with repeated Prize reinspection

## Question

Does a second or third Redeemable Ticket increase the probability that a blocked deck-search payload becomes searchable, after a player has already learned the original Prize composition? How much does learning the new Prize composition after each reset matter?

**Result:** with a known initial state, repeating blind Ticket resets has the *same marginal terminal success probability* as a single Ticket. If the player can re-inspect Prizes after each reset and stop immediately on success, the later Tickets can increase the probability sharply. This difference follows from the no-shuffle, bottom-of-deck nature of Ticket's effect. It is an **access-and-information upper bound**, not a deck recommendation.

Implementation: [`tools/prize_ticket_reinspection.py`](../../tools/prize_ticket_reinspection.py). Independent exhaustive regression: [`reproduce.py`](reproduce.py).

## Card-text basis and valid action window

The bundled Expanded card pool includes:

- **Redeemable Ticket** `sv9-156`: "Count your Prize cards, shuffle them, and put them on the bottom of your deck. Then, take that many cards from the top of your deck and put them face down as your Prize cards."
- **Town Map** `xy8-150` and `bw7-136`: "Turn all of your Prize cards face up. (Those Prize cards remain face up for the rest of the game.)"

Both are Items. An initial deck search can establish exact Prize *composition* using known deck contents. That search shuffles the deck, which is permitted **before** the first reset; the model begins with a uniformly random remaining deck. Each new Prize set is face down. Playing another Town Map after each Ticket exposes its composition without changing the deck order. This makes the inspection assumptions physically interpretable, **conditional on having the necessary Item copies and no relevant Item lock**. A *new ordinary deck search between Tickets* would shuffle the deck and invalidate the disjoint-block proof below.

## Exact state and proof

Let the current deck contain `D` cards, the current Prize zone contain `P` cards, and the original Prize composition be known. Target groups are distinguished by their number of cards initially in the deck `d_i`, their number initially Prized `o_i`, and how many must be in the deck for the intended next search to work `r_i`.

Without interleaved draws, shuffles, transfers, or other deck mutations, the first Ticket places original Prizes at the bottom, and replaces them with the first `P` cards from the original deck. The next Ticket places that new Prize block at the bottom, and replaces it with the *next* `P` original deck cards. For any number `k` of consecutive resets satisfying `kP <= D`, the `k`-th new Prize set is a disjoint `P`-card block `B_k` of the original random deck. Cards in the original Prize zone and earlier replacement blocks are in the deck again.

After reset `k`, the next search is available exactly when

`d_i + o_i - B_{k,i} >= r_i` for every target group `i`.

Each individual block `B_k` has the same hypergeometric marginal distribution. Therefore **choosing in advance to perform any fixed positive number of blind Tickets cannot improve the final success probability** compared with performing just one, for this fixed objective and reset window. This is a statement about final marginal success, not about line-by-line or information utility.

If instead each new Prize composition can be observed and the player can stop at the first successful state, the success-by-`k` probability is

`P(exists j in {1,...,k} such that d_i + o_i - B_{j,i} >= r_i for all i)`.

The reproducer evaluates this probability exactly by a dynamic program over multivariate-hypergeometric draws without replacement, retaining only prefixes in which every previous reset failed. The expected Ticket consumption under that policy is the sum of the prefix-failure probabilities before each allowed reset.

## Three-singleton numerical witness

Consider a conditional game state with **47 cards in deck, six current Prizes, and three individually necessary singleton payloads**. `A` is in the original Prizes, while `B` and `C` are in the deck. All three must be searchable *from the deck*, so the original state fails. Apart from these cards, the deck has 45 irrelevant cards. A successful Ticket returns `A` from the original Prizes to the deck, but can put `B` or `C` into the replacement Prize set.

| Maximum Tickets with reinspection | Probability all three searchable | Expected Tickets spent |
| ---: | ---: | ---: |
| 0 | 0% | 0 |
| 1 | 75.855689177% | 1.000000000 |
| 2 | 96.669750231% | 1.241443108 |
| 3 | 100.000000000% | 1.274745606 |

The first success probability is `C(45,6) / C(47,6) = 820/1081`. Both first and second resets fail only if `B` and `C` occupy different replacement blocks, yielding `P(fail twice) = 2*6^2/(47*46) = 36/1081`, so success by two is `1045/1081`.

Three different replacement blocks cannot *all* contain at least one of only two distinct at-risk original-deck singletons. Therefore success by the third reset is certain. Under **blind** execution of any fixed one, two, or three Tickets, terminal success stays at **75.855689177%**.

More generally, if a state is initially blocked solely by targets in old Prizes and has `m` vulnerable physical target cards still in the original deck, any `m+1` **disjoint** replacement blocks must include at least one block containing none of those `m` cards. A reinspection-and-stop policy therefore guarantees success by `m+1` Tickets when `(m+1)P <= D` and all required target cards are located either in the old Prizes or original deck. This is a conservative sufficient condition; fewer Tickets may suffice.


## Natural Item-access feasibility under the exact witness

The stopping-policy calculation assumes the necessary Tickets and non-shuffling reinspection actions are playable. To quantify one access bottleneck, [\`tools/prize_ticket_natural_access.py\`](../../tools/prize_ticket_natural_access.py) now computes exact **natural opening-and-one-draw access**, conditional on the same K1-style singleton-zone witness. A three-Ticket stopping policy needs **two** inter-reset Town Maps; inspection after the final reset is unnecessary because no further decision is made.

Illustrative 60-card composition: **14 ordinary Basic starters, four Tickets, four Town Maps, A/B/C as non-Basic singletons, and 35 other cards**. Condition on a legal starter-containing seven-card hand; set six Prizes; draw one card. The witness requires A in the initial Prizes and B/C still in the deck *after* that draw. The state has probability **6.166421481%** among valid openings before assuming any search access.

| Natural Item package available in opening plus draw | P(access \| exact singleton-zone witness) | P(witness and access \| valid opening) |
| --- | ---: | ---: |
| ≥1 Ticket | 45.011963876% | 2.775627410% |
| ≥2 Tickets, ≥1 Town Map | 3.035978791% | 0.187211248% |
| ≥3 Tickets, ≥2 Town Maps | 0.018720640% | 0.001154394% |

These are exact enumeration results, not Monte Carlo estimates. They show how an impressive **conditional** three-reset success guarantee can have very small immediate **unconditional** relevance if every required Item must be naturally drawn in the same early window. They do not model finding Items through search or draw engines, obtaining the initial K1 observation, or the opportunity costs of four-of copies in a realistic deck.

The calculation exploits an exchangeability identity. Conditional on all three designated non-starter singletons being excluded from the opening, one being Prized, and the other two surviving in the deck after the later draw, the ordinary opening and later draw are distributed as an accepted 7-card hand plus a random card from the remaining **57 non-target cards**. Their Item composition can be enumerated without explicitly enumerating the middle six-Prize subset. The companion [\`access_reproduce.py\`](access_reproduce.py) confirms this identity against an independent, exhaustive 10-card enumeration of hand, Prize, and later draw zones.



## Composing Prize-reset policy with naturally accessible Items

The resource ceiling and Item-access layers can be combined exactly when the original deck-order randomness is independent of the Item-count observation after conditioning on the K1 witness. This independence holds in the specified uniform-shuffle, physical-identity setup and is independently checked on an exhaustive small deck.

Let \`S_j\` be successful searchability by reset \`j\` **if the needed Items are guaranteed**, with \`S_0=0\` in the witness. Let \`A_j\` be the nested event that at least \`j\` Tickets and \`j-1\` Town Maps appear naturally in the early hand and draw. Then the achievable first-turn success under a ceiling of \`k\` adaptive resets and free initial K1 observation is:

\`V_k = S_0 + Σ_{j=1..k} P(A_j | witness) * (S_j - S_{j-1})\`.

Exact results for the 47-card three-singleton witness and illustrative four-Ticket/four-Town-Map, 14-starter 60-card access composition:

| Policy Item ceiling | Searchability conditional on K1 witness and random Item access | Joint witness + successful searchability, among valid openings |
| --- | ---: | ---: |
| 1 Ticket | 34.144135410% | 2.105471301% |
| 2 Tickets + 1 Map | 34.776045889% | 2.144437564% |
| 3 Tickets + 2 Maps | 34.776669333% | 2.144476008% |

The **second** reset-and-inspection capability adds **0.631910479 percentage points within the witness**, or **0.038966264 percentage points** on the accepted-opening denominator. The **third** adds only **0.000623444 percentage points within the witness**, or **0.000038444 percentage points** on the accepted-opening denominator. These are narrowly scoped searchability gains: there is no credit for alternate card uses, attacks, or lock handling.

The adaptive first-turn stopping policy spends an exact expected **0.457456035 Tickets per witness state**, including the many witness states in which no Ticket is naturally accessible. Its expectation is below one because natural initial access is the main bottleneck.

Implementation: [\`tools/prize_ticket_policy_access.py\`](../../tools/prize_ticket_policy_access.py). Independent end-to-end physical-card enumeration: [\`policy_reproduce.py\`](policy_reproduce.py). The full small-game enumerator samples hand, original Prizes, ordinary draw, and remaining deck **order**. It agrees exactly with the factorized policy values and Ticket consumption.



## Intervening deck shuffles eliminate the disjoint-block guarantee

The 100% three-reset ceiling relies on the deck order **surviving unchanged between Ticket uses**. A realistic turn may shuffle the deck through another search or draw-engine operation between Tickets. That intervention makes a previously returned target eligible to be Prized again.

A second exact kernel, [\`tools/prize_ticket_shuffle_intervention.py\`](../../tools/prize_ticket_shuffle_intervention.py), considers a perfectly randomized **full deck shuffle between each consecutive Ticket**, keeping every other assumption of the original singleton witness unchanged. For this regime, the pair \`(target counts in deck, target counts in Prizes)\` becomes a sufficient state. Every Ticket selects a multivariate-hypergeometric replacement set from the current deck, returns all old Prizes to the deck, and the policy reinspects then stops upon success.

| Reset ceiling, assuming reinspection | No shuffle between Tickets | Full deck shuffle between Tickets |
| --- | ---: | ---: |
| 1 Ticket | 75.855689177% | 75.855689177% |
| 2 Tickets | 96.669750231% | 94.328409043% |
| 3 Tickets | 100.000000000% | 98.666563217% |

The two-reset loss from an intervening shuffle is **2.341341188 percentage points**. The three-reset no-shuffle guarantee disappears, with **1.333436783%** residual failure even after three resets under the reshuffled model. Expected Ticket consumption rises from **1.274745606** to **1.298159018** under a three-reset ceiling, because a reshuffle causes some repaired targets to reenter the Prize zone.

This is a **conditional comparison between two idealized sequencing regimes**. A shuffle can also provide valuable new search access or affect non-target outcomes, and these benefits are deliberately unvalued here. Under a concrete first-turn ALS, the correct decision compares the shuffle's access improvement against the changed Prize risk.

[\`shuffle_reproduce.py\`](shuffle_reproduce.py) validates the grouped rational Markov model against an independent exhaustive labeled-card transition enumerator on a six-card toy deck. All first-through-third reset probabilities and Ticket-use expectations agree exactly. These regressions run alongside the earlier tests in the shared GitHub Actions workflow.



## Blind repeated Tickets after shuffling can reduce searchability

There is another important policy distinction in the full-reshuffle regime: using a Ticket **without** reinspection may undo an earlier successful repair. The stop-on-success probability in the preceding table assumes the player learns the current Prize configuration between actions.

[\`tools/prize_ticket_shuffle_blind.py\`](../../tools/prize_ticket_shuffle_blind.py) instead commits to playing exactly \`k\` Tickets, fully shuffling the existing deck between every pair, without looking at the new Prize set. The original A-Prized, B/C-deck singleton state gives:

| Fixed blind Ticket uses | Final deck-searchability |
| ---: | ---: |
| 0 | 0.000000000% |
| 1 | **75.855689177%** |
| 2 | 68.341461564% |
| 3 | 69.329450806% |
| 4 | 69.203724824% |
| 5 | 69.219780502% |
| 10 | 69.217962886% |

**One fixed Ticket is optimal among 0–10** in this starting state. Playing a blind second Ticket after the first and an intervening shuffle lowers the searchability probability by **7.514227613 percentage points**, even though the second action successfully restores whichever cards were in the old Prize set.

### Why repeated blind shuffles approach a uniform Prize prior

Consider the physical set of \`D+P\` cards partitioned into deck \`D\` and Prizes \`P\`, without any other zone mutation. A Ticket followed by a full shuffle transitions the current Prize subset \`B\` to a replacement Prize subset \`B'\` drawn uniformly from the complementary deck. Its transition kernel is:

\`Pr(B' | B) = 1 / C(D,P)\` if \`B ∩ B' = ∅\`, and zero otherwise.

This random walk is symmetric and doubly stochastic over all \`P\`-card Prize subsets. Its uniform distribution is stationary. With 47 deck cards, six Prizes, and three distinguished singleton targets, the stationary probability that **all three** are in the deck is:

\`C(47,3) / C(53,3) = 16215 / 23426 = 69.217962947%\`.

The ten-reset exact Markov value differs from that stationary probability by less than one ten-millionth in probability units. The first Ticket is unusually attractive because it guarantees the initially Prized singleton A returns to the deck, but enough subsequent blind reshuffles remove that initial conditional advantage.

The distinction between shuffle regimes is precise: consecutive Ticket Prize sets cannot overlap, because the immediately preceding Prize set is outside the deck when the next Prize cards are chosen. With **no shuffle**, the first \`floor(D/P)\` Prize sets are mutually disjoint segments of the original fixed deck order. With full shuffles between uses, a Prize card may return to the Prize set after an intervening Ticket and shuffle.

[\`blind_shuffle_reproduce.py\`](blind_shuffle_reproduce.py) independently enumerates the complete labeled physical-card transition tree and matches the grouped rational Markov model for each of the first four fixed resets. It checks convergence against the independent exact stationary formula.

**Strategic consequence:** when the player cannot observe the new Prize composition, a second Ticket and the shuffle needed to acquire it can make the target search problem harder. The correct policy may involve abstaining from additional reset attempts. Reinspection adds value by allowing the player to preserve successful states.


## Assumptions and practical limitations

- The model starts *after* an initial Prize-identifying observation and conditions on a particular known physical-zone composition. It does not estimate how often that state is reached from shuffled openings.
- Consecutive Tickets occur without ordinary draws, deck searches, shuffle effects, Prize-taking, or any other deck/Prize mutations; an initial shuffling search before Ticket is fine.
- The adaptive model presumes exact non-shuffling Prize reinspection after every reset. Town Map is a plausible Item source but costs slots, natural/card-search access, and playable action windows. The model deliberately does not charge these costs.
- At least `k` Tickets and the requisite information actions must be accessible, with no Item lock. There are copy limits and alternative uses for occupied deck slots. The extreme three-Ticket path is an upper-bound witness.
- This is a *deck-zone searchability* metric; it does not include attack success, evolution timing, Bench space, competing actions, locked abilities, or cards already removed from the deck into hand/discard/Lost Zone.
- Normal card-text precedence and any relevant format-specific bans must still be checked if turned into a real deck proposal. The cited print texts are drawn from the bundled card list.

## Validation

`results/prize_ticket_reinspection/reproduce.py` exhaustively enumerates all labeled orderings of two eight-card decks with two-Prize replacement blocks. It independently compares success-by-reset and expected action counts for both distinct-singleton targets and a repeated two-copy target group. An Aichi-sized 47-card, six-Prize case is checked against separate closed forms, including the blind-reset invariant and guaranteed three-reset success.

## Relation to existing research

- [`prize_zone_recovery/`](../prize_zone_recovery/) established the zone-typing and one-reset option values.
- [`aichi_post_gnh_prize_reset/`](../aichi_post_gnh_prize_reset/) estimated natural access and immediate opportunity costs for a *single* reset in a real ALS.
- [`prize_knowledge_nonmonotonic/`](../prize_knowledge_nonmonotonic/) showed that a reset can destroy exact Prize knowledge; this result isolates the value of reacquiring it.
- [`prize_effect_catalog/`](../prize_effect_catalog/) contains the relevant Ticket and Town Map operations.

## Next work

Combine a bounded number of actually playable Ticket and Town Map Items with their draw/search access, possible Item lock, and turn-window action costs. The strongest practical test would compare one Ticket against a second Ticket-plus-information package on real Aichi first-turn post-Guzma-&-Hala states and report *incremental endpoint value per occupied deck slot*.