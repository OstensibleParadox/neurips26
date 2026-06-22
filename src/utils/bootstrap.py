import numpy as np


def bootstrap_ci(data: list[float], n: int = 1000, alpha: float = 0.05) -> tuple:
    means = [np.mean(np.random.choice(data, len(data), replace=True)) for _ in range(n)]
    lo, hi = np.percentile(means, [100 * alpha / 2, 100 * (1 - alpha / 2)])
    return lo, hi


def cluster_bootstrap_ci(
    values: np.ndarray,
    cluster_ids: np.ndarray,
    statistic: str = "mean",
    n: int = 10000,
    alpha: float = 0.05,
) -> tuple[float, float, float]:
    """Bootstrap CI resampling entire clusters (content instances).

    Resamples at the cluster level to preserve within-cluster correlation.

    Parameters
    ----------
    values : 1-D array of observations.
    cluster_ids : 1-D array of cluster labels (same length as values).
    statistic : "mean" or "median".
    n : Number of bootstrap resamples.
    alpha : Significance level.

    Returns
    -------
    (point_estimate, ci_lo, ci_hi)
    """
    stat_fn = np.mean if statistic == "mean" else np.median
    unique_clusters = np.unique(cluster_ids)
    k = len(unique_clusters)

    # Build index for fast cluster lookup
    cluster_idx = {c: np.where(cluster_ids == c)[0] for c in unique_clusters}

    point = float(stat_fn(values))
    boot_stats = np.empty(n)
    for i in range(n):
        sampled = np.random.choice(unique_clusters, size=k, replace=True)
        boot_vals = np.concatenate([values[cluster_idx[c]] for c in sampled])
        boot_stats[i] = stat_fn(boot_vals)

    lo, hi = np.percentile(boot_stats, [100 * alpha / 2, 100 * (1 - alpha / 2)])
    return point, float(lo), float(hi)


def cluster_bootstrap_fn(
    stat_fn,
    arrays: list[np.ndarray],
    cluster_ids: np.ndarray,
    n: int = 10000,
    alpha: float = 0.05,
) -> tuple[float, float, float]:
    """Bootstrap CI for any statistic computed on cluster-resampled data.

    Resamples entire clusters (content instances), concatenates all
    observations from the sampled clusters, then calls stat_fn on the
    resampled arrays.  Correctly accounts for within-cluster dependence.

    Parameters
    ----------
    stat_fn : callable(*np.ndarrays) -> float
        Aggregate statistic.  Receives as many arrays as len(arrays).
    arrays : list of aligned 1-D ndarrays to resample together.
    cluster_ids : 1-D array of cluster labels (same length as each array).
    n : Number of bootstrap resamples.
    alpha : Significance level for CI.

    Returns
    -------
    (point_estimate, ci_lo, ci_hi)
    """
    unique_clusters = np.unique(cluster_ids)
    k = len(unique_clusters)
    cluster_idx = {c: np.where(cluster_ids == c)[0] for c in unique_clusters}

    point = float(stat_fn(*arrays))
    boot_stats = np.empty(n)
    for i in range(n):
        sampled = np.random.choice(unique_clusters, size=k, replace=True)
        idx = np.concatenate([cluster_idx[c] for c in sampled])
        boot_arrays = [a[idx] for a in arrays]
        boot_stats[i] = stat_fn(*boot_arrays)

    lo, hi = np.percentile(boot_stats, [100 * alpha / 2, 100 * (1 - alpha / 2)])
    return point, float(lo), float(hi)


def cluster_bootstrap_paired_diff(
    stat_fn,
    arrays_b: list[np.ndarray],
    cids_b: np.ndarray,
    arrays_a: list[np.ndarray],
    cids_a: np.ndarray,
    n: int = 10000,
    alpha: float = 0.05,
) -> tuple[float, float, float]:
    """Paired cluster bootstrap for stat(mode_b) - stat(mode_a).

    Restricts to content_ids present in BOTH modes, then resamples the
    same cluster IDs for both modes in each iteration.  This preserves
    the within-content pairing so the difference CI is tight.

    Parameters
    ----------
    stat_fn : callable(*np.ndarrays) -> float
    arrays_b / arrays_a : aligned arrays for Mode B / Mode A.
    cids_b / cids_a : cluster labels for Mode B / Mode A.

    Returns
    -------
    (point_diff, ci_lo, ci_hi)
    """
    common = np.intersect1d(np.unique(cids_b), np.unique(cids_a))
    if len(common) == 0:
        return float("nan"), float("nan"), float("nan")

    idx_b = {c: np.where(cids_b == c)[0] for c in common}
    idx_a = {c: np.where(cids_a == c)[0] for c in common}

    # Restrict to common clusters for point estimate
    common_mask_b = np.isin(cids_b, common)
    common_mask_a = np.isin(cids_a, common)
    point_b = stat_fn(*[a[common_mask_b] for a in arrays_b])
    point_a = stat_fn(*[a[common_mask_a] for a in arrays_a])
    point_diff = float(point_b - point_a)

    k = len(common)
    boot_diffs = np.empty(n)
    for i in range(n):
        sampled = np.random.choice(common, size=k, replace=True)
        bi = np.concatenate([idx_b[c] for c in sampled])
        ai = np.concatenate([idx_a[c] for c in sampled])
        val_b = stat_fn(*[a[bi] for a in arrays_b])
        val_a = stat_fn(*[a[ai] for a in arrays_a])
        boot_diffs[i] = val_b - val_a

    lo, hi = np.percentile(boot_diffs, [100 * alpha / 2, 100 * (1 - alpha / 2)])
    return point_diff, float(lo), float(hi)


def permutation_test(
    values: np.ndarray,
    labels: np.ndarray,
    cluster_ids: np.ndarray,
    n_perm: int = 10000,
) -> float:
    """Within-cluster permutation test for format effect.

    H0: format label has no effect on the score within each content cluster.

    Shuffles format labels within each cluster independently, then computes
    the between-label mean difference. Returns a two-sided p-value.

    Parameters
    ----------
    values : 1-D array of scores.
    labels : 1-D array of format labels (same length).
    cluster_ids : 1-D array of cluster identifiers.
    n_perm : Number of permutations.

    Returns
    -------
    Two-sided p-value.
    """
    unique_labels = np.unique(labels)
    if len(unique_labels) != 2:
        raise ValueError("permutation_test expects exactly 2 label groups")

    mask_a = labels == unique_labels[0]
    observed = abs(np.mean(values[mask_a]) - np.mean(values[~mask_a]))

    unique_clusters = np.unique(cluster_ids)
    cluster_idx = {c: np.where(cluster_ids == c)[0] for c in unique_clusters}

    count_extreme = 0
    for _ in range(n_perm):
        perm_labels = labels.copy()
        for c in unique_clusters:
            idx = cluster_idx[c]
            perm_labels[idx] = np.random.permutation(perm_labels[idx])
        perm_mask_a = perm_labels == unique_labels[0]
        perm_stat = abs(np.mean(values[perm_mask_a]) - np.mean(values[~perm_mask_a]))
        if perm_stat >= observed:
            count_extreme += 1

    return (count_extreme + 1) / (n_perm + 1)
