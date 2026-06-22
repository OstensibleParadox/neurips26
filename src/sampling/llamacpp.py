"""llama.cpp subprocess sampler (M4 Max / Metal backend)."""
import subprocess
from pathlib import Path


class LlamaCppSampler:
    def __init__(self, model_path: str, binary: str = "llama-completion"):
        self.model_path = model_path
        self.binary = binary

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
            cmd = [
                self.binary,
                "-m", self.model_path,
                "-p", prompt,
                "-n", str(n_tokens),
                "--temp", str(temperature),
                "--seed", str(seed + i),
                "-no-cnv",
            ]
            out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode()
            outputs.append(out.strip())
        return outputs
