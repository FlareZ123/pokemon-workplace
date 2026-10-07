# Trainer search state adapter: compiled text to executable connector actions

## Question

Can the repository's conservative Trainer-search compiler be connected to the resource-constrained connector solver without turning card-text possibilities into unconditional graph edges?

Yes.

This result adds `tools/trainer_search_state_adapter.py`, which converts one `CompiledTrainerSearchProfile` into state-valid `ResourceActionProfile` choices while preserving the action and resource constraints already represented elsewhere in the repository.

Reproducer: `results/trainer_search_state_adapter/reproduce.py`

Validation workflow: `.github/workflows/validate-trainer-search-state-adapter.yml`

## Representation

The adapter consumes:

- literal search-output labels from the existing compiler;
- counts of matching targets currently remaining in the searchable deck zone;
- currently acceptable discard capacity;
- remaining Supporter and Stadium plays;
- typed Item, Tool, Supporter, and Stadium play locks;
- an explicit whole-hand discard count for effects such as Larry's Skill;
- explicit satisfaction of literal play conditions such as Rosa's Knock Out condition.

It returns a `ResourceConnectorType` suitable for `tools/resource_constrained_connectors.py`.

The shared resource vector is:

1. discardable cards;
2. remaining Supporter plays;
3. remaining Stadium plays.

A connector action is omitted when its play class is locked, its mandatory cost is unaffordable, its literal play condition is not explicitly satisfied, or none of its relevant targets remain in the deck.

## Conservative semantic boundary

The adapter uses exact compiled labels.

For example, it does not silently decide that a compiled `Trainer card` output satisfies an `Item card` demand. That relationship is true only after a separate type/subtype semantic layer has been validated.

This preserves the compiler's current design principle: widen semantic coverage through tested wording and type families rather than optimistic inference.

## Search quantities become state-valid subsets

The bundled rules allow restricted deck searches to select fewer than the printed maximum, including no cards, unless the effect searches for unrestricted arbitrary cards.

The adapter therefore emits every nonzero relevant subset that is both:

- allowed by the compiled search quantity; and
- supported by the current target counts.

This matters for multi-output cards.

### Secret Box

With one relevant Item, Tool, Supporter, and Stadium target in deck, three acceptable discard cards, and Items playable, Secret Box produces **15** state-valid nonzero output subsets.

The full action is:

- output `(1, 1, 1, 1)`;
- cost `(3 discards, 0 Supporters, 0 Stadium plays)`.

The exact resource solver confirms that one Secret Box can satisfy all four channels together in that state.

With only two acceptable discard cards, the adapter emits no Secret Box action.

Under Item lock, it also emits no action.

This is the intended distinction between card-text capacity and current-state executable capacity.

### Arven and shared Supporter capacity

One Arven can search one relevant Item and one relevant Pokémon Tool in the same action.

Two Arven copies therefore look capable of supplying two Items and two Tools if each copy is evaluated independently.

The adapter assigns each Arven use a cost of one Supporter play.

Regression result:

- two Arven copies, demand `(2 Items, 2 Tools)`, one remaining Supporter play: **not jointly feasible**;
- the same state with two Supporter plays available: **jointly feasible**.

Raw per-channel reachability is true in the one-Supporter state. The failure appears only after shared action capacity is allocated jointly.

This is a direct compiler-to-transition example of Supporter contention.

### Guzma & Hala

With one Stadium, Tool, and Special Energy target remaining, two acceptable discard cards, and one Supporter play, the adapter emits **7** useful profiles:

- one Stadium-only profile at cost `(0 discards, 1 Supporter)`;
- six profiles that use the optional two-card discard and retrieve at least one conditional Tool/Special Energy output.

The full paid action supplies all three channels at cost `(2 discards, 1 Supporter)`.

With no acceptable discard cards, only the Stadium-only profile remains.

Under Supporter lock, no profile remains.

The card therefore has a state-dependent action set rather than one permanent search-capacity vector.

### Target-zone depletion

If Arven has an Item target remaining in the deck but no Pokémon Tool target, the adapter emits only the Item output.

This connects the search-target zone-depletion work to executable connector actions: a compiled card may retain some axes while others disappear because their payloads are no longer in the searchable zone.

### Literal play conditions

Rosa's compiled profile carries a literal Knock Out play condition.

The adapter refuses to emit Rosa unless that condition is explicitly marked satisfied.

It does not infer the condition from unrelated state.

### Whole-hand discard effects

Larry's Skill is compiled with a whole-hand discard flag rather than a fixed integer discard cost.

The adapter therefore requires the caller to state how many cards would actually be discarded and compares that number with the current acceptable discard capacity.

In the regression state:

- whole hand after play = 4 cards;
- acceptable discard capacity = 3: no action;
- acceptable discard capacity = 4: action profiles become available.

This remains a scalar DCI approximation. A richer hand-identity model can replace it later.

## Validation

GitHub Actions run `37553677992` executed the reproducer on Python 3.13 and passed.

The validated output was:

```json
{
  "guzma_hala_full_profiles": 7,
  "guzma_hala_no_discard_profiles": 1,
  "larry_whole_hand_gate": true,
  "rosa_requires_explicit_condition": true,
  "secret_box_joint_feasible": true,
  "secret_box_state_valid_profiles": 15,
  "two_arven_one_supporter_joint_feasible": false,
  "two_arven_two_supporters_joint_feasible": true
}
```

The workflow checked out commit `d1b15ac91b3bd7199ed126fe78c75438f59431dd`, which also included the latest legality correction present on `main` at validation time.

## Relation to existing work

This adapter composes three existing layers:

1. `trainer_search_profile_compiler.py` extracts conservative text-level outputs and costs;
2. `trainer_search_state_adapter.py` turns those possibilities into state-valid action profiles;
3. `resource_constrained_connectors.py` allocates physical connector copies and shared resources jointly.

That separation keeps parsing, state legality, and optimization independently testable.

It also provides a concrete route toward the repository's larger semantic-compiler objective without requiring an arbitrary-card-text parser.

## Limits

The adapter currently models search output, not full card resolution.

Important omissions include:

- subtype/type-lattice reasoning between labels such as Trainer and Item;
- destination zones other than the compiled deck-to-hand search family;
- Bench requirements created by downstream Pokémon plays;
- Energy attachment and attack timing after a searched card reaches hand;
- VSTAR/GX/ACE SPEC once-per-game or deck-building constraints;
- card-identity-level DCI rather than a scalar acceptable-discard capacity;
- dynamic hand mutation across several sequential connector actions;
- positive strategic value from discarding a card as an objective in itself;
- conditional outputs whose strategic value depends on the order of later actions.

A Supporter found by a Supporter connector is also only represented as an obtained output. Whether that found Supporter can be played in the same turn is a downstream timing question and must still use Supporter-capacity semantics.

## Next useful work

The strongest next extension is a validated resource-type lattice plus destination-zone metadata.

That would allow a broad output such as `Trainer card` to satisfy narrower Item, Tool, Supporter, or Stadium requirements without double counting overlapping target pools.

After that, the adapter can be inserted into the unified state kernel so compiled Trainer text participates in the same Bench, Prize, lock, Energy, and action-window state transitions as hand-written actions.
