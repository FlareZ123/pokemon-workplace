# Third-place Aichi Snorlax Stall: Block starter versus Beach draw frontier

## Question

Does an English-format replacement for the Japanese-only Player's Ceremony improve the chance of starting with Active Snorlax Block if the replacement is a fourth Snorlax rather than a second Tropical Beach?

The project already has a 60-card English adaptation preserving 59 original source copies and adding a second Tropical Beach. A new [complete four-Snorlax alternative](../../decks/snorlax-stall-4block-english/) substitutes one Snorlax instead, retaining the source's single Tropical Beach, two Galarian Stunfisk, and every other original card.

The source placed third at the [10 May 2026 CL Aichi Open League](https://limitlesstcg.com/tournaments/566/decklists), but neither of these English adaptations has a tournament or match-win record.

## Model

Exhaustive hypergeometric combinatorics with a uniformly shuffled 60-card deck, a drawn opening seven, mandatory opening Basic validity, and six randomly placed Prize cards. A legal initial selection of Active Snorlax requires that at least one of the opening seven be Snorlax. Search cards, Supporters, attacks, later draws and adversarial play are outside this endpoint.

For `N=60`, opening hand `h=7`, Basic count `B`, Snorlax count `S`, and Beach count `T`:

- `P(valid) = 1 - C(N-B,h)/C(N,h)`
- `P(Snorlax | valid) = [1 - C(N-S,h)/C(N,h)] / P(valid)`
- `P(Beach | valid) = [1 - C(N-B,h)/C(N,h) - C(N-T,h)/C(N,h) + C(N-B-T,h)/C(N,h)] / P(valid)`
- Replace `B` with `S` in the inclusion-exclusion numerator above for `P(Snorlax and Beach | valid)`.

All-copy Prize risk for `k` specific printed copies is `C(60-k,6-k)/C(60,6)`, for `k<=6`. The code uses exact rational arithmetic until decimal display.

## Results

| Configuration | Basic valid | Snorlax given Basic-valid | Beach given Basic-valid | Both given Basic-valid |
| --- | ---: | ---: | ---: | ---: |
| 3 Snorlax, 2 Stunfisk, 2 Beach | 77.75788585% | 40.56560565% | 20.81998929% | 8.01672097% |
| 4 Snorlax, 2 Stunfisk, 1 Beach | 80.93533073% | 49.36035007% | 10.97963314% | 5.14041513% |
| Sensitivity only: 4 Snorlax, 1 Stunfisk, 2 Beach | 77.75788585% | 51.37737753% | 20.81998929% | 10.22821976% |

The published four-Snorlax candidate uses the **second** row. The third row is a sensitivity check, not an independently released alternate 60. It sacrifices Snap Trap redundancy to preserve draw-Stadium presence.

A single Beach has a 10% chance of being initially Prized, while two Beaches are simultaneously Prized with probability 0.84746%. This changes resource access even if searching is perfect once the player has inspected the deck.

## Verification and limitations

The [reproducer](reproduce.py) uses the original English adaptation manifest as its independent baseline and checks the candidate's sole substitution (one Beach to one Snorlax), printed card IDs, exact 60-card construction, all English eligible prints and the 12 versus 11 Basic starters through the repository's 12 October 2026 legality snapshot.

Full-game value remains unsettled. Tropical Beach can transform turns when stall deliberately avoids attacking and can remain relevant for many turns. Four Snorlax increases Block starting and recovery redundancy. A precise simulation must model opposing Switch, Guzma, Ability suppression, prize-access rescue, Supporter contention and the remaining draw engine before recommending a universally stronger deck.

The reproducible output is a structural access comparison, with **no demonstrated win-rate difference**.
