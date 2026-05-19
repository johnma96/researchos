"""Local embedder — Sentence-transformer-based text embedding.

Provides synchronous embedding of single texts and batches using a locally
downloaded ``sentence-transformers`` model (default: ``all-MiniLM-L6-v2``).
The model is downloaded on first use and cached by the ``sentence-transformers``
library in the system's HuggingFace cache directory.
"""
from sentence_transformers import SentenceTransformer


class LocalEmbedder:
    """Thin wrapper around a ``sentence-transformers`` model.

    Provides ``embed`` and ``embed_batch`` helpers used by
    :class:`~researchos.infrastructure.retrieval.chroma.ChromaVectorStore`
    to vectorise documents and queries.

    Attributes:
        model: Loaded :class:`sentence_transformers.SentenceTransformer` instance.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2") -> None:
        """Load the sentence-transformer model.

        Args:
            model_name: Name of the model to load from HuggingFace Hub or
                the local cache.  Defaults to ``"all-MiniLM-L6-v2"``
                (384-dimensional embeddings, fast inference).
        """
        self.model = SentenceTransformer(model_name)

    def embed(self, text: str) -> list[float]:
        """Embed a single text string into a dense vector.

        Args:
            text: Input string to embed.

        Returns:
            List of ``float`` values representing the embedding vector.
        """
        return self.model.encode(text).tolist()

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Embed a list of text strings in a single forward pass.

        Batching is more efficient than calling :meth:`embed` in a loop
        because the underlying model processes all texts in parallel.

        Args:
            texts: List of input strings to embed.

        Returns:
            List of embedding vectors in the same order as the input.
        """
        return self.model.encode(texts).tolist()
