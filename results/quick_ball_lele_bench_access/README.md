# Quick Ball to Tapu Lele-GX: setup Bench saturation sensitivity

## Question

How much does automatic setup Benching change the previously modeled Quick Ball to Tapu Lele-GX to Gladion connector when Bench saturation is included explicitly?

## Method

`tools/quick_ball_lele_bench_access.py` extends the same category-level exact enumeration used by the earlier Quick Ball and Tapu Lele-GX result. It keeps the previous setup-trigger rule: an opening-hand Tapu Lele-GX is preserved for Wonder Tag only when another starter can become Active.

The extension then applies a setup Bench policy to the other opening starters. Under bench-all, every extra ordinary starter is Benched up to the five-slot limit. Under reserve-one, at most four are Benched, guaranteeing one slot for Tapu Lele-GX.

The modeled package keeps the earlier four critical non-starters, two Gladion, four Quick Ball, and 12 dedicated disposable non-starters. Results are conditional on a valid opening and at least one modeled critical card being Prized.

## Result

| Total starters including Tapu Lele-GX | Bench-all access | Reserve-one access | Recovery from reserving one slot |
| ---: | ---: | ---: | ---: |
| 8 | 46.265689% | 46.265692% | 0.000003 pp |
| 12 | 48.569163% | 48.569324% | 0.000162 pp |
| 16 | 50.047816% | 50.049396% | 0.001580 pp |
| 20 | 51.034010% | 51.042131% | 0.008120 pp |
| 24 | 51.652809% | 51.682234% | 0.029425 pp |
| 28 | 51.976837% | 52.062067% | 0.085231 pp |

For the earlier 12-starter baseline, setup Bench saturation is mechanically real and quantitatively tiny: reserving a slot recovers only about **0.000162 percentage points** of current-window Gladion access.

This is useful evidence against over-weighting every newly identified constraint. The earlier model's setup-trigger loss and discard-payability effects are much larger than setup Bench saturation for this particular one-slot connector at 12 starters.

The correction grows in high-Basic stress cases because accepted openings contain many more extra starters. At 28 total starters, reserving one slot recovers about **0.0852 percentage points** in this fixed package.

## Why the correction is smaller than raw full-Bench probability

A full setup Bench does not automatically imply connector failure in the outcome metric. Some of those hands already contain Gladion directly, and some lack another required component of the Quick Ball route. Bench saturation only changes states where the Bench-dependent route would otherwise be the successful access path.

This demonstrates why constraint effects should be measured inside the full action model rather than added as independent failure percentages.

## Validation

`results/quick_ball_lele_bench_access/reproduce.py` checks the exact 12-starter values and a 28-starter stress case. The enumeration is deterministic and uses no Monte Carlo sampling.

## Limitations

The extension still stops at the accepted opening seven. It does not model later draws, other search cards, Bench expansion effects, opponent restrictions, or active cleanup. Other deck compositions can have different overlap between direct Gladion access and Bench-dependent routes.

The high-Basic rows are sensitivity tests rather than claims about a specific competitive deck.
