# Flexible single-use cards and joint-coverage overstatement

The coverage-class model in [multi_role_notes.md](multi_role_notes.md) allows one physical card to satisfy multiple strategic requirements simultaneously. This is appropriate only when the card's *one executable use* can actually fulfill all credited requirements. Many Expanded search and choice effects provide one output, so they need a capacity-one model.

## Exact two-demand result

Consider two requirements A and B, exclusive card counts a and b, and f interchangeable flexible physical cards. Every flexible card can satisfy either requirement, but at most one per physical copy. All target cards are non-Basic and separate from B ordinary Basic starters. Conditional on a legal H-card Basic opener, Prize positions are uniformly marginalized.

Let q(k,m) be the probability that none of a particular k-card target set occurs in the opener or m opponent bonus draws:

    q(k,m) = [C(N-k,H)-C(N-B-k,H)] / [C(N,H)-C(N-B,H)]
             * C(N-H-k,m) / C(N-H,m).

An ideal simultaneous-coverage model reports

    P_ideal(m) = 1 - q(a+f,m) - q(b+f,m) + q(a+b+f,m).

For one-use flexible cards, the ideal succeeds incorrectly precisely when the observed opening plus bonus contains exactly one flexible card, no A and no B. Its exact probability is

    gap(m) = f * [q(a+b+f-1,m) - q(a+b+f,m)].

Therefore

    P_one_use(m) = P_ideal(m) - gap(m).

This is a literal event decomposition. The f factor selects which single physical flexible card is present. The excluded sets for the other flexible copies and both exclusive families leave disjoint possible witnesses.

## Concrete opening benchmark

For N=60, H=7, six Prizes, twelve unrelated ordinary Basic starters and two requirements with four effective outs each, let f flexible cards replace f exclusive cards in *each* family, yielding a=b=4-f.

| f flexible copies | Distinct physical target cards | Ideal simultaneous completion | Actual one-use completion | Overstatement |
| ---: | ---: | ---: | ---: | ---: |
| 0 | 8 | 12.964829% | 12.964829% | 0 pp |
| 1 | 7 | 18.249957% | 12.343880% | 5.906077 pp |
| 2 | 6 | 24.156036% | 10.987230% | 13.168805 pp |

At f=2, nominally preserving four effective outs for each missing target while switching to versatile single-output cards **reduces** the joint feasible opening rate compared with eight exclusive cards. Ideal simultaneous coverage predicts the opposite.

The result isolates connector output capacity. It does not include whether a flexible card is affordable to play, whether its target remains in the searchable deck, Supporter contention, one-use ACE SPEC limits, Bench constraints, or future turn sequence. Those constraints can make the executable joint probability lower still.

## Evidence and implications

[tools/opponent_bonus_flexible_capacity.py](../../tools/opponent_bonus_flexible_capacity.py) implements the exact fractions. [flexible_capacity_reproduce.py](flexible_capacity_reproduce.py) independently enumerates labeled opening hands, Prize subsets and bonus selections for three small decks, including f=0, f=1 and f=2 cases. It checks the event-decomposition equality and representative 60-card outputs.

This clarifies the interpretation of the earlier coverage-class extension. A card carrying two role labels must mean a **simultaneous AND supplier**, while a flexible one-use search or choice is an **OR supplier** with one unit of output capacity. Conflating those semantics can reverse deck-construction conclusions.
