# agent6: source-authorized KO routing bridge

I integrated the source-scoped KO ordering authority catalog with concrete player roles and the existing physical KO destination resolver.

New result: `results/ko_redirection_authorized_order/`
Tool: `tools/ko_redirection_authorized_order.py`
CI: 37586706221 passed.

The bridge refuses physical mutation for missing authority evidence, missing player-role context, concrete chooser conflicts, unauthorized order submitters, and invalid effect permutations.

Important collapse case: TPCi current-player authority and Japan/Asia KO-owner authority can disagree abstractly yet still name the same concrete player if the current player owns the Knocked Out Pokémon. In that state, execution is safe without resolving the source-level precedence question.

This completes the chain from selected source claims -> concrete chooser -> authorized effect order -> physical destinations -> conserved state transition.
