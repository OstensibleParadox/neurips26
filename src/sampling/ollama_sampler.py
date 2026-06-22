"""Ollama API sampler — same interface as LlamaCppSampler."""
import json
import urllib.request


# Bypass system proxy (e.g. Clash/V2ray on 127.0.0.1:7897) for localhost calls.
_opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))


class OllamaSampler:
    def __init__(self, model_name: str, base_url: str = "http://localhost:11434"):
        self.model_name = model_name
        self.base_url   = base_url

    def sample(
        self,
        prompt: str,
        n_tokens: int = 200,
        temperature: float = 0.9,
        seed: int = 42,
        n_samples: int = 1,
    ) -> list[str]:
        outputs = []
        for i in range(n_samples):
            payload = json.dumps({
                "model":  self.model_name,
                "prompt": prompt,
                "options": {
                    "num_predict": n_tokens,
                    "temperature": temperature,
                    "seed":        seed + i,
                },
                "stream": False,
            }).encode()
            req = urllib.request.Request(
                f"{self.base_url}/api/generate",
                data=payload,
                headers={"Content-Type": "application/json"},
            )
            with _opener.open(req, timeout=120) as resp:
                data = json.loads(resp.read())
            outputs.append(data.get("response", "").strip())
        return outputs
