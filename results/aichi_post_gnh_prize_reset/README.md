# Aichi post-Guzma & Hala Prize-reset option value

## Question

How much first-turn endpoint value can a Prize-reset Item add to Takahiro Ando's 2026 Aichi runner-up Vileplume Control line when the reset is used after Guzma & Hala has already searched the deck?

This investigation studies a narrow sequencing window:

`Guzma & Hala search -> exact Prize knowledge -> optional one-time Prize reset -> Artazon / Fan Rotom setup -> Bunnelby + TM: Evolution`

Implementation: `tools/aichi_post_gnh_prize_reset.py`

Regression: `results/aichi_post_gnh_prize_reset/reproduce.py`

## Why this window is useful

The established Aichi ALS result already models the first-turn-going-second Bunnelby line around Guzma & Hala, Artazon, Fan Rotom, Jet Energy, and Technical Machine: Evolution.

A full deck search exposes the remaining deck to the player. With accurate deck knowledge, that makes the current Prize composition inferable before the reset decision. This is the K1-style information state described in `resources/human_concepts.md` and is also consistent with the deck-search procedure in the bundled advanced rulebook.

Guzma & Hala can materialize the Stadium, Tool, and Special Energy outputs before the reset. The experiment therefore protects Technical Machine: Evolution, Jet Energy, and Artazon when those outputs are searchable, then evaluates what a later Prize reset can repair downstream.

Two legal Expanded Items are compared:

- Redeemable Ticket, `sv9-156`: old Prize cards go to the bottom of the deck, then replacement Prizes are taken from the top of the pre-existing deck.
- Rotom Dex, `sm1-131`: old Prize cards are shuffled into the deck, then replacement Prizes are taken from that combined pool.

The destination difference means Redeemable Ticket protects the old Prize cards from being immediately selected again as replacement Prizes in this window.

## Counterfactual slot model

The experiment tags four cards that the established first-turn planner treats only as generic hand material:

- Team Yell's Cheer;
- Karen;
- Plumeria;
- Cassius.

For the 1-copy through 4-copy curves, the first `n` tagged slots are reinterpreted as copies of the reset Item.

This is a first-turn opportunity-cost abstraction. Those cards have later-game strategic value that this experiment does not score. The result is therefore evidence about immediate line value per occupied slot, rather than a deck recommendation.

Only one informed reset may be used in a trial. Extra copies increase access only. The reset Item must be naturally present in the accepted opening hand or first-turn draw. Stellar Wish does not select it, and no extra Item-search connector is added.

## Primary simulation

Primary run:

- 100,000 raw shuffled deck orders;
- seed `20261007`;
- 86,133 accepted openings containing an ordinary Basic;
- 60,682 accepted states where the named Guzma & Hala route could first materialize TM: Evolution and Jet Energy;
- the same underlying states are used for all 1-copy through 4-copy access curves.

The baseline endpoint rates reproduce the established Aichi model within ordinary Monte Carlo variation:

| Endpoint | Baseline |
| --- | ---: |
| Bunnelby double-TM core | 69.506461% |
| Pidgeot ex Stage 2 | 59.463852% |
| Stoutland Stage 2 | 48.689817% |
| Pidgeot ex + Stoutland | 41.966494% |
| Vileplume Item lock | 36.560900% |
| Item lock + Pidgeot ex | 23.753962% |
| Item lock + Stoutland | 19.630107% |

## Finding 1: one naturally accessed reset can have material endpoint value

With one reset copy, the reset card is naturally available in 8.290667% of accepted starts and 11.767905% of the post-Guzma-&-Hala core-ready states.

The informed one-reset lifts are:

| Endpoint | Redeemable Ticket lift | Rotom Dex lift |
| --- | ---: | ---: |
| Bunnelby double-TM core | +0.089397 pp | +0.088236 pp |
| Pidgeot ex Stage 2 | +0.925313 pp | +0.853331 pp |
| Stoutland Stage 2 | +1.178410 pp | +1.069277 pp |
| Pidgeot ex + Stoutland | **+1.524387 pp** | **+1.400160 pp** |
| Vileplume Item lock | +0.322757 pp | +0.301859 pp |
| Item lock + Pidgeot ex | +0.460915 pp | +0.428407 pp |
| Item lock + Stoutland | +0.541024 pp | +0.477169 pp |

For the dual Pidgeot-plus-Stoutland endpoint, Redeemable Ticket repairs 48.289812% of baseline failures in which one copy is naturally accessible in the modeled window. Rotom Dex repairs 44.354542%.

The approximately 95% binomial half-width for the one-copy Redeemable Ticket dual-endpoint lift is 0.082 percentage points on the accepted-start denominator.

## Finding 2: access scales strongly while marginal slot value declines

The dual-Stage-2 endpoint gives a useful copy-count curve:

| Copies | Natural reset access among accepted starts | Ticket lift | Rotom lift |
| ---: | ---: | ---: | ---: |
| 1 | 8.290667% | +1.524387 pp | +1.400160 pp |
| 2 | 15.925371% | +2.921064 pp | +2.644747 pp |
| 3 | 22.613865% | +4.113406 pp | +3.797615 pp |
| 4 | 28.731148% | +5.252342 pp | +4.816969 pp |

For RedeemXX›HXÚÙ]HİXØÙ\ÜÚ]™H[Ù[YX[Y[™Ú[[˜Ü™[Y[È\™H\›Ş[X][N‚‚˜
ÌKL
ÌKŒÎMË
ÌKŒNL‹
ÌKŒLÎH\˜Ù[YÙHÚ[Ø‚•H[[YYX]H[™Ú[˜[YH\™Y›Ü™HÚİÜÈ[Z[š\Ú[™ÈX\™Ú[˜[™]\›œÈ[™\ˆ\ÈÛ™K\™\Ù]ÛXŞK‚‚ˆÈÈš[™[™ÈÎˆ™YY[XX›HXÚÙ]™]Z[œÈH^XİY™\Z\ˆY˜[YÙB‚”™YY[XX›HXÚÙ]\ÈZXYÙˆ›İÛH^]]™\H™\ÜYÛÜHÛİ[[™[™Ú[[ˆHš[X\H[‹‚‚‘›ÜˆHX[TİYÙKLˆ[™Ú[HXÚÙ]Y˜[YÙHİ™\ˆ›İÛHÜ›İÜÈœ›ÛHŒLŒÈ\˜Ù[YÙHÚ[È]Û™HÛÜHÈÍLÍÌÈÚ[È]›İ\ˆÛÜY\Ë‚‚•\È›ÛİÜÈHØ[YH™\Z\ˆÙ[ÛY]H\İX›\ÚY[ˆ™\İ[ËÜš^™WŞ›Û™WÜ™XÛİ™\KØˆÛš^™\È\™H›İXİYœ›ÛH[[YYX]H™\XÙ[Y[[™\ˆ™YY[XX›HXÚÙ]Ú[H›İÛH^Ø[ˆÙ[XİH™]\›™YÛš^™HØ\™ÈYØZ[‹‚‚ˆÈÈš[™[™ÈˆH[™Ú[]\›Z[™\È™\Ù]ÛÛ™\œÚ[Û‚‚•HØ[YH™\Ù]XØÙ\ÜÈÛÛ™\È™\HY™™\™[HXÜ›ÜÜÈ[™Ú[Ë‚‚]Û™HÛÜK™YY[XX›HXÚÙ]ÛÛ™\Î‚‚‹HÍMM	HÙˆXØÙ\ÜÚX›HYÙ[İ[Û›H˜Z[\™\ÎÂ‹HLŒÍIHÙˆXØÙ\ÜÚX›Hİİ][™[Û›H˜Z[\™\ÎÂ‹HŒNL‰HÙˆXØÙ\ÜÚX›HX[\İYÙH˜Z[\™\ÎÂ‹HËÍIHÙˆXØÙ\ÜÚX›Hš[\[YH][K[ØÚÈ˜Z[\™\Ë‚‚•HY™™\™[˜ÙHÛÛY\Èœ›ÛH˜Z[\™HÜÛÙŞKˆHYÙ[İ[™İİ][™[™\ÈÙ[ˆ˜Z[™XØ]\ÙH]›Û][Ûˆ^[ØYÈÜˆ™\]Z\™Y˜\ÚXÜÈØØİ\HHš^™H›Û™KÚXÚH™\Ù]Ø[ˆ™\Z\‹ˆX[Hš[\[YH[™Ú[˜Z[\™\È\š\ÙHœ›ÛHİ\ˆÛÛœİ˜Z[È]™[XZ[ˆ[˜Ú[™ÙYH›İ][™Èš^™\Ë‚‚ˆÈÈÙXÛÛ™\ÙYYÚXÚÂHÙ\\˜]HL[Ü™\ˆ[ˆÚ]ÙYYŒŒL›ÙXÙYHØ[YH]X[]]]™H˜[šÚ[™Ë‚‚”Ù[XİY˜[Y\Î‚‚ŸÛÜY\È[™Ú[XÚÙ]Y›İÛHYŸKKNˆKKHKKNˆKKNˆŸHYÙ[İ^İYÙHˆ
ÌLNL
ÌÎNNMŸHİİ][™İYÙHˆ
ÌKŒÌÈ
ÌKŒMÎÎMˆŸHYÙ[İ^
Èİİ][™
ÌKMÍLˆ
ÌKMMÍHŸHš[\[YH][HØÚÈ
ÌŒÌMŒŒˆ
ÌŒÌHŸYÙ[İ^
Èİİ][™
ÍKLMÈ
ÍKŒNLNMˆ‚•HÙXÛÛ™[ˆ\ÈH›Ø\İ™\ÜÈÚXÚÈ˜]\ˆ[ˆHÛÛY\İ[X]K‚‚ˆÈÈİ˜]YÚXÈ[\œ™]][Û‚‚•\È\ÈHÛÛ˜Ü™]H^[\HÙˆ[™›Ü›X][ÛˆÜ™X][™ÈX]\šX[Ü[Ûˆ˜[YK‚‚•H™\Ù]Ø\™]Ù[ˆ\È˜[™ÛZ^š[™Ëˆ]È˜[YHÛÛY\Èœ›ÛHØZ][™È[[H[YXÚÈÙX\˜ÚY[YšY\ÈH˜\Ù[[™KY˜Z[[™Èš^™Hİ]K[ˆ\Ú[™ÈH™\Ù]Û›H[ˆÜÙHİ]\ËˆHØ[YHØ\™\ÙY›[™H\È›È™X\ÛÛˆÈ™\Ù\™H[™XYKYÛÛÙš^™HÛÛ™šYİ\˜][ÛœË‚‚•H^\š[Y[[ÛÈ^ÜÙ\ÈHÙ\]Y[˜Ú[™Èš[˜Ú\NˆÙX\˜ÚX›Hİ]]È]İ^›XH	ˆ[HØ[ˆ[İ™HÈ[™™Y›Ü™HH™\Ù]\™H›İXİYœ›ÛHH™\Ù]Ú[HİÛœİ™X[HXÚË\ÙX\˜Ú^[ØYÈ™[XZ[ˆ^ÜÙYˆHİ]H[Ù[]™X]È[™\]Z\™YØ\™È\ÈÛ™H[™Y™™\™[X]Y]˜Z[Xš[]HÙ]Z\ÜÙ\È\È[Z[™È\Ş[[Y]K‚‚ˆÈÈ[Z]][ÛœÂ‚•\È™[XZ[œÈHš\œİ]\›ˆSÈ^\š[Y[‚‚‹HH›İ\ˆİXœİ]]Yİ\Ü\œÈ]™H]\‹YØ[YH˜[YH]\È[[[Û˜[H[œØÛÜ™Y‚‹HÛ›HÛ™H™\Ù]Xİ[Ûˆ\È[İÙY]™[ˆÚ[ˆÙ]™\˜[ÛÜY\È\™HXØÙ\ÜÚX›K‚‹HH™\Ù]][H]\İ™H˜]\˜[H˜]Û‹ˆÙX\˜ÚXØÙ\ÜÈ›İYÚÙXÜ™]›ŞÜˆ[›İ\ˆ][HÛÛ›™XİÜˆ\Èİ]ÚYH\È™\İ[‚‹Hİ[\ˆÚ\Ú›ÛİÜÈH\İX›\ÚY˜[YY\›İ]HÛXŞH[™Ù\È›İÙ[XİH™\Ù]][K‚‹HH[Ù[[š\š]ÈH˜\Ù[[™HZXÚH[›™\‰ÜÈÚ[\YšYY™X]Y[Ùˆİ^›XH	ˆ[IÜÈÛËXØ\™\ØØ\™ˆ]™\Ù\™\ÈYXÚ[šXØ[[™›Û[YH[™Ù\È›İ\ÜÚYÛˆÒHÜˆÛÛ[X][Ûˆ˜[YHÈH\ØØ\™YØ\™Ë‚‹HÜÛ™[[\˜Xİ[Û‹][HØÚËXš[]HØÚËX]Ú\\ÜXÚYšXÈ™\Ù\˜][Û‹]\ˆ\›œË[™[YØ[YHš^™HZÚ[™È™[XZ[ˆİ]ÚYHØÛÜK‚‹H[ÛHØ\›È\İ[X]\È]™HØ[\[™È\œ›Ü‹ˆHÙXÛÛ™ÙYYÚXÚÜÈ\™Xİ[Ûˆ[™\›Ş[X]HØØ[K‚‚ˆÈÈ™^\ÙY[ÛÜšÂ‚•Hİ›Û™Ù\İÛÛ[X][Ûˆ\ÈÈÛÛ›™XİH™\Ù]][HÈÙXÜ™]›Ş	ÜÈ][Hİ]][™™X]H][HÛİ\ÈHÛÛ\İYÛÛ›™XİÜ‹ˆ]Ûİ[\İÚ]\ˆÙX\˜ÚX›H™\Ù]XØÙ\ÜÈÜ™X]\È[›İYÚÜ[Ûˆ˜[YHÈ\İYH\ÜXÚ[™ÈYÈØ[Üˆ[›İ\ˆ][Hİ]][ˆHİ]\ÈÚ\™HÙXÜ™]›Ş\È[™XYH\ÙY‚‚HÙXÛÛ™ÛÛ[X][Ûˆ\È™\X]YÌK\™\Ù]Ù\]Y[˜Ú[™ËˆY\ˆHš\œİ™\Ù]H]\ˆXÚÈÙX\˜ÚØ[ˆ™]™X[H™]Èš^™HÛÛ\ÜÚ][Û‹ˆ][\HXØÙ\ÜÚX›H™\Ù]ÛÜY\ÈÛİ[[ˆ]™HXİ[Ûˆ˜[YH™^[Û™Ú[\HXØÙ\ÜÈ™Y[™[˜ŞK‚