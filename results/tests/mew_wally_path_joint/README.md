# Opposing Path to the Peak: joint Wally/Tapu launch and actual escape payment

**Scope:** Exact hypothetical first-turn-going-second launch of the fully print-validated [Tapu Lele-GX Mew VMAX candidate](../../decks/mew-genesect-tapu-wally-counterfactual/), with **opponent Path to the Peak already in play** before our first turn. This is an adversarial opening *condition*; the model does not estimate how frequently the opponent has Path or wins games. Executable solver: [reproduce.py](reproduce.py). Windows CI [38302406035](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38302406035) passed both exact 60-card fraction regressions and independently coded fully labeled toy physical-deal oracles, with and without Path.

## Why this test

Tapu Lele-GX's Wonder Tag only works when played **from hand** onto Bench. `Path to the Peak swsh6-148` says Pokémon with Rule Boxes have no Abilities, which suppresses Wonder Tag. The candidate's **two Sky Field `xy6-89`** can displace Path with one Stadium play; **Field Blower `sm2-125`** can discard Path if Items are playable; **Lost Vacuum `swsh11-162`** can put Path in Lost Zone but only by first putting a separate card from hand into the Lost Zone. These are the same printed counter sources studied independently as a draw-engine remedy in [the existing Mew Path-escape result](../mew_genesect_path_escape/). Here the endpoint also requires Mew V starting Active in seven, DCE, Wally/Lele route, Genesect reaching Bench, and non-Prized search targets. The counter has to be usable without consuming another mandatory piece.

## Exact endpoint with one natural draw and six Prizes

The fully physical group partition is `Mew V4, Genesect V4, Mew VMAX3, Wally1, DCE4, VIP3, Quick4, Ultra4, Tapu Lele1, Sky Field2, Field Blower1, Lost Vacuum1, other28`, totaling **60**. All 13 named classes are distinguished in exact enumerated opening-seven plus natural draw, with six hidden Prize cards jointly sampled from the remainder. Starting Active Mew must be in initial seven. Wally-held routes do not need Wonder Tag or Path removal. Wally-absent routes use held Lele or search Lele **into hand** with Quick/Ultra, Bench it, Wonder Tag Wally from unprized deck, Wally evolves starter Mew to Mew VMAX from deck; Bench Genesect from hand/VIP/Ball, attach DCE, Cross Fusion Strike copies Techno Blast (210 before modifiers). A VIP **cannot** obtain Lele as a Wonder Tag trigger, because it benches directly.

| Available first-turn Path answers in the hand/draw (if needed) | Launch probability over all random initial sevens |
| --- | ---: |
| Path absent | **7.326281829134%** |
| Path present, answer only via Sky Field | **2.420967242312%** |
| Path present, Sky Field or Field Blower | **2.858767473600%** |
| Path present, Sky Field, Field Blower, or payable Lost Vacuum | **3.217190331194%** |

In the final Path-active case the exclusive decomposed contributions are:

| Mechanism | Absolute opening probability |
| --- | ---: |
| Wally held, no Wonder Tag needed | 1.444045204289% |
| Tapu Wonder Tag restored using Sky Field | 0.976922038023% |
| Extra restore from Field Blower, when no payable Sky route | 0.437800231288% |
| Extra restore from Lost Vacuum, when other routes unavailable | 0.358422857594% |
| **Total** | **3.217190331194%** |

Exact union with Path `16510599747617/513199346259600`, and no Path `636040115150563/8681622274224900`. Thus the opponent-Path scenario loses **4.109091497939 percentage points** of access from the unrestricted 7.326281829134%. The remaining Tapu-driven increment over natural-Wally paths is **1.773145126905 pp**, versus 5.882236624844 pp with no Path.

The **mechanical payment** policy reserves an original starting Mew, held DCE, any held Lele that must Bench, a held Genesect or required VIP, all Ball search cards consumed, and one counter-removal card. It chooses Quick ahead of Ultra when either can satisfy a required Basic search. Each Quick consumes one additional card, each Ultra two; Lost Vacuum consumes one *further, distinct* hand card into Lost Zone. A two-Ultra path with Sky held can fail because eight visible cards contain too few otherwise unreserved cards to pay four discards. Where Sky is held but physically unpayable under the search schedule, the planner checks another held counter and its payment independently. These are **legal payment feasibility** checks rather than strategic DCI approvals.

## Verification and limitations

The source target print data is already validated by the [full English 60](../../decks/mew-genesect-tapu-wally-counterfactual/) and its [own print-legality run](../mew_wally_tapu_variant/). The Path-specific kernel independently checks two micro populations (N=12 and N=14), exhausting original seven-equivalent hands, hidden Prize combinations, conditional natural draw, each physical individual's identity, and all disjoint exit categories, with Path off/on. Four exact rational equality tests pass. All simulations are reproducible locally with Python standard library and in pinned Windows GitHub Actions.

This **does not** model Trainers' Mail access to the counters or other routes to Wally, Genesect draw chains, Path replacement via card search, opponent Item lock or Active Ability lock, double search lines spanning subsequent turns, strategic discarded-card value, weak/strong opposing Pokémon HP, attack prevention, or actual match wins. In particular, an **opponent Iron Thorns ex Ability lock** that remains active cannot be removed merely by replacing Path, so the Tapu Wonder Tag bridge still fails. This is a conditional line availability benchmark that should eventually be integrated with a full-game policy.

Related research: [independent Path-counter source access](../mew_genesect_path_escape/) (larger probabilities due to no simultaneous attack prerequisites), [baseline Mew Wally attack](../mew_wally_first_attack/), and [Tapu candidate creation/legality proof](../mew_wally_tapu_variant/).
