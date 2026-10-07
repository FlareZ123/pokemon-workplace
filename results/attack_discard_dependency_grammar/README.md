# Attack discard dependency grammar in paper Expanded

## Question

How often does attack text make a discard instruction a gate for later output, and how often does it instead leave later damage or effects governed by ordinary partial-resolution rules?

This extends `results/copied_attack_partial_resolution/`. That earlier result established one concrete copy family where an impossible effect-side Energy discard can be ignored while independent output still resolves. This result maps the wording that signals different dependency structures across a much broader discard-opening attack family.

## Rules basis

The Advanced Player's Rulebook establishes a general partial-resolution rule: an attack can be used when part of its instructions cannot be applied, with the applicable instructions still followed. Wording such as `Do X. If you do, do Y` creates an explicit dependency.

Section E-20 explains `If you do` and related `Then` wording. Once any part of the first half is performed, the dependent second half is applied. If none of the first half can be performed, the second half does not happen.

The rulebook's copied Crimson Blaster example provides a concrete contrast. Zoroark using Foul Play can execute Crimson Blaster without Fire Energy. The impossible discard is ignored and the attack still deals its independent 180 damage.

## Inventory

`tools/attack_discard_dependency_grammar.py` scans effectively legal Expanded attacks in two narrow wording families:

- text beginning with `Discard `;
- text beginning with `You may discard `.

Signatures are deduplicated by attack name, damage field, and normalized attack text. Dependency markers are recorded orthogonally because one attack can contain more than one marker.

### Mandatory discard-opening family

| Quantity | Count |
| --- | ---: |
| Print instances | 1,346 |
| Distinct signatures | 757 |
| No tracked dependency marker | 651 |
| `if you do` | 27 |
| `if you don't` or `if you do not` | 2 |
| `discarded in this way` | 75 |
| following `Then,` | 8 |

Marker combinations are:

| Combination | Signatures |
| --- | ---: |
| none | 651 |
| `discarded in this way` | 69 |
| `discarded in this way` + `Then,` | 5 |
| `if you do` | 26 |
| `if you do` + `discarded in this way` | 1 |
| `if you don't` | 2 |
| `Then,` | 3 |

### Optional discard-opening family

| Quantity | Count |
| --- | ---: |
| Print instances | 174 |
| Distinct signatures | 84 |
| No tracked dependency marker | 21 |
| `if you do` | 45 |
| `discarded in this way` | 19 |
| following `Then,` | 2 |

The optional combination counts are 42 `if you do` only, 3 `if you do` plus quantity coupling, 16 quantity-coupled only, 2 `Then,` only, and 21 with none of these markers.

## Four materially different structures

### Independent sequential resolution

Crimson Blaster begins with an Energy discard and then has independent damage text. It has none of the tracked dependency markers. The rulebook explicitly demonstrates that the damage still happens when the copied attacker has no Fire Energy to discard.

This shows why an engine cannot infer a prerequisite merely from sentence order.

### Explicit success gate

Rotom's Electribonus says to discard a Lightning Energy card from hand and then says `If you do, draw 3 cards.` The later draw is textually conditional on performing the discard.

A copied-attack or AMR model should encode this as a dependency edge from the discard outcome to the later output.

### Explicit failure gate

Passimian's Intentional Grounding and Barraskewda's Spiral Jet say to discard a resource and then state that, if the player does not, the attack does nothing.

Only two distinct signatures in the mandatory discard-opening family use this direct attack-failure form. It is strategically important because it turns the discard into a genuine execution gate.

### Quantity coupling

Photon Geyser and many similar attacks refer to Energy or cards `discarded in this way`. Their output depends on the realized discard quantity.

This is different from an all-or-nothing prerequisite. A zero-card result can make the variable component zero while other independent parts of the attack may still exist.

## Representation consequence

A useful attack-body representation should keep each instruction and its dependency relation instead of converting all discard text into one generic cost field.

For the wording family studied here, useful edge types include:

- sequential instruction;
- success-conditioned continuation;
- failure-to-nothing gate;
- quantity-coupled output;
- optional action;
- `Then` continuation requiring the first half to have occurred at least in part.

This representation is especially important for copied attacks because the selected attack body is rebound to the actual attacking Pokémon and current player's zones. A discard instruction that looks expensive on the source card can become impossible, cheap, or strategically desirable in the copier's state.

## Method

The scan uses the repository's Expanded-set filter and current print-level ban overlay. It intentionally matches only attacks whose normalized text starts with one of the two discard phrases. Marker detection uses exact regular expressions so `if you do` does not accidentally match `if you don't`.

The regression in `results/attack_discard_dependency_grammar/reproduce.py` pins all aggregate counts and verifies representative cases from the independent, success-gated, and failure-gated families.

## Limitations

The absence of these four tracked markers does not prove that every later clause is independent. Natural-language card text can encode dependencies through other constructions, punctuation, attack damage formulas, conditions earlier in the attack, or card-specific rules.

The `Then,` marker is also contextual. E-20 gives it dependency semantics for the relevant two-part construction, while this parser only identifies the wording and does not attempt a full grammar parse.

The scan does not cover discard instructions appearing later in an attack, discard costs embedded in Abilities or Trainers, or resource instructions using verbs other than discard.

## Next useful work

A stronger next layer would parse the complete attack body into ordered instructions and typed dependency edges. It could then evaluate the body against a concrete game state and report which outputs survive when each instruction succeeds only partially or cannot be applied.
