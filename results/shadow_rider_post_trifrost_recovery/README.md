# A deterministic return of Mimikyu after Regidrago's Trifrost snipe

## Question

After Regidrago VSTAR uses Apex Dragon to copy Timeless-GX, it gets an extra turn. If it copies Kyurem's Trifrost during that bonus turn, it may Knock Out the Aichi champion Shadow Rider Calyrex list's only unprotected, Benched Mimikyu (70 HP versus Trifrost's 110 damage).

Since the second declared attack is *again* Apex Dragon, could Shadow Rider immediately recover Mimikyu and use Copycat on the following turn anyway?

**Yes, in several fully specified resource configurations.** Trifrost moves the knocked-out Mimikyu and its attached cards to the discard, where recovery effects can access them. The response needs a new sequence that assembles Mimikyu, pays Copycat, and moves it Active in one turn. Regidrago does not automatically erase Apex Dragon from last-attack history by copying Trifrost.

## The conditional baseline witness

Construct a post-Trifrost state:

- Mimikyu and two Basic Psychic Energy are in Shadow Rider's discard pile.
- Shadow Rider Calyrex VMAX is still Active and damaged; another live copy or other Benched Pokémon is optional.
- One active Shadow Rider VMAX can still use Underworld Door; one manual Energy attachment and the Supporter quota are unused.
- Tulip, Float Stone and the needed resources can be played/obtained this turn.
- There is an open Bench slot for Mimikyu, the Active has no Tool, its normal Retreat is permitted, and Float Stone's effect is live.
- Regidrago's last declared attack remains Apex Dragon, Shadow Rider's Dialga-GX is in its discard, and Shadow Rider has not spent its own GX attack.

A deterministic witness, ignoring all cards drawn from Underworld Door, is:

1. **Tulip** returns Mimikyu and two Basic Psychic Energy from discard to hand, consuming the Supporter.
2. Bench Mimikyu.
3. **Underworld Door** attaches one Psychic Energy from hand to Benched Mimikyu.
4. Manually attach the other Psychic Energy to Benched Mimikyu.
5. Attach **Float Stone** to the Active Shadow Rider VMAX, if its Tool slot is empty and the Tool works.
6. Retreat the VMAX at zero Retreat Cost and promote Mimikyu.
7. Declare Copycat, selecting the still-exposed Apex Dragon, which can copy Timeless-GX from the Shadow Rider player's discarded Dialga-GX.

The planner searches the first six steps as a bounded state machine; the already validated canonical copy regression establishes the seventh step's nested semantics. The above is a **conditional feasible line**, not an assertion that the champion had those resources after the actual game attack.

Float Stone is a **Pokémon Tool** under current rules even though XY-era text also says “Item”. Under the Advanced Player's Rulebook B-02, older Pokémon Tools are not treated as Items. Thus the bounded Tulip+Float Stone witness remains legal under an *Item-only* restriction when Tools themselves may still be played.

With Dimension Valley in play, Copycat needs only one Psychic Energy; the manual attachment by itself can pay it even if Underworld Door is unavailable.

## Alternative bounded witnesses

| Resources and board state | Same-turn recovery/promotion |
| --- | --- |
| Tulip + Float Stone, two Psychic from discard, Underworld Door + manual attachment | **Feasible**, no second Supporter |
| Tulip + Float Stone with Item-only lock, Tools still enabled | **Feasible**, given the same independent constraints |
| Tulip + Float Stone, no Underworld Door, no Dimension Valley, zero starting Psychic in hand | **Blocked** by available Energy channels |
| Tulip + Float Stone, no Underworld Door, Dimension Valley active | **Feasible**, one Psychic attachment |
| Night Stretcher, two Psychic already in hand, Acerola, incumbent Active damaged | **Feasible**, Acerola picks up Active to promote Mimikyu |
| Night Stretcher, two Psychic already in hand, Guzma, opposing Bench present | **Feasible** |
| Night Stretcher + Guzma when opponent has no Bench, no Float Stone or Acerola | **Blocked** |
| No promotion card and no modeled alternative free retreat | **Blocked** |
| Only Night Stretcher, Psychic still in discard, Tulip unavailable | **Blocked** under the stipulated Energy supply |

Each row holds other required factors fixed. There may be other legal routes outside the modeled cards. Acerola's picked-up incumbent has to be damaged and Mimikyu must already be Benched; picking up a Shadow Rider VMAX means giving up that in-play Pokémon and its Energy state, an important opportunity cost.

### The counter-counter-counterplay effect

Regidrago's Trifrost choice punishes a pre-staged Mimikyu by knocking it out, taking one Prize, and possibly hitting two more Pokémon. **A single Mimikyu copy can return on the very next turn**, however, because Mimikyu remains a Basic Psychic Pokémon in the discard pile and the opponent last declared Apex Dragon.

The correct evaluation depends on Shadow Rider's Supporter availability, Tool and Item access, Energy recovery and attachment, Bench space, and incumbent Active position. If Regidrago instead covers with Budew, it removes the Apex Dragon target, regardless of whether Shadow Rider re-establishes Mimikyu.

This extends the earlier [bonus-turn Trifrost snipe](../regidrago_bonus_turn_mimikyu_snipe/README.md), [dual-denial Budew line](../timeless_budew_dual_denial/README.md), and [Shadow Rider payload-routing study](../shadow_rider_regidrago_counter_als/README.md).

## Reproduction and verification

- `tools/shadow_rider_post_trifrost_recovery.py`: typed immutable state, bounded action transitions, breadth-first witness search.
- `results/shadow_rider_post_trifrost_recovery/reproduce.py`: exact source card text checks and positive/negative recovery tests, including Supporter and Energy contention.
- The rules manual §§A-03, B-02, B-03, E-12 and C-19 describes retreats, Tools, Supporters, Abilities and Item-lock timing.
- The reproduced code assumes each named card is accessible, and does not simulate search, unknown draw outcomes, damage resolution, card effects on the opponent, Battle Compressor, evolution, or prize-taking on the response.
- The search always treats the opponent's Apex Dragon as still exposed and Dialga-GX as available in Shadow Rider's discard; if either fact fails, it correctly refuses to report a successful Copycat response.

To run:

`python results/shadow_rider_post_trifrost_recovery/reproduce.py`

The result is **deterministic line existence under the declared state**, not measured match win probability.

## Next steps

1. Place Regidrago's Timeless-GX and Trifrost in a full board-state model to track actual KO, Prize change, and wounded Active as post-attack facts rather than input assumptions.
2. Compute the probability of specific recovery resources under realistic late-game hand/Prize information and Tool locks.
3. Quantify costs: Regidrago discards all Energy when copying Trifrost, Shadow Rider loses a Mimikyu and a Prize, Acerola disrupts its VMAX board, and Tulip uses the Supporter window.
