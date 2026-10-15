# K1 Prize-composition-aware private-world sampler

**Evidence class:** pinned-engine source-aligned observation invariant and physical-card conservation test. **Format:** paper Expanded research. **Engine pin:** `3348ebdc898f175a2ed8f999133cd13d1afd01f5`.

## Research question

The initial K0 sampler mixes the player's uninspected deck and face-down Prizes before proposing a hypothetical world. After a legitimate complete deck search, a player with an accurately known decklist can infer the **multiset** of their remaining Prize cards. Under ordinary play, they still do not know which unrevealed Prize is at which face-down position. A K0 shuffle after that point forgets legitimately acquired knowledge and may change a play/hold decision for the wrong reason.

The Advanced Player's Rulebook supplied to the project, section **H. Deck**, authorizes looking at the contents of one's deck when searching. This result assumes a sufficiently complete search, accurate remembered deck inventory, and correctly tracked subsequent Prize exchanges. Card texts that limit the cards inspected do not automatically confer full K1 knowledge.

## Scoped implementation

The research adapter `simulation/twinleaf/k0-hidden-world-sampler.cjs` now exports separate factories:

- `makeK0HiddenWorldSampler(deepClone)`: existing policy model, draws hypothetical own deck and Prizes jointly.
- `makeK1HiddenWorldSampler(deepClone)`: **must only be called after Prize composition is genuinely known and remains tracked**; randomizes own unseen deck order and Prize *positions* independently, preserving the actual known Prize print multiset. The opponent's unknown hand/deck/Prize allocation is still sampled under the separately declared **open-opponent-list** assumption.

The K1 sampler deliberately accepts a state containing the real Prize cards, so **it is an information-privileged primitive**. Its caller is responsible for proving the transition from K0 to K1 using observed search history, not engine omniscience. It must never be selected merely because the authoritative simulator exposes all cards.

Both samplers copy the full Card object graph using `deepClone(state, [])` to avoid the pinned simulator's mutable-Card alias. Only hypothetical copies are reordered. The sampled State cannot be dispatched as authoritative game state.

## Test and interpretation

The pinned test `simulation/twinleaf/test-k0-hidden-world-sampler.cjs` now checks that: (1) K1 worlds with the same known Prize contents, public projection and full hidden inventories sample to identical card-name allocations despite opposite deck order and opponent hand allocations; (2) moving the same Prized Boss's Orders between secret Prize slots cannot change the K1 sampled state; (3) a K1 world with Boss Prized keeps it Prized, while the deck-Boss world keeps it in the deck; (4) sampled Card mutations do not reach the original state; and (5) unresolved prompt states are rejected. The existing K0 invariance regressions remain in the same test.

This demonstrates a **state-sampling prerequisite** and is not a complete observation-history implementation, a viable K1 match-playing bot, or evidence of improved deck strength. The current bounded runner continues to use only the labeled `sampled_k0` mode; K1 is intentionally not wired to matches until a trustworthy per-player search/Prize-knowledge tracker exists.

## Reproduction

Run the existing manually dispatched `.github/workflows/validate-twinleaf-blind-topdeck-search.yml` on the research revision to compile the pinned engine and execute the expanded `test-k0-hidden-world-sampler.cjs`.

Potential follow-up: record per-player search-inspection events and Prize modifications, maintain a conservative knowledge lattice (K0, exact-multiset K1, partial known-position Prizes), and test transitions against physical copy-conservation oracles.
