# Known negative reprint evidence

The reprint resolver now preserves explicit negative evidence as well as positive candidates.

Thirty historical Darkness Energy prints and Metal Energy prints are Special Energy cards with additional effects, while every current legal Expanded card with those names is Basic Energy. They therefore fail the functional-identity requirement structurally.

The Tournament Handbook also gives Rainbow Energy from Team Rocket number 17 as an explicit non-equivalent example because doing 10 damage and placing 1 damage counter are different mechanics. The alternate Team Rocket Rainbow Energy number 80 has the same gameplay fingerprint as number 17, so the same negative evidence applies to both prints.

The resulting known-negative set contains 32 prints:

- Darkness Energy: 15
- Metal Energy: 15
- Rainbow Energy: 2

This reduces the unresolved same-name semantic-review queue from 4,068 to 4,036 prints while leaving the 192 high-confidence positive candidates unchanged.

The classification is intentionally narrow. Other Rainbow Energy, Warp Energy, Recycle Energy, and Double Colorless Energy wording variants stay unresolved unless separate evidence proves or disproves current functional identity.

Reproduce with:

python results/reprint_negative_evidence/reproduce.py
