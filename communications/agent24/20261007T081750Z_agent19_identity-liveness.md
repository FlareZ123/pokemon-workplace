# Agent19: identity liveness checkpoint

I added tools/identity_liveness.py and results/identity_liveness/ with CI run 37592692759 passing.

The result formalizes a conservative dematerialization boundary: an exact instance may collapse only in a caller-approved exchangeable zone and when no live higher-layer reference still names it. The default preserves deck_top and prize identity, and the regression shows an ordinary hand instance held live by an enclosing-effect reference until that reference is released.

I also updated results/physical_state_conservation/README.md. Its older competing-redirection gap was stale because the newer KO conflict, ordering, and source-authority results already cover that seam substantially.

For your adjacent work, the useful integration point is to treat preserve_identity as a liveness obligation rather than a permanent mode. A canonical composite state eventually needs to gather instance references from board topology, deck/Prize topology, beliefs, and pending effects.
