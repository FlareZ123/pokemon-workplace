# Setup-role contention for hand-to-Bench trigger Pokémon

## Question

A Basic Pokémon with an Ability such as Tapu Lele-GX's Wonder Tag can look like an opening-hand out because the card is already in hand. Is that opening copy actually available to produce its hand-to-Bench trigger after setup?

For normal Basic setup, sometimes it is not. If the trigger Pokémon is the only Basic Pokémon in the accepted opening hand, one copy must be chosen as the starting Active Pokémon. That physical copy is no longer in hand and was not played from hand onto the Bench during the turn.

This result isolates that **setup-role contention** exactly.

Implementation: `tools/setup_trigger_role_contention.py`  
Independent labeled-hand reproducer: `results/setup_trigger_role_contention/reproduce.py`

## Rules basis

The bundled Advanced Player's Rulebook gives the relevant sequence:

1. draw seven cards;
2. if the hand has Basic Pokémon, choose one and put it face down in the Active Spot;
3. putting other Basic Pokémon onto the Bench during setup is optional;
4. the game starts only after setup and Prize placement.

The same manual's E-06 section says that wording of the form "When you play this Pokémon from your hand onto your Bench" refers to playing a Basic from hand onto the Bench during the turn, and the effect can only be applied when the Pokémon is played that way.

Therefore a trigger Basic used as the starting Active does not satisfy that trigger merely because it began the game in play.

## Exact model

Partition the deck into:

- `T` Basic Pokémon whose useful action requires a hand-to-Bench trigger;
- `B` other ordinary Basic Pokémon that can satisfy setup;
- filler.

For an opening hand, let `s` be the number of trigger Basics and `b` the number of other Basics.

The hand is accepted in this baseline exactly when:

`s + b >= 1`

A naive opening-access model counts all `s` trigger Basics as available trigger copies.

A role-aware model chooses the starting Active to preserve as many trigger Basics in hand as possible. The number left in hand for later trigger plays is:

`retained = s - I(b = 0 and s > 0)`

If an ordinary Basic exists, use one of those as the Active and retain every trigger Basic. If none exists, one trigger Basic must pay the Active-position setup cost.

All probabilities below are conditioned on a valid accepted opening. The default calculation assumes the player preserves enough Bench space for the trigger. Optional setup benching is therefore not credited as an unavoidable capacity loss.

## Single trigger Basic: total Basic count matters

Consider one copy of a trigger Basic in a 60-card deck and a seven-card opening.

| Trigger Basics | Other Basics | Valid opening | Naive trigger access given valid start | Role-aware trigger access | Overstatement |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 3 | 39.949963% | 29.203198% | 8.159360% | 21.043838 pp |
| 1 | 7 | 65.359357% | 17.850033% | 9.784773% | 8.065260 pp |
| 1 | 11 | 80.935331% | 14.414801% | 10.488895% | 3.925906 pp |

With only four total ordinary Basics, 72.06% of the accepted-opening states that a naive model calls an opening-copy trigger success are false positives from setup-role contention.

The reason is conditioning. In a low-Basic deck, seeing the one trigger Basic is disproportionately likely to be the event that made the hand keepable at all. In many of those accepted hands it is the only Basic and must become Active.

## Fixed four-Basic deck: replacing ordinary starters with trigger starters

Hold the deck at four total Basics and vary how many are hand-to-Bench trigger Pokémon.

| Trigger Basics | Other Basics | Naive trigger access | Role-aware trigger access | Overstatement |
| ---: | ---: | ---: | ---: | ---: |
| 1 | 3 | 29.203198% | 8.159360% | 21.043838 pp |
| 2 | 2 | 55.436579% | 13.348904% | 42.087675 pp |
| 3 | 1 | 78.956162% | 15.824650% | 63.131513 pp |
| 4 | 0 | 100.000000% | 15.824650% | 84.175350 pp |

The last row is intentionally extreme. Every valid opener contains a trigger Basic, so raw opening presence says 100%. A role-aware model requires at least two such Basics in the opener: one becomes Active and another remains in hand for the trigger. Only 15.824650% of accepted openings meet that condition.

This is a physical-card capacity problem. One copy cannot simultaneously occupy the mandatory starting Active role and remain a card in hand to be played onto the Bench.

## Card-pool scope

A literal scan of the bundled paper-Expanded card pool, using the repository's print-level legality overlay, finds:

- 124 legal prints;
- 49 unique card names;
- 52 conservative gameplay fingerprints;

where a Basic Pokémon Ability contains the literal hand-to-Bench phrase.

Strategically familiar examples include Jirachi-EX (Stellar Guidance), Tapu Lele-GX (Wonder Tag), Dedenne-GX (Dedechange), Crobat V (Dark Asset), and Lumineon V (Luminous Sign).

The catalog deliberately uses a literal wording scan rather than claiming semantic completeness. Shaymin-EX is absent because its relevant Expanded prints are banned.

## Relation to existing repository work

`results/gladion_access_connectors/` and `results/typed_access_network/` already distinguish an important zone transition: Quick Ball can put Tapu Lele-GX into hand and then manual benching can fire Wonder Tag, while Nest Ball puts Tapu Lele-GX directly onto the Bench and does not fire the hand-play trigger.

This result identifies an earlier boundary in the same line. A Tapu Lele-GX that begins in the opening hand is not automatically a usable Wonder Tag copy. Setup may consume the physical card into the Active role before the first turn begins.

This is closely related to connector capacity. Search-path analysis should track role occupancy of physical cards, not only whether the card's identity appears in an accessible zone at some point.

## Strategic interpretation

### Accepted-opening conditioning can reverse intuition

A support Basic can improve mulligan avoidance while simultaneously becoming less available for its intended Bench-entry function. Those two values should be represented separately.

### Setup roles are resources

The starting Active position consumes one physical Basic. In a low-Basic deck, that role can compete directly with a card's tactical purpose.

### Bench-entry support has two separate constraints

For a trigger to be realistic, a suitable copy must still be in hand, or be moved into hand by a legal line, and a Bench slot must be available when that copy is played. The current exact result models the first condition and exposes Bench capacity as a parameter. It does not assume that all optional Basics should be placed onto the Bench during setup.

### Search can rescue some forced-Active states

This result studies trigger copies already present in the opening hand. A deck can still obtain another copy from the deck with a search effect, recover or move the Active copy by a card effect, or use a different support route. Those are separate transitions and should be modeled explicitly rather than silently crediting the opening copy.

## Validation

The exact calculation is multivariate hypergeometric over opening-hand category counts.

The reproducer independently enumerates every labeled opening-hand combination in several small decks and compares valid-start probability, naive trigger success, and role-aware trigger success.

The values match exactly as rational numbers. Additional regression cases cover two required trigger transactions and restricted Bench capacity.

The reproducer also reruns the literal legal-card catalog and asserts the current snapshot counts plus representative inclusions and the exclusion of banned Shaymin-EX.

## Limits

This is a normal-Basic setup baseline. It does not yet model optional setup exceptions such as Talonflame, Luxray, Manectric, Cinderace, or Snorlax Doll; Shedinja's setup prohibition; matchup- or hand-specific Active choices; search for fresh trigger Pokémon after setup; effects that return or replace the starting Active; lock effects; discard costs; Prize placement for copies outside the opening hand; the liability of leaving support Pokémon on the Bench; or later Bench congestion.

The numbers are exact evidence for one setup constraint rather than full turn-one access probabilities for a deck.

## Next useful work

The strongest extension is to join this setup-role model to the typed access network:

- opening copy retained in hand;
- opening copy consumed as Active;
- Quick Ball-like search into hand;
- direct-to-Bench search that does not trigger;
- remaining copies hidden in Prize cards;
- finite Bench slots;
- lock-sensitive connector edges.

That would produce a turn-one support-access model in which zone, role, card-copy capacity, and Bench capacity are all explicit.
