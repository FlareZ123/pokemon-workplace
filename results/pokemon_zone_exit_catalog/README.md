# Pokémon zone-exit card-text catalog

## Question

How much of the current paper Expanded card pool explicitly uses the whole-board-
object exit shapes represented by `stack_zone_exit_conservation`?

This catalog searches the bundled card database conservatively. It recognizes
only wording families where the routing is explicit in card text.

Implementation: `tools/pokemon_zone_exit_catalog.py`  
Regression: `results/pokemon_zone_exit_catalog/reproduce.py`

## Legality

The scan uses the repository's paper Expanded legality model.

It first restricts cards to sets marked Expanded legal, then applies
`classify_effective_legality()`. This includes the repository's official ban
overlay, database bans, and explicit tournament-ban text.

That distinction matters here. Flapple `swsh2-22` and its Apple Drop reprints
still carry Expanded-legal metadata in the bundled database, while the official
2025 overlay bans those printings. The catalog excludes them.

## Conservative wording families

The scanner recognizes three routing families.

1. Pokémon stack to hand, attached cards to hand.
2. Pokémon stack to deck, attached cards to deck.
3. Pokémon stack to hand, attached cards to discard.

The first two require one literal effect clause that mentions a Pokémon, all
attached cards, and the destination.

The split hand/discard family requires the common two-part wording where the
Pokémon is put into hand and a parenthetical instruction discards all attached
cards.

The scanner does not infer routing from looser wording.

## Coverage

On the bundled card snapshot, after effective paper Expanded legality filtering,
the conservative catalog contains:

| Routing | Print effects | Unique card names |
| --- | ---: | ---: |
| Pokémon -> deck; attachments -> deck | 85 | 46 |
| Pokémon -> hand; attachments -> hand | 49 | 22 |
| Pokémon -> hand; attachments -> discard | 12 | 5 |
| **Union** | **146** | **73** |

These are effect rows rather than gameplay fingerprints. Reprints therefore
contribute multiple rows.

## Representative legal witnesses

### Scoop Up Cyclone `bw10-95`

Trainer rule text routes the selected Pokémon and all cards attached to it to
hand.

Compiled route:

`pokemon_destination = hand`  
`attachment_destination = hand`

### Cassius `xy1-115`

Trainer rule text shuffles one of the player's Pokémon and all attached cards
into the deck.

Compiled route:

`pokemon_destination = deck`  
`attachment_destination = deck`

### AZ `xy4-91`

Trainer rule text puts one Pokémon into hand and explicitly discards all cards
attached to that Pokémon.

Compiled route:

`pokemon_destination = hand`  
`attachment_destination = discard`

### Accelgor `bw5-11`

The Stage 1 attack Deck and Cover shuffles the attacking Pokémon and all cards
attached to it into the deck.

This is an important stack witness because the rulebook's C-02 semantics mean
the previous Evolution card also follows the evolved Pokémon.

### Swoobat `rsv10pt5-37`

Happy Return puts one Benched Pokémon and all attached cards into hand.

This shows that the same physical transition family can be reached through an
attack that targets another friendly board object.

## Why this is a catalog instead of a full parser

Destination routing is only one part of an executable action.

The matched effects can still differ in:

- self target versus another friendly target;
- opponent target;
- Active-only or Bench-only target restrictions;
- one target versus several targets;
- coin flips;
- optional branches;
- attack timing;
- Trainer action class;
- Knock Out replacement timing;
- follow-up instructions after the move.

The catalog preserves the original source kind, effect name, and normalized
text for those later semantic layers.

A state adapter should select only rows whose remaining target and timing
semantics have also been compiled.

## Relationship to whole-stack conservation

`stack_zone_exit_conservation` supplies the physical transition after a caller
has resolved:

- which Pokémon object leaves play;
- the Pokémon destination;
- the attachment destination;
- any required Active promotion.

This catalog supplies a validated card-text island for the two destination
fields. It does not yet choose the target object or timing window.

## Validation

The regression asserts the exact current catalog totals and representative
routes for Scoop Up Cyclone, Cassius, AZ, Accelgor, and Swoobat. It also asserts
that all four officially banned Apple Drop Flapple printings are absent.

Run:

`python results/pokemon_zone_exit_catalog/reproduce.py`
