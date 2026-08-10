from rank_bm25 import BM25Okapi

from researchos.domain.models import Document


class BM25Retriever:
    """BM25-based retriever implementing the Retriever protocol.

    Builds an in-memory BM25 index from a list of Documents at construction
    time. Retrieval is pure keyword matching — no embeddings, no vector store.
    Complements semantic search for exact term and acronym lookups.
    """

    def __init__(self, documents: list[Document], tokenizer=None) -> None:
        """Build the BM25 index from the provided documents.

        Args:
            documents: Pre-processed documents to index. Typically the same
                chunks stored in the vector store.
            tokenizer: Optional callable that takes a string and returns a
                list of tokens. Defaults to lowercased whitespace splitting.
        """
        self.documents = documents
        self._tokenize = tokenizer or (lambda text: text.lower().split())
        self._corpus = [self._tokenize(doc.text) for doc in documents]
        self.bm25 = BM25Okapi(self._corpus)

    async def search(self, query: str, k: int) -> list[Document]:
        """Return the top-k documents ranked by BM25 score.

        Defined as async to satisfy the Retriever protocol and allow uniform
        use with asyncio.gather alongside async retrievers like ChromaVectorStore.
        Executes synchronously in practice since no I/O is involved.

        Args:
            query: Natural-language query string.
            k: Number of top results to return.

        Returns:
            List of Document objects sorted by BM25 score descending, with
            the score field populated.
        """
        tokenized_query = self._tokenize(query)
        scores = self.bm25.get_scores(tokenized_query)
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:k]

        return [
            self.documents[i].model_copy(update={"score": float(scores[i])}) for i in top_indices
        ]
