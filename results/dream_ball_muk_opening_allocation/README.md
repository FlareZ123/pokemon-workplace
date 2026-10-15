# Dream Ball / Alolan Muk: exact opening-Prize allocation

## Question and scope

What fraction of uniformly shuffled starting hands and Prize layouts could support Dream Ball putting Alolan Muk directly onto the Bench?

The existing [Dream Ball Bench transaction](../dream_ball_typed_bench_execution/) proves that a Stage 1 Muk may enter play from the deck after Dream Ball is taken as a face-down Prize. The [lock-interaction regression](../ability_lock_muk_thorns_precedence/) shows how Muk can suppress Active Iron Thorns ex's Initialization. This report measures only a static prerequisite of that line.

## Model

Consider a hypothetical 60-card list containing **14 Basic Pokémon**, **one Alolan Muk**, and D Dream Balls (one to four). The curated Aichi 2026 Shadow Rider champion has 14 Basics, although its actual list contains neither Muk nor Dream Ball. Adding either card would require removing other cards. This hypothetical does not propose a playable 60.

Deal a seven-card initial hand, then six Prizes uniformly without replacement. Require (a) at least one Basic in the initial hand, (b) Muk in the deck after dealing the six Prizes, and (c) at least one Dream Ball among the **first k randomly awarded Prizes**. The k awarded cards are a uniform k-subset of those six Prizes, not a player-selected known-Prize policy.

For N=60, B=14, H=7, P=6, let b be Basics and d be Dream Balls in the opening hand. With C(n,r) denoting a binomial coefficient, the joint event probability is the sum over b>=1, d>=0 of

C(B,b) C(D,d) C(N-B-D-1,H-b-d) / C(N,H) × (N-H-P)/(N-H) × [1-C(N-H-1-D+d,k)/C(N-H-1,k)].

Divide by the Basic-valid opening probability 1-C(N-B,H)/C(N,H) for conditional figures.

## Exact outcomes

Initial opening-seven Basic validity is **86.140932%**. The table reports probability of this allocation event conditional on a valid opening seven.

| Dream Balls | First random Prize | First 2 random Prizes | First 3 random Prizes | All 6 random Prizes |
| ---: | ---: | ---: | ---: | ---: |
| 1 | 1.344856% | 2.689713% | 4.034569% | 8.069139% |
| 2 | 2.689713% | 5.332756% | 7.929128% | 15.438224% |
| 3 | 4.034569% | 7.929128% | 11.686148% | 22.156695% |
| 4 | 5.379426% | 10.478830% | 15.308101% | 28.271322% |

The unconditional single-Dream-Ball / first-Prize rate is 1.158472% of all dealt opening configurations.

## Validation

- Exact Fraction combinatorial implementation: [tools/dream_ball_muk_opening_allocation.py](../../tools/dream_ball_muk_opening_allocation.py).
- [Single runnable regression](reproduce.py) compares the formula against independent exhaustive labeled-card enumeration in three tiny decks (10, 12, and 11 cards respectively) and asserts representative 60-card values.

## Limits and interpretation

This is an **opening allocation probability**, rather than a match-win probability, observed line frequency, or general bound on later-turn play. It has no mulligan bonus cards, extra draws, search, Bench-space constraints, targeted Prize selection after K1 deck inspection, Prize manipulation, recovery, timing of Knock Outs, or opponent actions. These omissions can increase or decrease actual line feasibility. The table does not show that Muk is accessible on a useful turn, even when all six initial Prizes are eventually taken.

One Dream Ball's first random Prize has a low static prerequisite rate before other costs are considered. A serious deck-building recommendation needs a complete legal 60, direct counterplay and matchup testing, and comparison against more accessible responses to Iron Thorns.
