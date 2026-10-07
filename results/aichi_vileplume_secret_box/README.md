# Aichi Vileplume: Grand Tree to Secret Box first-turn core

## Question

What happens to Takahiro Ando's 2026 Aichi runner-up Vileplume Control first-turn Bunnelby line if the deck's ACE SPEC slot changes from Grand Tree to Secret Box?

The narrow endpoint is:

`Bunnelby in play + Technical Machine: Evolution + Jet Energy in hand`

before the attack sequence on the first turn going second.

This experiment studies immediate line feasibility. It does not value Grand Tree's later-turn evolution effect, matchup utility, or the future value of cards discarded to Secret Box and Guzma & Hala.

Implementation: `tools/aichi_vileplume_secret_box.py`  
Reproducer: `results/aichi_vileplume_secret_box/reproduce.py`

## Deck change

The published 60-card list is preserved card for card except:

`Grand Tree -> Secret Box`

Both cards are ACE SPECs, so this is a legal one-slot ACE SPEC substitution in the modeled deck.

Grand Tree cannot evolve a Basic during the player's first turn, so the existing first-turn ALS does not use its Stadium effect. Secret Box can be played during that turn when its three-other-card discard condition is payable.

## Transaction model

The planner preserves the relevant current card-text structure:

- Tag Call may obtain up to two TAG TEAM cards. It prioritizes Guzma & Hala for the line and may keep another TAG TEAM card as physical hand material.
- Secret Box leaves the hand, discards three other cards, then retrieves available Item, Tool, Supporter, and Stadium outputs.
- Guzma & Hala leaves the hand before its optional two-card discard. The optional discard unlocks the Tool and Special Energy searches.
- Secret Box outputs enter the hand before a later Guzma & Hala is played, so those searched cards can participate in the later two-card discard.
- Artazon and Fan Rotom can supply Bunnelby.
- Jirachi's Stellar Wish can select a relevant Trainer from the top five, including Secret Box in the variant.
- The first-turn Active policy matches the current Aichi planner: use Jirachi when available, otherwise avoid starting Bunnelby when another Basic is available.

The model uses exact compressed discard selections rather than a scalar hand-size check.

## 500,000-state paired result

Seed: `20261007`.

The same accepted opening permutation, Prize positions, first-turn draw, and Stellar-Wish top five are used for both ACE SPEC variants.

| ACE SPEC | Core success |
| --- | ---: |
| Grand Tree baseline | 70.6524% |
| Secret Box | 74.8094% |
| Increment from Secret Box | **+4.1570 pp** |

The approximate 95% Monte Carlo half-width is about 0.126 percentage points for the baseline, 0.120 points for Secret Box, and 0.055 points for the paired incremental event.

There were **20,785** Secret-Box-only successes and **0** Grand-Tree-only successes in the paired sample.

The zero-loss property is expected for this narrow endpoint. Grand Tree has no represented first-turn core action, while a Secret Box drawn into the same physical slot can still be discarded as an ordinary hand card when its own effect is unnecessary.

This monotonicity does not extend to later turns because Grand Tree's evolution effect then matters.

## Secret Box access and conversion

Secret Box was directly available in hand in 63,734 trials and available only through Jirachi's Stellar Wish in another 5,796.

Total represented first-turn Secret Box access was therefore:

**13.9060%**

The 20,785 incremental successes are **29.8936%** of states with represented Secret Box access.

The remaining accessible states were already baseline successes or still failed another requirement.

## The new successes identify the actual bottleneck

Every one of the 20,785 incremental successes began without Guzma & Hala or Tag Call in hand.

This means Secret Box is primarily adding an upstream connector into the established ALS rather than merely adding another copy of an already-reached payload.

Among the incremental successes:

| Jet Energy state before new searches | Incremental successes | Share of gains |
| --- | ---: | ---: |
| Jet Energy already in hand | 4,849 | 23.3293% |
| Jet Energy absent from hand | 15,936 | 76.6707% |

Secret Box cannot search Special Energy.

For the 76.67% majority where Jet Energy is absent, the successful structure therefore needs the Supporter output to obtain Guzma & Hala, after which Guzma & Hala obtains Jet Energy. Secret Box can simultaneously obtain TM: Evolution and Artazon, while its Item output can obtain Tag Call when useful.

A representative dependency is:

`Secret Box -> Guzma & Hala -> Jet Energy`

with Secret Box also covering some of the Tool, Stadium, and Item axes.

## Finding 1: raw output count is not independent demand capacity

The abstract `multi_channel_connector` result treats each Secret Box output as a distinct required channel.

The concrete Vileplume line violates that independence assumption.

The Supporter output is itself a connector into the missing Special Energy channel. The Item output can overlap the same Guzma & Hala access route through Tag Call. Tool and Stadium outputs can be direct payloads.

Secret Box therefore has four physical output categories here, while those categories occupy different levels of the dependency graph.

A connector model should distinguish:

- direct payload outputs;
- upstream connector outputs;
- redundant routes to the same downstream need;
- side payload that mainly becomes future action or discard material.

Counting four output labels as four independent solved needs would overstate the structure of this ALS.

## Finding 2: high discard cost can coexist with high immediate AMR

Secret Box requires three other cards to be discarded.

The first-turn setup state still gives it meaningful mechanical AMR because the opening hand, first draw, and delayed optional plays leave enough physical hand volume in many states. Secret Box then refills several Trainer categories before the later Guzma & Hala discard decision.

This does not make the discard strategically cheap.

The current planner treats all mechanically selectable discard cards as acceptable. It does not assign state-dependent DCI or future continuation value. A line that burns three cards for Secret Box and then two more for Guzma & Hala may be legal and immediately successful while being strategically poor in a full game.

## Finding 3: the ACE SPEC comparison remains unresolved at deck level

The +4.1570 point result is evidence about one first-turn endpoint.

Grand Tree has meaningful later-turn value because it can evolve a Basic through Stage 1 and Stage 2 after the first-turn restriction no longer applies. Replacing it also changes later lock establishment, recovery, Prize mapping, and resource preservation.

The current result therefore does not recommend Secret Box over Grand Tree for the deck.

It isolates a tradeoff:

- Secret Box improves the modeled first-turn core by creating another path into the connector chain.
- Grand Tree retains later-turn evolution value that this endpoint assigns zero credit.

A deck-level comparison needs continuation value after the first-turn state.

## Validation

The 500,000-state reproducer asserts the exact deterministic counts above.

It also asserts two structural checks:

- no paired baseline-only core success occurs;
- no incremental Secret Box success starts with Guzma & Hala or Tag Call already in hand.

The result is protected by `.github/workflows/validate-aichi-vileplume-secret-box.yml`.

## Relation to prior results

This experiment links several existing research threads:

- `aichi_vileplume_als/` supplies the concrete line and deck.
- `multi_output_slot_marginals/` shows abstractly that discardability can dominate direct redundancy for multi-output connectors.
- `trainer_search_transaction/` and `optional_discard_branch_witness/` motivate exact resolution and discard witnesses.
- `connector_domination/` warns that search access must be evaluated together with competing and downstream connector uses.

The concrete result adds an important qualification to the abstract multi-output model: output categories can be nested connectors rather than independent terminal needs.

## Next useful work

The next extension is continuation-aware ACE SPEC evaluation.

A useful model would assign value to the post-setup state, including:

- which cards were discarded by Secret Box and Guzma & Hala;
- whether Grand Tree remains available for later evolution;
- which Stage 2 lock pieces were established by the two TM: Evolution attacks;
- remaining Bench and Active-position geometry;
- matchup-dependent value of the established locks;
- Prize information and rescue requirements.

That would turn the current setup-probability comparison into an actual resource-policy comparison.
