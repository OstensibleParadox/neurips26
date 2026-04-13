"""
Thin wrapper around statsmodels MixedLM for format-sensitivity analysis.

Fits models like:
    delta ~ format_pair + (1 | content_id)
    R_g ~ format + (1 | content_id)

Returns a plain dict so the caller does not need to understand
statsmodels internals.
"""
import logging
from typing import Optional

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def fit_mixed_model(
    df: pd.DataFrame,
    dep_var: str,
    fixed_effects: list[str],
    group_var: str,
    alpha: float = 0.05,
) -> dict:
    """Fit a linear mixed-effects model and return results as a dict.

    Parameters
    ----------
    df : DataFrame with all named columns.
    dep_var : Name of the dependent variable column.
    fixed_effects : Names of fixed-effect columns (will be dummy-coded
        if categorical).
    group_var : Name of the grouping variable for the random intercept.
    alpha : Significance level for confidence intervals.

    Returns
    -------
    dict with keys:
        converged : bool
        coefficients : dict[str, float]
        std_errors : dict[str, float]
        p_values : dict[str, float]
        ci_lo : dict[str, float]
        ci_hi : dict[str, float]
        random_effect_var : float  (variance of the random intercept)
        n_obs : int
        n_groups : int
        method : str  ("mixedlm" or "ols_clustered" if fallback)
    """
    try:
        return _fit_mixedlm(df, dep_var, fixed_effects, group_var, alpha)
    except Exception as exc:
        logger.warning("MixedLM failed (%s), falling back to OLS.", exc)
        return _fit_ols_fallback(df, dep_var, fixed_effects, group_var, alpha)


def _fit_mixedlm(
    df: pd.DataFrame,
    dep_var: str,
    fixed_effects: list[str],
    group_var: str,
    alpha: float,
) -> dict:
    from statsmodels.regression.mixed_linear_model import MixedLM

    # Build design matrix with dummy coding for categoricals
    formula_parts = []
    for col in fixed_effects:
        if df[col].dtype == object or pd.api.types.is_categorical_dtype(df[col]):
            formula_parts.append(f"C({col})")
        else:
            formula_parts.append(col)
    formula = f"{dep_var} ~ " + " + ".join(formula_parts)

    model = MixedLM.from_formula(formula, groups=group_var, data=df)
    result = model.fit(reml=True)

    ci = result.conf_int(alpha=alpha)
    return {
        "converged": result.converged,
        "coefficients": result.fe_params.to_dict(),
        "std_errors": result.bse_fe.to_dict(),
        "p_values": result.pvalues.to_dict(),
        "ci_lo": ci.iloc[:, 0].to_dict(),
        "ci_hi": ci.iloc[:, 1].to_dict(),
        "random_effect_var": float(result.cov_re.iloc[0, 0])
        if hasattr(result.cov_re, "iloc")
        else float(result.cov_re),
        "n_obs": int(result.nobs),
        "n_groups": int(result.model.n_groups),
        "method": "mixedlm",
    }


def _fit_ols_fallback(
    df: pd.DataFrame,
    dep_var: str,
    fixed_effects: list[str],
    group_var: str,
    alpha: float,
) -> dict:
    """OLS with clustered standard errors as a fallback."""
    import statsmodels.formula.api as smf

    formula_parts = []
    for col in fixed_effects:
        if df[col].dtype == object or pd.api.types.is_categorical_dtype(df[col]):
            formula_parts.append(f"C({col})")
        else:
            formula_parts.append(col)
    formula = f"{dep_var} ~ " + " + ".join(formula_parts)

    model = smf.ols(formula, data=df).fit(
        cov_type="cluster", cov_kwds={"groups": df[group_var]}
    )
    ci = model.conf_int(alpha=alpha)
    return {
        "converged": True,
        "coefficients": model.params.to_dict(),
        "std_errors": model.bse.to_dict(),
        "p_values": model.pvalues.to_dict(),
        "ci_lo": ci.iloc[:, 0].to_dict(),
        "ci_hi": ci.iloc[:, 1].to_dict(),
        "random_effect_var": float("nan"),
        "n_obs": int(model.nobs),
        "n_groups": df[group_var].nunique(),
        "method": "ols_clustered",
    }
