# Regidrago's Item-joint resource frontier after imposing an Energy gate

## Question and the core failure mode

The [first-turn Item joint-action study](../../regidrago_joint_launch/) found the experimental one-card +Dragapult ex / −Battle VIP Pass candidate improved simultaneous Regidrago V access and Dragapult ex discard (13.257301% to 19.536020% under D=0 protected discards). That result left out the Energy to use Regidrago VSTAR's Apex Dragon. How much of the same first-turn launch event also coincides with an ordinary two-turn Energy source window?

Multiplying the Item source probability by an unconditional Energy draw probability assumes independence that is false: held Items and held Energy compete for the same small opening hand slots and share unprized deck composition.

## Exact restricted source event

Fixed 60-card lists are the published 2026 Aichi Regidrago deck and [the fully legal experimental 60](README.md), with exactly +1 Dragapult / −1 VIP. Both retain 15 Basics, four Double Dragon Energy, four Grass Energy, and two Fire Energy.

- Seven-card opener contains a Basic; one natural draw enters the hand on turn one. Six face-down Prizes remove resources.
- First-turn Item search language is exactly the prior *D=0* planner: VIP benches a Regidrago V; Quick Ball and Mysterious Treasure may discard a held Dragapult; Battle Compressor may directly discard one from the deck. Each Item is consumed once. The held Dragapult can fund the Ball/Treasure payment, with zero anonymous safe-filler cards.
- The additional Energy event requires **at least one Double Dragon Energy and one further Double Dragon/Grass/Fire Energy among the first nine naturally exposed cards**. At most one of those nine is drawn on turn two, so a suitable Energy card is always available for a turn-one manual attachment. Double Dragon supplies two arbitrary Energy to a Dragon Pokémon; with the second Energy this meets Apex Dragon's Grass/Grass/Fire cost.
- The turn-two draw is an independent *pre-search reference draw* from the initial 46-card post-Prize deck. Modeled search Items only remove non-Energy sources, so their actual physical thinning cannot decrease the subsequent chance of drawing an Energy. This baseline reference is a conservative comparator for the restricted material window, although it is not a full turn-sequencing simulation.
- A first-Item search and its Dragapult discard payment must be committed with only K0 information. A subsequent deck search may reveal Prize composition before selecting the first search target and later Item lines. The independent K0 extension below verifies whether that initial commitment reduces the Energy-gated endpoint.

The exact category solver retains original Item search/prize classes and analytically integrates Double Dragon versus other compatible Energy inside the former anonymous filler category. For each opening class, the remainder of the six Prizes is hypergeometric among non-Regidrago/non-Dragapult cards. This yields an exact conditional probability of one more compatible Energy in a uniformly drawn future card without enumerating an 11-dimensional physical card group grid.

## Verified results

All numbers are percentages of legal Basic-valid seven-card openers:

| Event | Published 3 VIP, 1 Dragapult | Experimental 2 VIP, 2 Dragapult | Candidate change |
| --- | ---: | ---: | ---: |
| Regidrago V obtained and Dragapult discarded via Items | 13.257301009% | 19.536019594% | +6.278719 pp |
| Natural two-turn Energy pair (marginal) | 32.651714301% | 32.651714301% | 0 pp |
| **Same-deal three-channel intersection** | **3.275512337%** | **4.830454132%** | **+1.554941795 pp** |
| Naive product of the first two rows | 4.328736050% | 6.378845303% | Inaccurate |

Thus the independence product **overstates** the baseline intersection by approximately 1.053224 percentage points and the candidate by 1.548391 points. The experimental candidate retains a clear positive delta under this stricter source-only conjunction, while its total source event is substantially smaller than the Item-only metric.

The exact candidate-minus-published difference is `177253375533853/11399357591622000`; the original and proposed intersection fractions are respectively `43802912931679/1337284321420320` and `408575428938988601/8458323332983524000`.


## K0 nonanticipative first-Item policy

The [Energy-weighted first-action optimizer](../../../tools/regidrago_joint_energy_k0.py) enumerates exactly four physically distinct, payable first-Item actions that can exist under D=0: Battle Compressor, Battle VIP Pass, Quick Ball paid with a held Dragapult, and Mysterious Treasure paid with a held Dragapult. For every observable eight-card category hand it commits to **one action before knowing Prize placement**, then optimizes the searched target and remaining Item sequence once that first deck search reveals the deck.

It scores each hidden Prize world by the same exact turn-two natural Energy reference probability used in the three-channel study. Both complete 60-card lists retain an **exactly zero K0 first-Item information gap**: the original **3.275512337%** and candidate **4.830454132%** values remain unchanged. At every hand class with positive attainable payoff, a single first-Item action attains all Prize-world attainable payoff simultaneously. This refines the earlier Item-only universal-action witness to an Energy-weighted objective; it does **not** imply all pre-search decisions in a full game have zero information value.

An independent first-action regression checked every candidate action across thousands of small hand/deck material configurations against the previously verified K0 planner. The [manual Windows CI run passed](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38294434493), and its proof module is [joint_energy_k0_reproduce.py](joint_energy_k0_reproduce.py).

## Independent validation

[Finite category calculator](../../../tools/regidrago_joint_energy_gate.py), [separate literal physical-card Item/Prize/draw oracle](joint_energy_reproduce.py), and [manual Windows CI 38293991446, passed](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38293991446).

The oracle exhausts labeled opening sets, first natural draws, Prize subsets, and subsequent natural cards across six small toy configurations. It uses an independent physical Item DFS that consumes exact individual VIP/Quick Ball/Treasure/Compressor copies and pays with exact held Dragapult IDs. All Item-only marginal outputs also reproduce the existing joint Item module; all Energy-only marginals reproduce the independently enumerated natural Energy module. The full 60 fractions and the rejected naive independence product are regression-locked.

## What this does not yet establish

The candidate could still lose on average due to lower Regidrago V Basic access, Item-lock opponents, Bench availability, evolution and Energy acceleration access, timing of Trainer effects, or the lost Battle VIP Pass's other Basic-Pokémon targets. This source proxy does **not** model:
- Regidrago VSTAR availability/evolution;
- actual turn-two draw after shuffles and Item physical deck reductions;
- Supporter choices or first-turn/second-turn draw Abilities;
- Double Dragon Energy removal/lock and opposing attacks;
- actual attack copies, Prize-taking, win probability, or matchup spread.

**Next useful work:** enforce K0 first-Item action choice under the new Energy-weighted payoff, then add physical VSTAR acquisition and one future natural/Supporter draw to the same resource planner before making a deck selection.
