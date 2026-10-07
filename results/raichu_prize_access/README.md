# Harto Miki Raichu/Electrode: zone-aware Alolan Raichu access

## Question

In Harto Miki's 13th-place Raichu/Electrode Combo list from Champions League Aichi Expanded 2024, how does the singleton Alolan Raichu's hidden zone change the practical value of Ultra Ball, Gladion, and Computer Search?

This is a concrete deck-level continuation of the repository's earlier discard-gate, Prize, and connector-domination work. It asks a narrow access question before attempting full combo simulation:

> after an accepted opening, six Prize cards, and a configurable number of later random draws, can the deck put its singleton Alolan Raichu into hand inside one Supporter-legal action window using the direct targeted package?

Implementation: `tools/raichu_prize_access.py`  
Independent exhaustive regression: `results/raichu_prize_access/reproduce.py`

## Deck and card basis

The published Harto Miki list is:

- 1 Alolan Raichu;
- 1 Pikachu;
- 2 Gladion;
- 3 Ultra Ball;
- 1 Computer Search;
- 4 Reversal Energy;
- 4 Counter Energy;
- 3 Unit Energy LPM;
- 1 Giratina;
- 16 setup-eligible Basic Pokemon in total.

Source: <https://limitlesstcg.com/decks/list/11221>

The same Raichu/Electrode archetype also placed second at that event and later returned at the 2026 Aichi Open League, so this is a real competitive archetype rather than a synthetic combo shell. Harto's particular list is intentionally the object modeled here because it combines a singleton Alolan Raichu with two Gladion and Computer Search.

The bundled card database gives the relevant text:

- **Alolan Raichu** (`sm11-57`) is a Stage 1 whose Electro Rain attack discards Lightning Energy from itself and spreads 30 damage per Energy discarded.
- **Gladion** (`sm4-95`) looks at the face-down Prize cards, puts one into hand, then shuffles the played Gladion into the remaining Prizes.
- **Ultra Ball** has a two-card discard cost and searches for one Pokemon.
- **Computer Search** (`bw7-137`) has a two-card discard cost and searches for any one card.
- **Electrode-GX** (`sm7-48`) can attach five Energy cards from the discard pile to non-GX/non-EX Pokemon, then Knocks itself Out.
- **Giratina** (`sm8-97`) can return from the discard pile to the Bench with Distortion Door.

The rulebook's deck-search procedure makes the target zone operationally relevant. When a player searches their deck, they inspect the remaining deck contents. A missing singleton can therefore be inferred to be Prized once the deck is searched accurately.

## Modeled direct package

The exact model partitions the 60-card list into:

1. singleton Alolan Raichu;
2. two Gladion;
3. three Ultra Ball;
4. one Computer Search;
5. a caller-defined pool of currently acceptable discard cards;
6. 16 setup-eligible starters;
7. protected or otherwise unmodeled cards.

Opening hands are conditioned on containing at least one of the 16 setup starters. Six Prize cards are then sampled from the remaining deck. The model can expose additional unbiased random cards before the action snapshot.

The preserved baseline exposes one additional random card and uses a **12-card conservative discard pool**:

- the 11 Special Energy cards;
- Giratina.

This is a state-dependent DCI policy assumption, not a claim that those cards are free. Energy in the discard pile is structurally useful to Extra Energy Bomb, and Giratina has a discard-pile Ability, so these 12 are natural candidates for a first conservative pool. Some games may preserve Energy, and other cards may become cheaper discards. Sensitivity results are therefore reported.

Only those designated cards pay Ultra Ball or Computer Search in the baseline. Spare connectors, Gladion, setup Pokemon, and other resources remain protected.

## Zone-aware connector semantics

The target can be in three strategically distinct zones.

### Raichu already exposed in hand

No connector is needed.

### Raichu remains in the deck

Ultra Ball or Computer Search can take it directly if the two-card discard cost is payable.

### Raichu is Prized

Ultra Ball cannot retrieve it. A Gladion already in hand can retrieve it directly.

Computer Search has an additional route:

`Computer Search -> inspect deck -> Raichu absent -> take Gladion -> play Gladion -> take Raichu`

The same Computer Search therefore changes role according to the hidden target zone. In an unprized state it is a direct Pokemon-access connector. In a Prized state it becomes a Supporter-access connector.

This is stronger than a static graph edge such as `Computer Search -> Alolan Raichu`. The any-card search combines information and material access in one action.

## Main result

Baseline assumptions:

- 60-card deck;
- valid seven-card opening;
- six Prize cards;
- one later random draw;
- 16 setup-eligible starters;
- 1 Alolan Raichu;
- 2 Gladion;
- 3 Ultra Ball;
- 1 Computer Search;
- 12 modeled disposable cards;
- two-card connector cost.

| Measurement | Exact probability |
| --- | ---: |
| Valid opening before conditioning | 90.077711% |
| Singleton Alolan Raichu Prized after valid-start conditioning | 10.052903% |
| Alolan Raichu already exposed in hand | 12.874837% |
| Two-card connector cost payable from modeled pool | 48.735852% |
| Ultra Ball + direct Gladion, Computer Search removed | 26.999305% |
| Add Computer Search as only another direct Raichu search | 30.170056% |
| Full zone-adaptive Computer Search | **30.623976%** |
| Zone-adaptive access if connector discard costs are ignored | 50.261185% |

The result is deliberately a direct-access component. It is not a claim that the full list sees Alolan Raichu only 30.62% of the time. Dedenne-GX, Crobat V, Squawkabilly ex, Forest Seal Stone, Quick Ball chains, Battle Compressor sequencing, repeated turns, Rescue Stretcher after discard, and other deck actions are outside this layer.

## Finding 1: a singleton non-starter is slightly more likely than 10% to be Prized after legal setup conditioning

Alolan Raichu is a Stage 1, so it does not help satisfy the opening Basic requirement.

With 16 setup-eligible starters, the exact post-mulligan probability that the singleton Alolan Raichu is in the six Prize cards is **10.052903%** rather than exactly 10%.

The correction is small in this 16-starter deck. It is still useful because this result composes with the repository's setup-conditioned Prize work instead of silently reverting to an independent uniform Prize model.

## Finding 2: Computer Search's zone-adaptive role is measurable

Treating Computer Search as merely a fourth direct Raichu search gives 30.170056% modeled access after one random draw.

Allowing the actual any-card fallback to Gladion raises that to **30.623976%**, an overall gain of **0.453921 percentage points**.

The average masks where the value lives. Conditional on Alolan Raichu being Prized:

- static Computer Search / direct Gladion access: **24.706757%**;
- zone-adaptive Computer Search access: **29.222076%**.

The any-card fallback therefore adds **4.515319 percentage points** inside the target-Prized states.

This is a concrete example of a connector whose best output depends on a hidden zone that becomes known during the connector's own resolution.

## Finding 3: Computer Search contributes through two different mechanisms

Removing Computer Search entirely leaves the modeled Ultra Ball + direct Gladion package at 26.999305%.

Adding Computer Search with its full semantics raises access to 30.623976%, a total gain of **3.624671 percentage points**.

Most of that gain comes from Computer Search acting as an additional direct target search when Raichu is in the deck. A smaller but strategically concentrated part comes from its ability to switch outputs and find Gladion when Raichu is Prized.

A graph representation should therefore preserve both the connector's output domain and the state discovered while resolving the search.

## Finding 4: discard payability remains the largest modeled gate

Under the strict 12-card discard policy, a two-card connector cost is payable from the exposed hand in **48.735852%** of baseline states.

If the discard costs are ignored while every other modeled constraint is kept, zone-adaptive access rises from 30.623976% to 50.261185%. The resulting **19.637208-point gap** is a property of this conservative DCI policy, not an estimate of full-game loss.

Discard-pool sensitivity after one random draw:

| Modeled disposable pool | Cost payable | Zone-adaptive access | Access if Raichu is Prized |
| ---: | ---: | ---: | ---: |
| 8 | 27.197529% | 23.593319% | 27.149862% |
| 11 | 43.503683% | 28.873930% | 28.707494% |
| 12 | 48.735852% | 30.623976% | 29.222076% |
| 15 | 63.068768% | 35.576846% | 30.673224% |
| 20 | 81.080688% | 42.224503% | 32.604622% |

The Prize-rescue side is less sensitive than the unprized direct-search side because a Gladion already in hand requires no discard cost.

## Finding 5: random exposure and connector access are separate axes

Using the 12-card discard policy:

| Extra random cards exposed | Raichu naturally exposed | Ultra Ball + direct Gladion | Static Computer Search | Zone-adaptive Computer Search | Access if Raichu is Prized |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | 11.199353% | 21.715422% | 24.097338% | 24.423367% | 24.938166% |
| 1 | 12.874837% | 26.999305% | 30.170056% | 30.623976% | 29.222076% |
| 2 | 14.550321% | 32.437630% | 36.358038% | 36.945326% | 33.501409% |
| 3 | 16.225805% | 37.879690% | 42.471170% | 43.191361% | 37.717065% |

Extra exposure helps by naturally finding the target, by finding connectors or Gladion, and by increasing the chance of accumulating two acceptable discard cards.

## Relation to K0/K1 and connector domination

The human-concepts prior describes `K0` as the state before the player has searched the deck and `K1` as the state after a search reveals the remaining deck and therefore the initial Prize composition.

This result shows a concrete reason that the transition itself can have option value. Computer Search does not merely move the player from K0 to K1. Because it searches for any card, it can choose a different material output after the target's zone becomes apparent.

The interaction is also a connector-domination problem. Computer Search could be spent on many other pieces in this list. This model only asks whether using it for Alolan Raichu access is feasible. It does not claim that doing so is strategically optimal compared with finding an Electrode-GX, an Energy-enabling piece, a draw engine, or another game-winning resource.

## Validation

The 60-card calculation is exact. It uses multivariate hypergeometric probabilities for the accepted opening and Prize state, then exact without-replacement averaging for later random exposure.

`results/raichu_prize_access/reproduce.py` additionally validates the implementation on a labeled 10-card deck. It independently enumerates every accepted three-card opening, every disjoint two-card Prize set, and every possible next draw, then evaluates the connector routes directly from card labels.

The labeled exhaustive result matches the category model to floating-point precision for:

- target-Prize probability;
- target naturally exposed;
- connector payability;
- Ultra Ball + direct Gladion access;
- static Computer Search access;
- zone-adaptive Computer Search access;
- no-cost access;
- target-Prized conditional access.

The complete conditioned state mass is also asserted to equal one.

## Limitations

This is a direct-access component, not a turn simulator.

It omits:

- Forest Seal Stone and its Pokemon V requirement;
- Dedenne-GX, Crobat V, and Squawkabilly ex draw effects;
- Quick Ball and other indirect draw-engine chains;
- Battle Compressor sequencing;
- the need to establish Pikachu or Ditto Prism Star before Alolan Raichu can evolve;
- evolution timing;
- Electrode-GX setup and Energy-count requirements;
- Bench capacity;
- ordinary Prize-taking;
- Rescue Stretcher after a Pokemon reaches the discard pile;
- Item, Ability, or Supporter lock;
- opponent interaction;
- competing uses of Gladion, Ultra Ball, Computer Search, or the discard cards;
- the possibility that Gladion itself retrieves a useful discard card before a later connector is paid.

The 12-card discard pool is intentionally conservative and state dependent. Different DCI policies produce different access rates, as the sensitivity table shows.

## Next useful work

The strongest continuation is to add the list's other real access layers while preserving their types:

1. Forest Seal Stone as an any-card connector gated by a Pokemon V and Tool attachment;
2. Quick Ball -> Dedenne-GX / Crobat V draw-engine transitions with hand discard consequences;
3. Battle Compressor as a deck-to-discard connector that both loads Extra Energy Bomb and changes future draw composition;
4. the actual Pikachu / Ditto Prism Star evolution requirement;
5. Electrode-GX plus enough Energy in the discard pile to make Electro Rain meaningful.

That would turn the present singleton-access kernel into a small ALS planner for Raichu/Electrode while preserving the state-dependent discard and Prize logic that this result isolates.
