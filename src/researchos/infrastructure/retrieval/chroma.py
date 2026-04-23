import chromadb

from researchos.domain.models import Document
from researchos.infrastructure.retrieval.embedder import LocalEmbedder
from researchos.paths import CHROMA_DIR


class ChromaVectorStore:
    """ChromaDB-backed implementation of the VectorStore protocol.

    Uses a local persistent Chroma database and a LocalEmbedder to convert
    text to vectors. The embedding space metric (cosine, L2, etc.) is
    configured via ``embedder_metadata``.
    """

    def __init__(
        self,
        embedder: LocalEmbedder,
        collection_name: str = "papers",
        embedder_metadata: dict | None = None,
    ):
        """Initialize the store and open (or create) the Chroma collection.

        Args:
            embedder: The embedder used to convert text to dense vectors.
            collection_name: Name of the Chroma collection to use.
            embedder_metadata: HNSW / distance-space settings passed to Chroma.
                Defaults to ``{"hnsw:space": "cosine"}``.
        """
        self.embedder = embedder
        self.embedder_metadata = embedder_metadata or {"hnsw:space": "cosine"}
        self.client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        self.collection = self.client.get_or_create_collection(
            name=collection_name, metadata=self.embedder_metadata
        )

    async def search(self, query: str, k: int) -> list[Document]:
        """Search for the top-k most relevant documents.

        Args:
            query: Natural-language query string.
            k: Number of results to return.

        Returns:
            List of Document objects sorted by relevance score (descending).
        """

        query_embedding = self.embedder.embed(query)
        retrieved_docs = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=k,
            include=["documents", "metadatas", "distances"],
        )

        results = [
            Document(
                doc_id=id, text=text, metadata=metadata, score=self._distance_to_score(distance)
            )
            for id, text, metadata, distance in zip(
                retrieved_docs["ids"][0],
                retrieved_docs["documents"][0],
                retrieved_docs["metadatas"][0],
                retrieved_docs["distances"][0],
                strict=False,
            )
        ]

        return results

    async def upsert(self, documents: list[Document]) -> None:
        """Insert or update documents in the store.

        Embeddings are computed in batch for all documents. Existing documents
        with the same ``doc_id`` are overwritten.

        Args:
            documents: Documents to index. Each must have a unique ``doc_id``.
        """

        vectors = self.embedder.embed_batch([doc.text for doc in documents])

        self.collection.upsert(
            ids=[doc.doc_id for doc in documents],
            embeddings=vectors,
            documents=[doc.text for doc in documents],  # ← guarda el texto
            metadatas=[
                doc.metadata if doc.metadata else {"source": "unknown"} for doc in documents
            ],
        )

    def _distance_to_score(self, distance: float) -> float:
        """Convert a Chroma distance value to a [0, 1] similarity score.

        Args:
            distance: Raw distance returned by Chroma (interpretation depends
                on the HNSW space configured in ``embedder_metadata``).

        Returns:
            Similarity score in [0, 1] where 1 is a perfect match.
        """
        space = self.embedder_metadata.get("hnsw:space", "cosine")
        if space == "cosine":
            return 1 - (distance / 2)
        elif space == "l2":
            return 1 / (1 + distance)
        else:
            return 1 - distance
