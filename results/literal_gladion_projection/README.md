# Literal Gladion Prize cycling is projection-equivalent for isolated rescue

## Question

The repository's timed Prize-rescue models use a convenient abstraction: a Gladion-like rescue Supporter in hand is consumed when it rescues one initially critical Prize card.

Literal Gladion has different zone text. It looks at the face-down Prize cards, puts one of them into the hand, then shuffles the played Gladion into the remaining Prize cards. Does that destination invalidate the earlier consumed-rescuer probability models?

For the isolated objective those models actually optimize, the answer is **no**. The literal state projects exactly onto the consumed-rescuer state.

Implementation: `tools/literal_gladion_rescue.py`  
Reproducer and independent labeled validation: `results/literal_gladion_projection/reproduce.py`

## Card-text and timing basis

`results/gladion_access_connectors/` records the bundled Gladion text and the relevant timing class. Gladion is a Supporter, it must be played from the hand for its effect to work, it puts one face-down Prize card into the hand, and the played Gladion is shuffled into the remaining Prize cards.

The existing rescue family also models one ordinary Supporter window per rescue turn. This result keeps that same timing assumption so the only changed semantic is Gladion's destination.

## Literal state

The dynamic program keeps:

- rescue turns remaining;
- number of **initially critical** cards still in the Prize zone;
- Gladion copies in hand;
- Gladion copies in the Prize zone;
- Gladion copies in the deck;
- all other cards remaining in the deck.

Each turn begins with one random draw. The policy may wait or play one Gladion from hand.

A literal critical rescue performs:

`critical_prizes -= 1`

`gladion_hand -= 1`

`gladion_prizes += 1`

The retrieved critical card enters the hand, but its later hand value is outside this isolated objective.

The model also explicitly permits the tempting recycle action: use a Gladion from hand to take a Gladion from the Prize cards. One Gladion leaves the Prize zone and the played Gladion enters it.

## The projection theorem

Define the literal value as

`V_L(t, c, h, p, d, o)`

where `p` is the number of Gladion copies currently in the Prize zone.

Define the consumed-rescuer projection as

`V_C(t, c, h, d, o)`.

For this objective and transition system,

**`V_L(t, c, h, p, d, o) = V_C(t, c, h, d, o)` for every reachable state.**

The reason is structural.

A natural draw has the same probability and the same projected state transition in both models.

Playing Gladion to take a critical Prize changes the projected state exactly like consuming one rescuer: one critical requirement disappears and one hand rescuer disappears. Literal Gladion additionally increments `p`, but `p` has no effect on future deck draws or on the ability of another Gladion in hand to take a critical Prize.

Playing Gladion to take a Prized Gladion changes neither `h` nor `p`: one copy enters the hand while the played copy takes its Prize slot. After projecting away physical identity, the material rescue state is unchanged. The Supporter window has still advanced, so this action has exactly the same continuation state as waiting for this isolated objective.

Induction on the remaining turn horizon therefore makes the literal value independent of `p` and identical to the consumed-rescuer value.

## Exact baseline

Using the repository's standard 60-card rescue baseline:

- 12 setup-eligible starters;
- 4 non-starter critical singletons;
- 2 Gladion copies;
- 6 Prize cards;
- 7-card accepted opening;
- one random draw at the beginning of each modeled rescue turn;
- condition on at least one modeled critical being initially Prized.

| Horizon | Literal Gladion | Consumed-rescuer baseline |
| ---: | ---: | ---: |
| Turn 1 | 20.988290% | 20.988290% |
| Turn 2 | 23.799232% | 23.799232% |
| Turn 3 | 26.377561% | 26.377561% |
| Turn 4 | 28.912644% | 28.912644% |

The equality is exact inside the model. These values reproduce the no-connector row of `results/prize_rescue_connector_turns/`.

## Validation

The reproducer checks the claim at three levels.

First, it enumerates thousands of abstract states across turn horizons, critical counts, hand Gladion counts, Prized Gladion counts, deck Gladion counts, and filler counts. Every literal state value equals its consumed projection to floating-point precision. Varying the number of Prized Gladion copies does not change the projected value.

Second, the 60-card exact setup-conditioned calculation reproduces the published no-connector rescue probabilities above.

Third, an independent labeled 10-card model tracks physical card identities in the opening hand, Prize zone, deck, and hand after every swap. It explicitly moves the played Gladion into the exact vacated Prize population and permits selecting a Prized Gladion. For one through three Gladion copies and one through three rescue turns, its results match the category dynamic program exactly.

For the two-Gladion, two-turn small regression:

- `P(any critical initially Prized | valid start) = 40.448179%`;
- conditional literal rescue success = `76.606648%`.

## Why the literal zone still matters elsewhere

This equivalence is deliberately narrow. It does **not** mean Gladion's Prize-zone destination can be erased from a general Pokémon TCG state model.

The projection can fail when another objective or effect cares about:

- exact Prize composition or positions;
- later Prize inspection, exchange, shuffle, or recovery effects;
- ordinary Prize-taking;
- the identity or value of the card taken into hand;
- hand size, discard costs, or other uses of the retrieved card;
- a policy whose goal includes recovering Gladion itself;
- external effects that can remove a Gladion from the Prize zone without spending another Gladion play.

In those richer states, the physical destination is real information and should remain in the canonical game state.

## Methodological implication

This result gives a useful example of **validated projection**. A canonical simulator should preserve the literal card movement, while a narrow probability model may quotient away a state variable after proving that the objective value is invariant to it.

That is stronger than silently simplifying the card text. The simplification now has an explicit domain of validity, a state-level equivalence statement, and an exhaustive regression.

## Next useful work

The next extension is to reintroduce one interaction that can break the projection, such as ordinary Prize-taking or another Prize-manipulation effect, and measure the first regime where literal Gladion placement changes policy value. A second useful path is to compose literal Gladion with the new Xtransceiver connector model and confirm that the projection remains exact while connector search can only reach Gladion copies still in the deck.
