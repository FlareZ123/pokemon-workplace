# Agent6: overlapping effect-order authority

I extended the KO ordering work with `results/effect_order_authority_overlap/` and
`tools/effect_order_authority_overlap.py`.

The new resolver composes the existing evidence-backed authority cases without
inventing precedence. If all applicable cases identify the same concrete player,
the state is executable. If complete cases identify different players, the
resolver returns an explicit conflict.

Concrete unresolved overlap: current-turn Player A versus Player B owning a
Lost City/Persistent Cells Reuniclus, when an upstream semantic layer asserts
both the multi-Pokemon simultaneous-KO authority scope and the specific
Lost City/Reuniclus authority scope. The existing evidence claims A and B
respectively, so the repository now refuses to choose.

If the Reuniclus owner is also the current-turn player, both claims identify the
same player and the concrete order chooser is safe despite unknown rule
precedence.

CI run 37566187081 passed.
