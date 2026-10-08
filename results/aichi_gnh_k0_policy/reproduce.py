"""Reproduce the direct Guzma & Hala K0 policy audit."""

from aichi_gnh_k0_policy import ENDPOINTS, simulate


def main():
    trials = 10_000
    qualifying, results = simulate(trials)
    assert qualifying > 0
    assert tuple(result.endpoint for result in results) == ENDPOINTS
    for result in results:
        assert 0 <= result.k0_weight <= result.oracle_weight
        assert result.qualifying == qualifying
        assert result.trials == trials
        assert result.denominator > 0

    print(f"trials={trials}")
    print(f"qualifying={qualifying} ({qualifying / trials:.6%})")
    for result in results:
        print(result.endpoint)
        print(f"  unique_observations={result.unique_observations}")
        print(f"  positive_gap_states={result.positive_gap_states}")
        print(f"  positive_gap_observations={result.positive_gap_observations}")
        print(f"  oracle_conditional={result.oracle_conditional:.9%}")
        print(f"  k0_conditional={result.k0_conditional:.9%}")
        print(f"  conditional_gap_pp={result.conditional_gap * 100:.9f}")
        print(f"  overall_gap_pp={result.overall_gap * 100:.9f}")
        print(f"  half_width_95_pp={result.half_width_95 * 100:.9f}")
        print(f"  max_observation_gap_pp={result.max_gap * 100:.9f}")


if __name__ == "__main__":
    main()
