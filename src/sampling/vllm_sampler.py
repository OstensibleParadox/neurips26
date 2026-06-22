"""vLLM sampler for cluster (A100) inference."""

try:
    from vllm import LLM, SamplingParams
except ImportError:
    LLM = None  # not available on M4


class VLLMSampler:
    def __init__(self, model_name: str, **kwargs):
        if LLM is None:
            raise ImportError("vllm not installed")
        self.llm = LLM(model=model_name, **kwargs)

    def sample(
        self,
        prompt: str,
        n_tokens: int = 200,
        temperature: float = 0.9,
        n_samples: int = 20,
    ) -> list[str]:
        params = SamplingParams(
            temperature=temperature, max_tokens=n_tokens, n=n_samples
        )
        outputs = self.llm.generate([prompt], params)
        return [o.text for o in outputs[0].outputs]
