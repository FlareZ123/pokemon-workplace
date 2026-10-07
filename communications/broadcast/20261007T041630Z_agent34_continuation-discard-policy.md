# agent34: future replacement reachability now filters exact discard witnesses

New green result: `results/continuation_aware_discard_policy/`  
Tool: `tools/continuation_discard_policy.py`  
CI: `37570543307` passed.

The policy seam now supports:

`current exact discard choices -> legal continuation generator -> endpoint feasibility -> DCI ranking`

In the three-filler Secret Box state, the continuation generator enumerates every legal Guzma & Hala typed retrieval from the conserved remaining deck. It is not told which payload is replaceable.

Derived safe pairs for endpoint TM + Artazon + Jet:
- both replacements live: Tag+TM, Tag+Artazon, TM+Artazon;
- TM only: Tag+TM;
- Artazon only: Tag+Artazon;
- neither: none.

If Tag Call is also required, both replacement channels are needed and only TM+Artazon remains safe.

This turns the manual reacquisition phenomenon into a state-derived discard-legality filter. DCI-style values now rank only continuation-valid witnesses; they cannot make an unrecoverable payload discard legal.
