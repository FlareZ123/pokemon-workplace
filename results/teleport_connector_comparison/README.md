# Typed connector choice reverses Stadium-feed access value

## Question

With a live Gothitelle already able to use Teleport Room, and normal Stadium
play exhausted, does the Item chosen to discard Sky Field affect whether a
full Collapsed Stadium Bench can reopen?

**Yes.** When the required searched target is Basic, Quick Ball can use Sky
Field as its entire one-card discard payment and retrieve that Basic. Ultra
Ball searches any Pokémon but must discard Sky Field plus an additional card.
For a required Evolution Pokémon, Quick Ball cannot search it at all; Ultra
Ball's broader target domain can outweigh its higher discard burden.

This is a typed-action, payment-aware extension of
[`teleport_discard_goal_closure/`](../teleport_discard_goal_closure/).

- Mathematical model: [`tools/teleport_connector_comparison.py`](../../tools/teleport_connector_comparison.py)
- Physical Quick Ball extension: [`tools/teleport_discard_payload_line.py`](../../tools/teleport_discard_payload_line.py)
- Regression: [`reproduce.py`](reproduce.py)
- [Passing GitHub Actions run 37772986382](https://github.com/FlareZ123/pokemon-workplace/actions/runs/37772986382)

## Exact source anchors

- Quick Ball `swsh1-179` is Expanded-legal in the bundled legality baseline.
  Its text requires discarding **one other card from hand** and searches the
  deck for **a Basic Pokémon**.
- Ultra Ball `swsh9-150` is Expanded-legal. It requires discarding **two
  other cards** and searches for **a Pokémon**.
- Sky Field `xy6-89` raises the Bench capacity to eight while present.
- Gothitelle `xy3-41` / Teleport Room moves a differently named Stadium
  from the discard pile into play without consuming ordinary Stadium play.

The two Item profiles are borrowed from the existing canonical Harto Raichu
search-execution infrastructure. Both are grounded in exact card text.

## Physical two-Basic witness

Start with Collapsed Stadium and four Bench occupants, an already-established
Active Gothitelle with unused Teleport Room, and the turn's ordinary
Stadium-play quota spent. Hand contains Quick Ball, Sky Field, and one Basic;
a second Basic is available either in hand or deck.

For the *deck target*:

`Quick Ball discards Sky Field -> retrieves Basic -> Teleport Room places Sky Field -> Bench first Basic -> Bench second Basic`

For the *already held target*, Quick Ball discards Sky Field and chooses zero
cards in its restricted search; the same two Bench entries then succeed.
The shared Trainer transaction now correctly models this zero-result search
with compulsory discard payment.

The physical test confirms exact card identity movement, one-card payment,
Stadium quota preservation, capacity eight, and two successful entries in
both branches. Card-class totals remain conserved.

On the same hand, Ultra Ball has no legal analogous one-card payment. Its
two-card requirement needs an additional sacrifice, which may be protected
or entirely absent.

## Exact access comparison

The experiment considers two hypothetical alternate deck configurations,
one with four Quick Ball and the other with four Ultra Ball. Each has two
Sky Field, 16 separately approved additional discard candidates, one required
target singleton, and 23 filler cards inside a 46-card unknown pool.

Six random Prizes are placed, then five random cards observed. The
appropriate connector plus Sky Field must be seen. The target is either
naturally seen or unprized and still in the deck; for Ultra Ball, an
additional approved discard card must be in hand. For Quick Ball, that extra
card is unnecessary.

| Target access endpoint | 4 Quick Ball build | 4 Ultra Ball build |
| --- | ---: | ---: |
| Required **Basic Pokémon**, ultimately Bench-entered | **5.804898%** | 4.474518% |
| Required **Evolution Pokémon**, obtained in hand | 0.479006% | **4.474518%** |

The Evolution-Pokémon row measures access to the Evolution card in hand for
a later valid evolution, whereas the Basic row has the additional bounded
physical Bench-entry witness. Naturally drawing the Evolution singleton
accounts for all Quick Ball success in the second row, because Quick Ball's
search domain excludes Evolution cards.

These exact percentages are conditioned on the existing Gothitelle, full
Collapsed Bench, spent Stadium-play action, pre-held first Basic, and the
stated search/payment channel. They are **not** whole-deck setup rates.

The comparison is exact for the constructed group counts and card-type
requirement. It is not evidence that Quick Ball universally dominates Ultra
Ball, since real decks have diverse search targets and discard resources.

## Why the ranking reverses

For Basic-target access, Quick Ball has a target-compatible search and a
cheaper compulsory payment. Its availability event requires only one
Quick Ball and one Sky Field, with the target either accessible in the deck
or naturally held.

Ultra Ball additionally requires an approved second discard. That
extra constraint produces a lower access rate under equal connector copy
counts in the chosen model.

For Evolution-target access, Quick Ball can only contribute if the target
is already in hand. Its search cannot directly retrieve that target.
Ultra Ball retains both the natural-hand and deck-search branches, even
while paying an extra card. The broader target domain produces the
opposite ranking.

This is a quantitative example of **payment cost interacting with typed
search coverage**. Comparing Item effects only by discard cost, search
generality, or average draw access can miss the relevant composition.

## Validation

The SFT independently enumerates all labeled Prize subsets and subsequent
hands in four small test configurations: one versus two discard requirements
crossed with searchable versus unsearchable targets. Symbolic and brute-force
fractions match exactly. The larger results, printed in the successful CI
run, are exact rational evaluations.

The physical Quick Ball-to-Teleport line is tested twice: with a searched
Basic and with a Basic already in hand. The test also checks both Items'
current effective Expanded legality and exact printed discard/target
wordings, and demonstrates Ultra Ball's rejected one-card payment.

## Limitations and next questions

Real games require establishing Gothitelle (Stage 2), managing Ability
lock and other Bench restrictions, preserving the chosen Basic, and
considering other Item search targets and Supporter contention. This
abstract calculation excludes those costs and does not estimate whether
a deck should run either Item or Gothitelle.

The next useful extension is to treat both Quick Ball and Ultra Ball in
the *same* unknown pool, allowing a policy to choose which connector to
play based on observed hand, target type, and other discard commitments.
That introduces overlapping card-access events and exact policy choice
rather than separate hypothetical deck substitutions.
