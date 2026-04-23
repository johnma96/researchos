# infrastructure/retrieval/embedder.py
from sentence_transformers import SentenceTransformer


class LocalEmbedder:
    """Wraps a SentenceTransformer model for local CPU/GPU embedding.

    The model is downloaded on first use and cached by the sentence-transformers
    library. No network access is required after the initial download.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """Load the embedding model.

        Args:
            model_name: HuggingFace model identifier. Defaults to
                ``all-MiniLM-L6-v2`` (384-dim, fast, good quality).
        """
        self.model = SentenceTransformer(model_name)

    def embed(self, text: str) -> list[float]:
        """Embed a single text string.

        Args:
            text: Input text to embed.

        Returns:
            Dense vector as a list of floats.
        """
        return self.model.encode(text).tolist()

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Embed multiple texts in a single forward pass.

        Args:
            texts: List of input strings to embed.

        Returns:
            List of dense vectors, one per input string, preserving order.
        """
        return self.model.encode(texts).tolist()
