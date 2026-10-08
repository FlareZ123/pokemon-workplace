# Aichi direct Guzma & Hala K0 policy

This result audits the optional two-card Guzma & Hala payment before the first full-deck inspection in the established Aichi Vileplume first-turn model.

Implementation: `tools/aichi_gnh_k0_policy.py`  
Regression: `reproduce.py`

## Clean subset

A state qualifies when Guzma & Hala is available directly after the first draw. Earlier information routes are excluded: Tag Call, Artazon, Fan Rotom, Capture Energy, and visible Jirachi. Starting Jirachi and Fan Rotom are excluded as well.

The outer run uses 10,000 accepted opening-plus-draw states with seed `20261007`. For each visible observation, all six Prize placements among the 52 unseen cards are integrated exactly with grouped hypergeometric weights.

The oracle may choose a different payment in each hidden Prize world. The K0 policy must use one payment for every hidden world with the same visible observation.

## Result

1,082 of 10,000 accepted starts qualify.

| Endpoint | Observations | Oracle | K0 |
| --- | ---: | ---: | ---: |
| Core | 98 | 96.799773953% | 96.799773953% |
| Pidgeot ex | 324 | 81.176229126% | 81.176229126% |
| Stoutland | 290 | 65.657784434% | 65.657784434% |
| Dual Stage 2 | 602 | 55.247011817% | 55.247011817% |
| Item lock | 329 | 46.025751078% | 46.025751078% |
| Item + Pidgeot | 651 | 26.030621548% | 26.030621548% |
| Item + Stoutland | 597 | 21.422305548% | 21.422305548% |

All seven endpoints have zero positive-gap observations and exact equality of weighted oracle and K0 success.

## Visible-slack explanation

After the first draw, removing the Active and the played Supporter leaves six cards. When the paid branch is useful, at least one of TM: Evolution or Jet Energy is missing. The richest endpoint then needs to preserve at most four visible cards: Bunnelby, two endpoint Basics, and the one present core resource. At least two cards remain available for the two-card payment.

When both TM: Evolution and Jet Energy are already present, the optional payment is unnecessary for these endpoints.

Hidden Prize placement can still change whether missing pieces are available. It does not improve the discard choice inside this immediate-endpoint abstraction.

See `results/discard_information_slack/` for the general payment-pressure boundary and the contrasting Secret Box local counterexample.
