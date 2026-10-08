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