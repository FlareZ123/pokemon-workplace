# Palace Belt + Player's Ceremony + Speed Lightning recovery line

## Question

Can the same paid Guzma & Hala action that recovers the Japanese-only Belt/Ceremony package also improve the Energy state and generate immediate card draw?

Yes. Kazuma and Kohei each run four Speed Lightning Energy. The bundled card text says that attaching Speed Lightning Energy from hand to a Lightning Pokemon draws two cards, and the bundled Iron Thorns ex records are Lightning type.

Because paid Guzma & Hala can search a Stadium, a Pokemon Tool, and a Special Energy in one action, it can support the line:

`Tag Call -> Guzma & Hala -> Player's Ceremony + Palace Belt + Speed Lightning Energy -> attach Belt -> attach Speed Lightning, draw 2 -> use Ceremony, draw 2 and end turn`

Implementation: `tools/iron_thorns_speed_recovery_line.py`  
Regression: `results/iron_thorns_speed_recovery_line/reproduce.py`

## Exact endpoint

The model uses the same accepted seven-card opening, six Prize cards, and first normal draw as the existing exact Iron Thorns named-line result.

It first checks the narrow Thunder Mountain + DCE Volt Cyclone line. Only named-line failures are considered for recovery.

The full recovery package is ready when Palace Belt, Player's Ceremony, and Speed Lightning Energy are each either already in hand or can be supplied through one accessible Guzma & Hala. Missing Belt and Speed require the optional two-card discard branch. Ceremony is the unconditional Stadium channel.

The model preserves the one-connector constraint: one G&H can satisfy all three missing channels because they are Stadium, Tool, and Special Energy respectively.

## Exact results among named-line failures

| List | Full Belt + Ceremony + Speed package | Package requires paid G&H branch | One G&H fetches all three missing pieces |
| --- | ---: | ---: | ---: |
| Kazuma Kashi | **10.576296530%** | **9.722143029%** | **4.732013644%** |
| Kohei Hamamichi | **11.912415167%** | **10.272280267%** | **4.574220874%** |

As full accepted-opening state mass, the recovery package is 7.003464314% for Kazuma and 7.888221957% for Kohei.

The all-three-from-deck G&H witness is 3.133468184% and 3.028980188% of the full state space.

## Physical hand-flow witness

For the clean all-three search line, the hand-flow is mechanically favorable even after the two-card G&H discard.

After the Active Iron Thorns is chosen and the normal draw is taken, the model has seven cards in hand.

If Tag Call is needed to obtain G&H, playing Tag Call and taking one G&H is hand-size neutral.

Then:

1. play G&H: 7 -> 6;
2. discard two other cards: 6 -> 4;
3. search Ceremony + Belt + Speed Lightning: 4 -> 7;
4. attach Belt: 7 -> 6;
5. attach Speed Lightning: 6 -> 5, then draw 2: 5 -> 7;
6. play Player's Ceremony: 7 -> 6, then draw 2 and end the turn: 6 -> 8.

Thus the clean recovery witness can finish with eight cards in hand while leaving Palace Belt and Speed Lightning attached to the Active Iron Thorns.

This arithmetic describes card count only. The two discarded cards can still be strategically expensive under DCI.

## Why this is a multi-axis ALS

The line addresses several objectives with one paid Supporter:

- Player's Ceremony converts the current failed turn into two cards;
- Palace Belt raises the next normal beginning-of-turn draw from one to two while its holder stays Active;
- Speed Lightning provides Energy and draws two immediately when attached from hand to the Lightning-type Iron Thorns;
- the G&H discard places two chosen cards into the discard pile, which may be helpful or harmful depending on state.

The same connector therefore changes from an attack enabler to a recovery engine after the attack objective becomes impossible.

## Cross-checks

The regression loads the bundled `swsh2-173` Speed Lightning Energy record and asserts its draw effect.

It loads bundled Iron Thorns ex `sv6-77` and asserts Lightning type.

It independently calls `exact_named_line_probability()` and requires the recovery model to reproduce the original accepted-opening and named-line success probabilities exactly.

## Limits

Palace Belt and Player's Ceremony semantics come from the provenance-bearing Japanese external references in `regional_card_source/`; their translations are unofficial.

The model does not score the strategic quality of the two G&H discards.

It assumes the normal Energy attachment remains unused when the model evaluates the recovery pivot at the beginning of the represented turn.

It omits Trainers' Mail, which can itself find the regional Trainer cards.

It omits other G&H Special Energy choices, alternate Supporters, VS Seeker, opponent mulligan bonus draws, opponent interaction, and later switching.

Player's Ceremony ends the turn and is symmetrical. Palace Belt also competes with other Tools for the Active Iron Thorns.

## Next work

Integrate Trainers' Mail with a policy that first maximizes the named Volt Cyclone route and then, only when that route fails, maximizes a Palace Book or Player's Ceremony fallback. This will measure how much of the regional continuation is additionally exposed by the lists' 3/4/2 Trainers' Mail counts.
