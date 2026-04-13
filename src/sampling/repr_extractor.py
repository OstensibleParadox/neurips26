"""Hidden-state representation extractor for CFSG geometry.

Provides a unified representation space h_B for computing d_repr between
format variants. All judges share this geometry so the Lipschitz-failure
analysis uses a single coordinate system.
"""
import numpy as np
import torch


class ReprExtractor:
    """Extract hidden states from a HuggingFace model.

    Supports MPS (Apple Silicon), CUDA, and CPU. Uses the last hidden
    state, mean-pooled across tokens, as the representation vector.
    """

    def __init__(self, model_name: str, device: str = "auto", dtype=torch.float16):
        from transformers import AutoModel, AutoTokenizer

        if device == "auto":
            if torch.backends.mps.is_available():
                self._device = torch.device("mps")
            elif torch.cuda.is_available():
                self._device = torch.device("cuda")
            else:
                self._device = torch.device("cpu")
        else:
            self._device = torch.device(device)

        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        self.model = (
            AutoModel.from_pretrained(
                model_name,
                output_hidden_states=True,
                dtype=dtype,
            )
            .to(self._device)
            .eval()
        )
        self.model_name = model_name

    def extract(self, text: str) -> np.ndarray:
        """Returns mean-pooled last hidden state as a 1-D numpy array."""
        inputs = self.tokenizer(
            text, return_tensors="pt", truncation=True, max_length=4096
        ).to(self._device)
        with torch.no_grad():
            outputs = self.model(**inputs)
        last_hidden = outputs.hidden_states[-1]  # (1, seq_len, hidden_dim)
        return last_hidden.squeeze(0).mean(0).float().cpu().numpy()

    def extract_batch(
        self, texts: list[str], batch_size: int = 8
    ) -> np.ndarray:
        """Extract embeddings for a list of texts.

        Returns shape (N, hidden_dim).
        """
        all_embeddings = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            inputs = self.tokenizer(
                batch,
                return_tensors="pt",
                truncation=True,
                max_length=4096,
                padding=True,
            ).to(self._device)
            with torch.no_grad():
                outputs = self.model(**inputs)
            last_hidden = outputs.hidden_states[-1]  # (B, seq_len, hidden_dim)
            # Mean-pool over non-padding tokens
            attention_mask = inputs["attention_mask"].unsqueeze(-1)  # (B, seq, 1)
            masked = last_hidden * attention_mask.to(last_hidden.dtype)
            pooled = masked.sum(dim=1) / attention_mask.sum(dim=1).to(
                last_hidden.dtype
            )
            all_embeddings.append(pooled.float().cpu().numpy())
        return np.concatenate(all_embeddings, axis=0)

    @staticmethod
    def cosine_distance(a: np.ndarray, b: np.ndarray) -> float:
        """Cosine distance between two vectors: 1 - cos(a, b)."""
        dot = np.dot(a, b)
        norm = np.linalg.norm(a) * np.linalg.norm(b)
        if norm < 1e-12:
            return 1.0
        return float(1.0 - dot / norm)

    @staticmethod
    def pairwise_cosine_distance(embeddings: np.ndarray) -> np.ndarray:
        """Pairwise cosine distance matrix for a set of embeddings.

        Parameters
        ----------
        embeddings : shape (N, D)

        Returns
        -------
        Symmetric matrix of shape (N, N) with zeros on the diagonal.
        """
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        norms = np.maximum(norms, 1e-12)
        normed = embeddings / norms
        sim = normed @ normed.T
        return 1.0 - np.clip(sim, -1.0, 1.0)
