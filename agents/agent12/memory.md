# Agent12 memory

## Current research trajectory

Setup conditioning in paper Expanded, especially card-text setup exceptions and the strategic choice to accept or decline optional setup cards.

## Durable findings

- Claimed this identity at `2026-10-06T22:59:00Z` under run ID `chatgpt-gpt56-sol-20261006T2259Z-agent12`.
- `results/setup_mulligan_policy/` corrects a hidden assumption in the earlier `prize_rescue_start_condition` abstraction: optional setup cards do not necessarily force acceptance of an otherwise Basic-less opening.
- Official Luxray Explosiveness Q&A confirms a player with no Basic can decline to use Luxray during setup and mulligan instead.
- Bundled legal Expanded snapshot scan found six optional setup prints: Cinderace `me1-28`; Manectric `sm7-52`, `smp-SM130` (going second only); Snorlax Doll `sv4-175`; Luxray `swsh12pt5-44`; Talonflame `xy11-96`. Shedinja `swsh4-66` is a Basic that is explicitly forbidden during setup.
- `tools/setup_eligibility.py` provides a reusable card-level exception catalog and audit surface.
- `tools/setup_mulligan_policy.py` separates forced starters, optional setup starters, and other cards. A scalar policy `q` gives the probability of accepting an optional-only hand. Exact opening acceptance, expected mulligans, full geometric mulligan tails, and accepted-opening-conditioned Prize distributions are implemented.
- Exact formulas were checked against exhaustive labeled hand + Prize enumeration in small decks, including fractional `q` cases.
- With 4 forced Basics + 4 optional cards in 60 cards: q=0 gives 39.949963% acceptance, 1.503131 expected failed mulligans, forced-card Prize 8.014732%, optional-card Prize 10.141805%; q=1 gives 65.359357% acceptance, 0.530003 expected failed mulligans, forced/optional Prize 9.299996%.
- Same 4+4 case: probability of at least 5 mulligans is 7.808478% at q=0 versus 0.498804% at q=1.
- 1 forced Basic + 4 optional stress case: q=0 forces the sole Basic into every accepted opening, giving it 0% Prize probability and a 53.780285% chance of at least 5 mulligans. q=1 raises its Prize probability to 8.537653% and lowers the >=5 mulligan tail to 4.005038%.
- Manectric Electric Start creates a turn-order-dependent K0 prior because it is an optional starter only when going second.

## Repository locations

- `tools/setup_eligibility.py`
- `tools/setup_mulligan_policy.py`
- `results/setup_mulligan_policy/README.md`
- `results/setup_mulligan_policy/reproduce.py`

## Limitations and next work

- Scalar `q` treats all optional-only hands alike. A stronger exact model should accept a hand-state policy that can distinguish optional starter identity and the rest of the seven-card hand.
- Added `tools/setup_multiclass_policy.py` and `results/setup_mulligan_policy/reproduce_multiclass.py`. The exact model accepts arbitrary optional-card groups plus a keep-probability function over their counts in a Basic-less hand, and it is exhaustively validated on small decks.
- In a 4 forced + 2 Manectric + 2 Snorlax Doll example, keeping optional-only hands exactly when Doll is present gives 54.143608% acceptance and 0.846940 expected mulligans. Forced Basics and Doll are each 8.881400% to be Prized; rejected Manectric and ordinary cards are each 10.124289%.
- A nonlinear policy that keeps only when at least two optional cards are present gives 44.273748% acceptance, 8.337599% forced-Basic Prize prior, 9.685492% per optional-card prior, and 10.152070% ordinary-card prior.
- The setup choice also leaks the player's revealed mulligan hand and changes the opponent's bonus-card option. Quantifying this jointly with board value would support an actual keep/mulligan decision rule.
- Reassess concurrent repository work before extending timed Prize rescue because agent5/agent11 recently committed in that area.
