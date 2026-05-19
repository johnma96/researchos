"""Chroma vector store — Concrete implementation of the ``VectorStore`` Protocol.

Persists document embeddings to disk using ChromaDB's ``PersistentClient``.
All embedding computation is delegated to :class:`LocalEmbedder` so the store
remains agnostic to the embedding model.

To swap Chroma for another backend (e.g. Qdrant, Vertex Search), create a new
file in ``infrastructure/retrieval/`` that implements the same four-method
interface (``search``, ``upsert``) defined in
:class:`~researchos.domain.interfaces.VectorStore`.
"""
import chromadb

from researchos.domain.models import Document
from researchos.infrastructure.retrieval.embedder import LocalEmbedder
from researchos.paths import CHROMA_DIR


class ChromaVectorStore:
    """Persistent vector store backed by ChromaDB.

    Implements the :class:`~researchos.domain.interfaces.VectorStore` Protocol.
    Embeddings are computed locally via :class:`LocalEmbedder` and stored in a
    ChromaDB collection on disk at :data:`~researchos.paths.CHROMA_DIR`.

    Attributes:
        embedder: The :class:`LocalEmbedder` used to vectorise queries and documents.
        embedder_metadata: HNSW index configuration forwarded to the ChromaDB
            collection (e.g. ``{"hnsw:space": "cosine"}``).
        client: ChromaDB :class:`chromadb.PersistentClient` instance.
        collection: The active ChromaDB collection.
    """
    def __init__(
        self,
        embedder: LocalEmbedder,
        collection_name: str = "papers",
        embedder_metadata: dict | None = None,
    ) -> None:
        """Initialise the persistent vector store.

        Args:
            embedder: A :class:`LocalEmbedder` instance used for both query
                embedding and batch document embedding.
            collection_name: Name of the ChromaDB collection to use or create.
                Defaults to ``"papers"``.
            embedder_metadata: HNSW metadata for the collection
                (e.g. ``{"hnsw:space": "cosine"}``).  If ``None``, defaults
                to ``{"hnsw:space": "cosine"}``.
        """
        self.embedder = embedder
        self.embedder_metadata = embedder_metadata or {"hnsw:space": "cosine"}
        self.client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        self.collection = self.client.get_or_create_collection(
            name=collection_name, metadata=self.embedder_metadata
        )

    async def search(self, query: str, k: int) -> list[Document]:
        """Search for the top-k most relevant documents using cosine similarity.

        Embeds the query with :class:`LocalEmbedder`, queries the ChromaDB
        collection, and converts raw results to typed
        :class:`~researchos.domain.models.Document` objects with normalised
        relevance scores.

        Args:
            query: Natural-language search string.
            k: Number of top documents to return.

        Returns:
            List of :class:`~researchos.domain.models.Document` objects ordered
            by descending relevance score (best match first).
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
        """Insert or update documents in the ChromaDB collection.

        Embeds all document texts in a single batch call to the embedder,
        then calls ChromaDB ``upsert`` (insert-or-replace) so the operation
        is idempotent: re-ingesting the same paper does not create duplicates.

        Args:
            documents: List of :class:`~researchos.domain.models.Document`
                objects to persist.  Documents with an empty ``metadata`` dict
                receive a fallback ``{"source": "unknown"}`` entry to satisfy
                ChromaDB's non-null constraint.
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
        """Convert a ChromaDB distance value to a [0, 1] relevance score.

        ChromaDB returns distances whose interpretation depends on the HNSW
        distance space configured for the collection:

        - ``cosine``: distance ∈ [0, 2]; score = ``1 - distance / 2``.
        - ``l2`` (Euclidean): distance ∈ [0, ∞); score = ``1 / (1 + distance)``.
        - Anything else: score = ``1 - distance`` (assumes distance ∈ [0, 1]).

        Args:
            distance: Raw distance value returned by ChromaDB.

        Returns:
            Normalised relevance score where 1.0 is a perfect match and
            0.0 is maximally dissimilar.
        """
        space = self.embedder_metadata.get("hnsw:space", "cosine")
        if space == "cosine":
            return 1 - (distance / 2)
        elif space == "l2":
            return 1 / (1 + distance)
        else:
            return 1 - distance
