# Playing Box-fetched Nest Ball competes with Guzma & Hala payment

A Secret Box's immediate Item output can be a Nest Ball. It can put a
Basic Pokémon directly onto the Bench and thereby create a second
eligible Tool holder, but the played Nest Ball leaves the hand and
cannot then pay Guzma & Hala's optional two-card cost.

Exact bounded state model:
tools/secret_box_nest_ball_bootstrap.py

Physical labeled oracle:
results/secret_box_nest_ball_bootstrap/reproduce.py

Canonical Box-held hand has one Basic holder, P protected, D expendable
cards and no other relevant pieces. Searchable deck includes one copy
of each required Tool A/B, a Guzma & Hala, Special Energy, Item Nest Ball
and one/two Stadium copies. The terminal objective is A+B+Stadium+
Special Energy in hand with two distinct compatible Tool holders.

With one Basic already in play and at least one Basic searchable by
Nest Ball, minimum initial D is four when two Stadium copies exist
and five when only one Stadium exists. Without a searchable Basic
or without Nest Ball, this bounded one-holder line cannot satisfy the
two-holder condition. With two holders already available, the minimal
D falls to three when both Item and Stadium backups exist.

A concrete D=4 / S=2 witness: Box spends three starting D and
searches Nest Ball, Tool A, G&H, Stadium1. Play Nest Ball to Bench
the missing Basic, then play G&H, discarding the remaining D and
Stadium1, searching Tool B, Special Energy and Stadium2. Final state
has two Tool-capable holders and A+B+S+E acquired.

The two decisions for the searched Item are state-dependent:

- pay G&H with it and forgo its Bench-fetch utility;
- play it for the extra holder, forcing G&H payment from other hand
  resources.

The model enumerates the continuation rather than fixing the Item's
discardability.

The independent labeled-card oracle checks 192 configurations,
including multiple counts of Stadium, Item and Basic availability,
a G&H already in hand, and whether the Supporter play is permitted.
GitHub Actions run 37830758792 passed.

The related population-averaged hidden-Prize extension appears in
results/secret_box_nest_ball_k0/ and quantifies a +9.070392-point K0
recovery when Nest Ball play is allowed.

This is an acquisition-plus-holder-count model. Actual Tool
attachments, Stadium playing, Bench slot fullness, Tool-specific
restrictions, active locks, other Item search and opponent behavior
are excluded.
