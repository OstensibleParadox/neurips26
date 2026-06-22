"""MINE lower-bound estimator for the broad-probe fallback.

Implements the Donsker-Varadhan variational lower bound on mutual information
(Belghazi et al. 2018) with a neural critic, used when the narrow tool-vocab
probe yields a near-zero InfoNCE estimate. The broad probe passes the full
layer-L residual stream (shape `[d_model]` per sample) instead of the narrow
projection.

Status: scaffold with function signatures. Full implementation scheduled for
the next revision; only invoked if the primary narrow probe is underpowered.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def estimate(pairs_path: str | Path, out_path: str | Path) -> dict[str, Any]:
    """Full MINE estimation pipeline (broad probe).

    Steps:
        1. Load (Z_broad, A) pairs where Z_broad is the full residual stream.
        2. Train a neural critic T(z, a) via SGD on the Donsker-Varadhan bound:
               L = -E_joint[T(z, a)] + log E_marginal[exp(T(z, a))]
        3. Apply bias correction per Belghazi et al. 2018.
        4. Report I^LB in nats with cluster-bootstrap CI.
        5. Serialize to out_path.
    """
    raise NotImplementedError(
        "estimate_mi_mine: implementation scheduled for the next revision. "
        "See README.md for the fallback conditions."
    )


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pairs", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    try:
        result = estimate(args.pairs, args.out)
        print(json.dumps(result, indent=2))
    except NotImplementedError as e:
        print(f"not yet implemented: {e}")
        raise SystemExit(1)
