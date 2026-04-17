import chromadb

from researchos.domain.models import Document
from researchos.infrastructure.retrieval.embedder import LocalEmbedder
from researchos.paths import CHROMA_DIR


class ChromaVectorStore:
    def __init__(
        self,
        embedder: LocalEmbedder,
        collection_name: str = "papers",
        embedder_metadata: dict | None = None,
    ):
        self.embedder = embedder
        self.embedder_metadata = embedder_metadata or {"hnsw:space": "cosine"}
        self.client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        self.collection = self.client.get_or_create_collection(
            name=collection_name, metadata=self.embedder_metadata
        )

    async def search(self, query: str, k: int) -> list[Document]:
        """Search for the top-k most relevant documents."""

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
        """Insert or update documents in the store."""

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
        space = self.embedder_metadata.get("hnsw:space", "cosine")
        if space == "cosine":
            return 1 - (distance / 2)
        elif space == "l2":
            return 1 / (1 + distance)
        else:
            return 1 - distance
