# Aichi Vileplume Prize-Supporter information timing

## Question

Do the singleton Gladion and Peonia in Takahiro Ando's 2026 Aichi runner-up Vileplume Control list materially repair the first-turn Bunnelby plus Technical Machine: Evolution plus Jet Energy core, once Supporter contention, Prize destinations, and information timing are represented?

They create a small but measurable rescue layer. Gladion is stronger in the endpoint-feasibility model, while much of that apparent value depends on exact Prize knowledge being available before the player commits the turn's Supporter.

Implementation: `tools/aichi_prize_supporter_information.py`

Regression: `results/aichi_prize_supporter_information/reproduce.py`

Raw aggregate counts: `results/aichi_prize_supporter_information/summary.json`

## Relationship to the existing Aichi model

This work extends `results/aichi_vileplume_als/` rather than replacing it.

The existing broader first-turn planner conditions on an accepted seven-card opening, sets six Prize cards, takes the first-turn draw going second, uses the same starting-Active policy, and allows the Bunnelby core to be reached through natural resources or Guzma & Hala.

The current regression for that planner reports 70.709% core success for 100,000 trials at seed `20261007`.

The new tool reproduces exactly 70,709 baseline successes on that same seed before adding either Prize Supporter.

## Card transitions represented

Gladion is modeled as:

1. spend the Supporter play;
2. inspect the six face-down Prize cards;
3. choose one Prize card and move it to hand;
4. continue the immediate line from the resulting hand.

The recovered card stays in hand. It does not return to the deck. This matters because Technical Machine: Evolution searches the deck for Evolution cards.

Peonia is modeled as:

1. spend the Supporter play;
2. choose three fixed face-down Prize positions without looking at them;
3. move those three cards to hand;
4. choose three cards from the resulting hand and put them back as Prize cards;
5. continue the immediate line.

Because the simulated deck order is random, the fixed three positions are an unbiased blind three-of-six Prize sample. Replacement cards are chosen after the three selected Prizes are known, matching the information order in the card text.

For this immediate hand-feasibility objective, taking three is weakly better than taking fewer. Any extra unwanted Prize card can itself be returned among the replacement cards, so the extra blind sample need not reduce the final hand's immediate core resources. This claim is limited to the modeled immediate objective. Future Prize composition can still matter.

## Finding 1: both Prize Supporters add a small first-turn repair layer

Five matched 100,000-trial blocks, seeds `20261007` through `20261011`, give:

| Model | Core success | Gain over baseline |
| --- | ---: | ---: |
| Existing broader baseline | 70.6334% | |
| + state-aware Gladion route | 70.9298% | +0.2964 pp |
| + blind Peonia route | 70.8344% | +0.2010 pp |
| + both routes | 71.1118% | +0.4784 pp |

The paired added-success counts are:

- Gladion: 1,482 of 500,000 states;
- Peonia: 1,005 of 500,000 states;
- either Supporter: 2,392 of 500,000 states.

Only 95 states are repaired by both mechanisms. The gains are therefore mostly complementary in this narrow first-turn core.

Approximate normal 95% half-widths for the paired added-success events are about 0.0151 pp for Gladion, 0.0124 pp for Peonia, and 0.0191 pp for the combined gain.

## Finding 2: Gladion mainly repairs the Tool or Special-Energy channel

Eight 100,000-trial blocks, seeds `20261007` through `20261014`, give a state-aware Gladion gain of:

- baseline: 70.62750%;
- with Gladion route: 70.92675%;
- gain: **+0.29925 percentage points**;
- added successes: 2,394 of 800,000.

Among those 2,394 added successes, the selected Gladion Prize was:

| Recovered card | Added successes | Share |
| --- | ---: | ---: |
| Jet Energy | 954 | 39.8496% |
| Technical Machine: Evolution | 903 | 37.7193% |
| Artazon | 225 | 9.3985% |
| Bunnelby | 218 | 9.1061% |
| Fan Rotom | 94 | 3.9265% |

Jet Energy plus Technical Machine: Evolution account for 77.5689% of the incremental Gladion wins.

This is structurally consistent with Supporter contention. When Gladion is the Supporter, Guzma & Hala cannot be played that turn, so the line needs most of its remaining core resources already in hand. Gladion is especially useful when exactly one of those hand-required channels is trapped in the Prize cards.

Only 105 of the 2,394 added successes, 4.3859%, require Stellar Wish to find Gladion itself. Most added value comes from states where the singleton Gladion is already accessible and another Stellar choice is unnecessary or can serve a different resource.

## Finding 3: exact Prize information is a major Gladion bottleneck

The full state-aware Gladion result assumes the player can choose Gladion when that branch is the useful one.

That is an information assumption. Before the first full deck search, a skilled player can still be at K0 and may not know whether a missing resource is in the deck or among the Prize cards.

A separate 400,000-state experiment gates the Gladion branch behind concrete pre-Supporter full-deck searches:

| Information gate | Core success | Gain over baseline |
| --- | ---: | ---: |
| Baseline | 70.61150% | |
| Tag Call search before Gladion | 70.62375% | +0.01225 pp |
| Tag Call or Fan Rotom search before Gladion | 70.68425% | +0.07275 pp |
| Full state-aware Gladion ceiling | 70.91000% | +0.29850 pp |

The Tag Call or Fan Rotom subset captures 291 of 1,194 added state-aware Gladion successes, or 24.3719%.

This is deliberately a conservative K1 surface rather than an exhaustive one. Other legal full-deck searches may also establish exact Prize composition before the Supporter decision. The result is still enough to show that the state-aware Gladion ceiling should not be interpreted as a directly executable K0 policy.

## Finding 4: Peonia and Gladion solve different information problems

Gladion becomes exact after it is played because the player looks at all face-down Prize cards and chooses one.

Peonia samples Prize positions blindly. Its three selected positions do not depend on Prize identity in this model. Its value comes from sample size and flexible hand-to-Prize replacement after the sampled cards are observed.

This difference matters for planners. Treating both Supporters as a generic `Prize -> hand` edge loses:

- selection information;
- number of cards moved;
- replacement obligations;
- Supporter contention;
- whether the decision to commit the Supporter can be justified at K0 or requires K1.

## Validation

The fixed-seed regression uses 100,000 accepted-opening trials at seed `20261007` and asserts:

- baseline: 70,709;
- state-aware Gladion: 71,006;
- blind Peonia: 70,938;
- combined: 71,212;
- Tag Call K1 Gladion: 70,721;
- Tag Call or Fan Rotom K1 Gladion: 70,776.

For the 297 state-aware Gladion additions on this seed, the exact recovered-card counts are also asserted.

The baseline count matches the current `aichi_vileplume_als` broader-route regression exactly, giving a direct compatibility check with the existing planner.

## Limits

This remains an endpoint-feasibility model.

It does not model opponent interaction, strategic future value of cards moved into or out of the Prize zone, matchup-specific DCI, later-turn Prize-taking, or full-game utility.

The state-aware Gladion and combined rows are ceilings under pre-Supporter Prize knowledge. The Tag Call and Fan Rotom information rows cover only two concrete K1 enablers.

The Peonia row uses legal blind Prize selection, while the union of Peonia with the baseline remains an endpoint-aware feasibility comparison rather than a complete K0 decision policy.

The model studies only the Bunnelby double-Evolution core. Downstream Stage 2 endpoints have additional deck-zone constraints.

## Next work

A stronger continuation is a genuine K0/K1 Supporter-choice policy for this exact list.

Such a planner should:

- represent the first full-deck search as an information event;
- distinguish searches that happen before and after the Supporter commitment;
- choose among Guzma & Hala, Gladion, Peonia, and natural lines using only information legally available at that decision point;
- carry Peonia's new Prize composition into later turns;
- score future utility instead of only the first-turn core.

That would turn the current feasibility ceilings into an executable information-aware policy.
