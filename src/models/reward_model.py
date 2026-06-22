"""Reward model wrappers for CFSG experiments.

Three judge interfaces:
  RewardModel      — pointwise scorer (ArmoRM, Skywork, etc.)
  PairwiseJudge    — pairwise preference model (PairRM, etc.)
  RubricJudge      — LLM-as-judge with structured rubric (Claude API, etc.)
"""


class RewardModel:
    """Pointwise reward model: (prompt, response) -> scalar score."""

    def __init__(self, model_name: str):
        self.model_name = model_name

    def score(self, prompt: str, response: str) -> float:
        raise NotImplementedError

    def score_batch(self, pairs: list[tuple[str, str]]) -> list[float]:
        return [self.score(p, r) for p, r in pairs]


class PairwiseJudge:
    """Pairwise preference model: (prompt_a, resp_a) vs (prompt_b, resp_b) -> p_ij.

    p_ij in [0, 1] where p_ij > 0.5 means pair A is preferred.
    """

    def __init__(self, model_name: str):
        self.model_name = model_name

    def preference(
        self,
        prompt_a: str, response_a: str,
        prompt_b: str, response_b: str,
    ) -> float:
        """Returns probability that (prompt_a, response_a) is preferred."""
        raise NotImplementedError

    def preference_batch(
        self,
        pairs: list[tuple[str, str, str, str]],
    ) -> list[float]:
        return [self.preference(*p) for p in pairs]


class RubricJudge:
    """LLM-as-judge with a fixed rubric: (prompt, response) -> structured scores.

    Returns a dict of dimension scores plus a composite.
    """

    def __init__(self, model_name: str):
        self.model_name = model_name

    def judge(self, prompt: str, response: str) -> dict:
        """Returns dict with rubric dimension scores and 'composite_score'."""
        raise NotImplementedError
