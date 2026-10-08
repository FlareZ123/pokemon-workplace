# Boss's Orders versus Serena: target-restricted gust option value

## Question

The Trainer gust catalog distinguishes broadly player-selected effects such as Boss's Orders from restricted ones such as Serena's *switch a Benched Pokémon V* option. How do those target restrictions interact with the combinatorial value of having two gust actions across a six-Prize endgame?

## Source and abstraction

Bundled `resources/cards/en/swsh12.json` Serena `swsh12-164` says the Supporter can choose a discard-and-draw mode or switch an opposing Benched Pokémon V with their Active. Boss's Orders `me1-114` or `swsh2-154` can select any opposing Benched Pokémon. Both consume a Supporter use per turn under the normal rules.

`tools/typed_gust_target_minimax.py` implements the earlier one-hit KO, static opposing board, adversarial-promotion, six-Prize minimax with two kinds of **already available** targeted-gust resources:

- A **Boss** token can select any opposing Bench target.
- A **Serena** token can select only a target classified as a Pokémon V.

Only one token can be spent per attack turn, reflecting ordinary one-Supporter-per-turn quota. The player can also attack the current Active without spending a gust. Each opponent Pokémon is worth 1, 2, or 3 Prizes and is Knocked Out by one attack. The defender always selects the next Active to maximize the required attack turns.

This evaluates Serena's **gust mode only**. Its optional discard-and-draw mode is strategically important and omitted. The model additionally excludes attacks requiring multiple hits, searching for the Supporter, ability lock, other Supporter effects, opponent attacks, and new Bench placements.

## Source-state census

Use five hypothetical legal reward/eligibility classes:

- 1-Prize non-V;
- 2-Prize non-V;
- 2-Prize Pokémon V;
- 3-Prize non-V;
- 3-Prize Pokémon V.

This covers abstract Prize classes associated with one-Prize Pokémon, two-Prize ex/GX/V, three-Prize Mega ex and VMAX, while intentionally omitting exact attack and evolution stage distinctions. No class assumes a one-Prize Pokémon V.

Enumerate all multisets of 2 to 5 opposing Pokémon from these classes with total available Prize rewards at least six, and each distinct starting Active: **582 structural board classes**.

## Two restricted gusts are not equivalent to two unrestricted gusts

Compare optimal attack counts for two Boss tokens, one Boss plus one Serena, and two Serena tokens:

| Extra attacks needed compared with two Boss | Two Serena | One Boss + one Serena |
| ---: | ---: | ---: |
| 0 | 374 | 527 |
| 1 | 178 | 51 |
| 2 | 30 | 4 |
| **Total** | **582** | **582** |

Two Serena gust modes lose at least one attack turn relative to two Boss effects on **208 of 582** structural states. Replacing just one of the two broad gust options with Serena's restricted mode creates a penalty in **55 of 582** states.

A single Serena has the same pure gust-endgame value as a single Boss in **475** states and strictly less in **107**. These are unweighted counts over the artificial board taxonomy, not match-up frequencies or an argument for universally preferring Boss to Serena.

## Narrow-resource-first dominance

Suppose an opposing Benched Pokémon V is a legal target for both the Serena and Boss gust effects and the player holds one of each. Using Serena to gust that same target **weakly dominates** consuming Boss: the immediate board transition and Supporter usage are identical, while a retained Boss has a superset of Serena's future eligible targets.

The exact tool checks every possible forced first-turn targeted V switch across the 582 board classes, comparing the continuation costs using Boss versus Serena as the source. Spending Boss on a V target is **strictly worse** in **118** distinct board/target-state comparisons and is never better under the model's assumptions.

This is a source-selection-specific domination theorem in the gust-only abstraction. Serena's draw mode or other multi-axis strategic objectives can change the tradeoff outside that abstraction.

## Dramatic witness

Opponent Active: **1-Prize non-V**. Bench: **1-Prize non-V**, **3-Prize non-V**, **3-Prize Pokémon V**.

With one Boss and one Serena, the optimal route is two attacks:

1. Use Serena to gust and KO the three-Prize V target.
2. Preserve Boss, then gust and KO the three-Prize non-V target.

If instead the player spends Boss to gust the three-Prize V target on the first turn, the remaining Serena cannot gust any surviving non-V target. The opponent can keep promoting the one-Prize Pokémon, forcing **four attacks** in total. The incorrect source choice costs **two entire attack turns** even though the first gust selects the same target.

## Independent validation

`results/typed_gust_target_minimax/reproduce.py` checks every board for Boss budgets zero through two and Serena budgets zero through two (582 × 3 × 3): **5,238** independent Boolean attack-deadline checks against the minimax recurrence. It verifies both distributions, relative dominance, the 475 equality cases for one gust, every same-target source-choice comparison, and the explicit two-attack versus four-attack witness.

Reproduce: `python results/typed_gust_target_minimax/reproduce.py`.

## Implications and limits

Card search connectivity and counts of cards able to switch an opponent's Active should retain **target type restrictions**. The practical cost of using a broad gust on an overlapping target includes losing the option to hit a different, inaccessible type later.

A next bridge can evaluate explicit Bench Pokémon card profiles with legal evolution category and Prize rules, rather than synthetic labels, and add per-target HP and energy cost. A richer multi-axis model should restore Serena's discard-and-draw mode before making any decklist comparison.
