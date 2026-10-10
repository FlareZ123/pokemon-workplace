# Opposing gust source access through accepted openings

## Question

The prior [stochastic opposing gust arrival](../stochastic_opposing_gust_arrival/) solver conditions on a single opposing Boss's Orders or Counter Catcher among unseen cards. Here we add a physical 60-card hand and six Prize cards. An opening hand is accepted only if it contains at least one Basic Pokémon. Our gust source is a non-Basic singleton; the other cards are B Basic Pokémon and generic fillers.

## Exact distribution

Write T=60, H=7, P=6. Define A=1-C(T-B,H)/C(T,H), the chance of a Basic-valid hand. Conditional on that acceptance, the singleton's chance of being in hand is

h = (H/T) [1-C(T-1-B,H-1)/C(T-1,H-1)] / A.

The singleton is Prized with probability (1-h)P/(T-H), or in the remaining deck with probability (1-h)(T-H-P)/(T-H).

For k natural opponent draws, k no greater than the 47-card post-Prize deck, its chance of being in hand or drawn is

Q(k) = h + (1-h)k/(T-H).

The early-access expression does not depend on the Prize count after averaging uniformly over Prize layouts. Prize placement still determines whether that source is inaccessible within the modeled draw process.

## Exact numerical results

All values below are percentages conditional on Basic-valid openings.

| Number of Basics | In opening hand | In Prizes | Accessible by first reply | Accessible by second reply |
| ---: | ---: | ---: | ---: | ---: |
| 4 | 10.4141 | 10.1418 | 12.1044 | 13.7947 |
| 8 | 10.7154 | 10.1077 | 12.4000 | 14.0846 |
| 12 | 10.9796 | 10.0778 | 12.6593 | 14.3389 |
| 16 | 11.1994 | 10.0529 | 12.8748 | 14.5503 |
| 20 | 11.3708 | 10.0335 | 13.0430 | 14.7153 |
| 24 | 11.4948 | 10.0195 | 13.1647 | 14.8347 |

Unconditioned 8/60 and 9/60 access estimates overstate these values. With four Basics, the overstatement is 1.2290 percentage points on the first reply and 1.2053 on the second.

## Exact tactical integration

The earlier first-reply Boss liability has modeled win probability 1-Q(1). The two-reply Boss/Counter liability, where the opponent may strategically pass, has modeled win probability 1-Q(2). For B=4 these are 87.8956% and 86.2053%. For B=16 they are 87.1252% and 85.4497%. These represent artificial one-hit-KO endgame states, rather than metagame win rates.

The [source tool](../../tools/opposing_gust_opening_access.py) combines held, Prized, and deck source cases using exact rational probabilities. The [reproducer](reproduce.py) exhaustively validates 18 ten-card toy populations across varying Basic count, Prize count and first/second draws, then verifies 60-card composition and tactical formulas. Run `python -m results.opposing_gust_opening_access.reproduce` at repository root.

## Scope

There is exactly one non-Basic gust source, uniform shuffling, Basic-valid opener conditioning, six hidden Prize cards and one natural draw per opponent reply. No extra mulligan draws, search, Prize recovery or draw engine is included. The downstream solver reveals initial source zone and subsequent draws to both players, a perfect-information relaxation that can overestimate our adaptive policy. Future work should retain private opposing source status, source-specific locks, turn quotas and real attack readiness.
