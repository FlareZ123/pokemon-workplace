# Complementary Item and Supporter gust endgame minimax

## Tested question

Do an Item gust and a Supporter gust together sometimes reach decisive Prize targets that two copies of either source cannot? The answer is **yes**, under an exact bounded six-Prize endgame model. The mixed allocation can also perform worse than a specialized pair.

## Model

The defender begins with 2–6 Pokémon, each worth one, two, or three Prize cards. Each KO takes one attacker turn. The defender chooses each next Active to maximize remaining attack turns. The attacker chooses to attack Active or spend at most one Item/Supporter gust per turn to attack a Bench target eligible for that source. A game ends after six Prizes or the last defender Pokémon is Knocked Out. No new cards or Pokémon enter, and all source-immunity states are fixed.

Eight target classes are enumerated. U1, U2 and U3 are ordinary one-, two- and three-Prize targets accepting either gust. I3 is a three-Prize Greninja V-UNION with Ninja Body, which prevents Item-play effects and can be selected by Supporter gust. S2 and S3 represent VSTAR and VMAX Pokémon protected against Supporters by Leafy Camo Poncho, still targetable by Item gust. B1 is Axew with Unnerve and B2 is Cetitan ex with Snow Camouflage; each blocks both Item and Supporter effects. Real prints are verified by the regression, including Prize rules.

## Exhaustive results

Every unordered type multiset of 2–6 Pokémon with total Prize value at least six is expanded by each distinct choice of starting Active. There are **10,107** distinct abstract boards. Three inventories are compared: two Items, two Supporters, and one of each, yielding **30,321** scenarios.

| Mixed inventory versus the better homogeneous inventory | Board classes |
| --- | ---: |
| Two fewer attacks | 32 |
| One fewer attack | 298 |
| Equal attack count | 8,786 |
| One additional attack | 869 |
| Two additional attacks | 122 |
| **Total** | **10,107** |

A mixed pair beats **both** homogeneous pairs in **330** distinct board classes; it loses to the better homogeneous pair in **991**. These are structural board counts, **not** tournament frequencies or metagame-weighted performance claims.

The numerical minimax solver is independently checked by a Boolean turn-deadline feasibility solver that requires every possible defending promotion to have a winning continuation. Every result is verified both at its computed deadline and one turn earlier.

## Smallest tactical witness

Opponent Active: one ordinary one-Prize Pokémon. Opponent Bench: Greninja V-UNION with Ninja Body (three Prizes, Item protection) and a Poncho-equipped VMAX (three Prizes, Supporter protection).

| Inventory | Worst-case attack turns |
| --- | ---: |
| Two Items | 3 |
| Two Supporters | 3 |
| One Item and one Supporter | **2** |

The mixed inventory Supporter-gusts Greninja and earns three Prizes. The defender can promote VMAX, which is now directly attackable, or the one-Prize Pokémon, after which an Item gust reaches VMAX. The attacker earns the final three Prizes next turn in either case.

With only Items, Greninja cannot be gusted. With only Supporters, the protected VMAX cannot be gusted. Adversarial promotion therefore delays the remaining three-Prize KO.

## Scope and evidence

This is a finite tactical representation of static source-specific protections. It omits Item and Supporter access consistency, V-UNION setup effort, remaining deck and Prize cards, legal source play permissions, Tool removal, Ability suppression, attack damage thresholds, healing, rebenching and additional actions. The source classes can coexist as a constructed legal board, without implying the combination is common competitively.

Code: [source-mix minimax](../../tools/gust_source_mix_minimax.py). Independent verifier and card audit: [reproduce.py](reproduce.py). All 30,321 scenarios passed GitHub Actions validation on the 2026-10-08 commit d577bd2.
