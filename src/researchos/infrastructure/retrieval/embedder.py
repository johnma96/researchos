"""Local embedder — Sentence-transformer-based text embedding.

Loads from a local directory when ``EMBEDDING_MODEL_LOCAL_PATH`` is set in
the environment — useful on networks where HuggingFace is blocked.
Falls back to downloading ``EMBEDDING_MODEL`` from HuggingFace otherwise.
"""

from sentence_transformers import SentenceTransformer

from researchos.config import settings


class LocalEmbedder:
    """Thin wrapper around a ``sentence-transformers`` model.

    Provides ``embed`` and ``embed_batch`` helpers used by
    :class:`~researchos.infrastructure.retrieval.chroma.ChromaVectorStore`
    to vectorise documents and queries.

    Attributes:
        model: Loaded :class:`sentence_transformers.SentenceTransformer` instance.
    """

    def __init__(self) -> None:
        """Load the sentence-transformer model.

        Uses ``EMBEDDING_MODEL_LOCAL_PATH`` from settings when set (offline mode).
        Falls back to downloading ``EMBEDDING_MODEL`` from HuggingFace Hub.
        """
        source = settings.embedding_model_local_path or settings.embedding_model
        local_only = bool(settings.embedding_model_local_path)
        self.model = SentenceTransformer(source, local_files_only=local_only)

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
