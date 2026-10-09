# K0/K1 reversal for voluntary G&H Tool thinning

## Question

The companion Aichi late-Stellar Wish payment experiment found a counterintuitive conditional state: discard a held TM: Evolution, search another copy with Guzma & Hala, and improve the remaining deck's Ticket density. Does that make the discard strategically reasonable before the player knows the Prize cards?

This separate **exact mathematical toy model** isolates that question. It does not claim to solve the actual Aichi first turn.

Files: tools/gnh_tool_thinning_information.py, reproduce.py and .github/workflows/validate-gnh-tool-thinning-information.yml. Successful CI run: https://github.com/FlareZ123/pokemon-workplace/actions/runs/37975938586.

## Model

A player holds one necessary Pokémon Tool and can either preserve it, or discard it to fund G&H's optional search and retrieve one backup copy. Among U uniformly exchangeable unseen cards are two distinguished cards: the backup Tool and a desired Ticket/Map. Exactly P unseen cards become Prizes; D=U-P cards remain searchable. If the backup is Prized, the replacement path cannot satisfy setup. After G&H's search, an unused Stellar Wish examines s uniformly selected deck cards. Other G&H payment material and setup requirements are assumed guaranteed.

At **K0**, Prize identities are hidden before deciding whether to discard the held Tool. At **K1**, a previous full-deck inspection reveals both distinguished cards' Prize status, so a player can choose whether to thin conditionally.

Define success as both retaining the Tool needed for setup **and** seeing the Ticket target with Stellar Wish. The exact outcomes (for 1 <= s <= D-1) are:

\[
\begin{aligned}
P(\mathrm{setup}\mid \mathrm{keep}) &= 1,\\
P(\mathrm{setup}\mid \mathrm{blind\ replace}) &= D/U,\\
P(\mathrm{setup\ and\ Ticket}\mid\mathrm{keep}) &= s/U,\\
P(\mathrm{setup\ and\ Ticket}\mid\mathrm{blind\ replace}) &= sD/[U(U-1)],\\
P(\mathrm{setup\ and\ Ticket}\mid\mathrm{K1\ oracle}) &= s/(U-1).
\end{aligned}
\]

The oracle keeps the held Tool unless **both** the replacement Tool and Ticket are known to be in the deck. When both are present, replacing the Tool thins one non-target and raises the subsequent Wish probability.

For P>1, D<U-1, so blind K0 replacement makes *joint* success strictly less likely even though replacement improves conditional target density when it succeeds. The K1 advantage over keeping the Tool is exactly s/[U(U-1)]. This positive value isolates the importance of knowing the location of a replacement before choosing a discard.

## Representative 60-card opening

For a simplified post-opening uncertainty U=52, six Prizes and a five-card Stellar Wish (D=46, s=5):

| Policy | Setup succeeds | Setup and Ticket hit |
| --- | ---: | ---: |
| Keep held Tool | 100% | 9.615384615% |
| Blindly replace held Tool | 88.461538462% | 8.672699849% |
| K1 adaptively replace only when safe | 100% | 9.803921569% |

The K1 information premium for the joint objective is **+0.188536953 percentage points** over keeping the Tool; blind replacement at K0 loses **0.942684766 points** of joint success and creates an **11.538461538%** chance of immediately losing the necessary Tool.

These figures are derived from a toy two-singleton Prize model. The real Aichi deck has multiple relevant Tools, other search options, other card-protection concerns and a more complicated sequence of partial/full information acquisition. The joint event is **not a game win rate**.

## Verification

The independent brute-force enumerator loops over labeled Prize subsets and averages exact within-world Stellar Wish success probabilities. All **164** enumerated small-deck parameter combinations agree exactly with the closed-form model (Python rational arithmetic). The regression also confirms the K0 direction flips for P=0, ties for P=1, and disfavors blind replacement for P>=2.

## Strategic implication

An endpoint-preserving payment chosen with full knowledge of simulated Prize composition is an upper bound on a pre-search decision. For the specific Tool-thinning play, this gap can reverse the direction of the decision. K1 information can make a safe local density improvement actionable; K0 uncertainty makes blindly sacrificing a guaranteed setup resource much worse under the modeled joint objective.

The next integration challenge is to classify actual Aichi G&H payment states by whether an earlier Tag Call, Fan Rotom or other full-deck search has already established K1. Only then should a full-game policy use an observed backup to authorize deliberate Tool replacement.
