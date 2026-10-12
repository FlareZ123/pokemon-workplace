# Aichi fifth-place Mew VMAX: first-turn Wally / Techno Blast

**Evidence category:** exact physical combinatorics for a deliberately restricted legal execution route. Original published 2026 Aichi fifth-place Mew/Genesect 60, with no card substitutions. Reproduce with `python results/tests/mew_wally_first_attack/reproduce.py`.

## Executable line going second

1. Start **Mew V** `swsh8-113` Active from the initial seven. This specifically excludes starting another Basic and relying on a later switch.
2. By the first natural draw, have **Wally** `xy6-94` and one **Double Colorless Energy** `sm1-136` in hand.
3. Use Wally to search a non-Prized, still-in-deck **Mew VMAX** `swsh8-114`, evolving Mew V despite ordinary first-turn and just-played evolution limits. Wally excludes Pokémon-EX, which Mew V is not.
4. Have **Genesect V** `swsh8-185` on the Bench, either held or naturally drawn, or put directly from the deck onto the Bench using a held/drawn **Battle VIP Pass** `swsh8-225`. If VIP supplies Genesect, a copy must remain in the deck.
5. Attach DCE to Mew VMAX and use **Cross Fusion Strike**, copying Benched Genesect V's **Techno Blast** for **210 attack damage before defenses/modifiers**. Copies of attacks generally do not require the copied attack's printed Energy cost (rulebook C-18). The Mew VMAX attack has its own two-Colorless cost. DCE is distinct from Double Turbo Energy and has no 20-damage reduction.

**First player limitation:** Wally cannot be played by the player going first on their first turn under current turn-one Supporter restrictions. The documented attack is for the player going **second**.

## Exact launch probabilities

| Strict success event | Unconditional over shuffled initial seven | Conditional on valid initial seven |
| --- | ---: | ---: |
| Genesect already in hand by first natural draw, Mew V starter + Wally + DCE + VMAX in deck | 0.581386703842% | 0.747688414473% |
| Additional exclusive VIP route: no Genesect held, VIP held and Genesect remains in deck | 0.326307167880% | 0.419645112918% |
| **Union (disjoint)** | **0.907693871722%** | **1.167333527391%** |

The exact unconditional union is `18541777258637/2042734652758800`. Opening seven has a valid Basic with probability **77.757885850414%** (11 eligible Basics). Conditional on **at least one Mew V in the initial seven**, the strict union rate is **2.272076901274%**.

**Method:** group physical cards into disjoint (Mew V 4, Genesect V 4, Mew VMAX 3, Wally 1, DCE 4, VIP 3, other 41). Enumerate opening seven as multivariate hypergeometric counts and the first natural draw as a conditional one-card draw. The six Prize cards are an independent size-six sample of cards left after those observations; exchanging the order of the random Prize sample and natural draw preserves their joint law because no strategy conditions either sample. For each state require at least one VMAX in the search deck, and where VIP is needed, at least one Genesect there too. The last joint condition is calculated with inclusion-exclusion of all-Prized events. Summation is performed in exact `Fraction` arithmetic.

**Verification:** independent physically labeled exhaustive oracles reproduce both disjoint categories for two small-card population fixtures (N=10 and N=12). The main exact fractions are regression-locked. The printed card text and legality were checked against `resources/cards/en/` for IDs `xy6-94`, `swsh8-113`, `swsh8-114`, `swsh8-185`, `sm1-136`, `swsh8-225`. Official Pokémon material confirms Mew's Cross Fusion Strike and Genesect's Techno Blast interactions: https://www.pokemon.com/uk/features/sword-shield-fusion-strike-deck-strategy-mew-vmax-and-genesect-v ; official Expanded Wally turn-one precedent: https://www.pokemon.com/uk/features/a-deep-dive-into-the-2025-pokemon-tcg-expanded-format .

## Interpretation and limits

The model **deliberately omits** Genesect V's Fusion Strike System, Quick Ball, Ultra Ball, Trainers' Mail, VS Seeker recursion, prize recovery, opponent interference, and multiple sequential actions that increase reach. It excludes starting a non-Mew Basic and switching later. It also excludes any separate special first-turn attack exceptions. The narrow estimate is a certified restricted natural-hand/VIP line, **not** a comprehensive first-turn attack probability, match win percentage, or deck-strength ranking. Wally consumes the Supporter turn; actual setup must respect opponent lock conditions, Bench space, evolving legality and future turn continuation.

**Next work:** add source-aware Ball access with discard payment and ordered Genesect System draw windows, then test policy-dependent follow-on turns. Compare the actual outcome utility of early 210 damage with preserving Wally as a tactical option.

## Existing paid-Ball routes: mechanical feasibility versus strategic cost

The published 60 also contains four Quick Ball (`swsh1-179`) and four Ultra Ball (`swsh9-150`). [`paid_ball_routes.py`](paid_ball_routes.py) splits the 41-card "other" class into those eight paid Balls plus 33 remaining cards, maintaining the **same unmodified 60**. The exact first seven + first natural draw + six hidden Prize model then selects a disjoint route by precedence:

| First-turn route | Unconditional launch probability |
| --- | ---: |
| Genesect naturally held/drawn | 0.581386703842% |
| Extra VIP route when no Genesect held | 0.326307167880% |
| Extra Quick Ball route when neither above is available | 0.319438451878% |
| Extra Ultra Ball route when the first three are unavailable | 0.216912880689% |
| **Union** | **1.444045204289%** |

The union is exactly `167155400140607/11575496365633200`. The additional Quick and Ultra Ball lines are **legally payable**: out of the eight physically observed cards (seven opening, one draw), one is the starting Active Mew, and the line reserves Wally, one DCE, and its chosen search Item. At least **four other cards** remain in hand before the search, so one Quick discard or two Ultra discards can be paid without sacrificing those three named prerequisites. Whether any of those four is *strategically* expendable is **not** proved; a board/hand-sensitive DCI policy can make the search unattractive or fatally costly for later turns. Ball search of Genesect also requires at least one Genesect remaining in the post-Prize deck, and Wally's evolution search independently requires a VMAX there; the model checks both jointly.

Two independent physically labeled toy-population enumerations (N=11, N=12) confirm all four disjoint probabilities and the prize-state inclusion-exclusion formula. The larger result remains a **restricted mechanical-access** probability because Fusion Strike System, Trainers' Mail, sequential card draws, alternate starters/pivots, matchup disruptions, and opponent response are omitted. Even this enlarged value is not an estimated win percentage.
