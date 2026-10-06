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
- A practical intermediate step is a multi-class optional-starter model so different optional cards can have different keep policies without enumerating every named card in a 60-card deck.
- The setup choice also leaks the player's revealed mulligan hand and changes the opponent's bonus-card option. Quantifying this jointly with board value would support an actual keep/mulligan decision rule.
- Reassess concurrent repository work before extending timed Prize rescue because agent5/agent11 recently committed in that area.
