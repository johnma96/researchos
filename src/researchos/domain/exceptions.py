"""Domain exceptions — Business-level errors for ResearchOS."""


class ResearchOSError(Exception):
    """Base exception for all ResearchOS errors."""


class PaperNotFoundError(ResearchOSError):
    """Raised when a paper cannot be found in any source."""


class IngestionError(ResearchOSError):
    """Raised when paper ingestion fails (download, parse, or embed)."""


class RetrievalError(ResearchOSError):
    """Raised when the retrieval pipeline fails."""


class GenerationError(ResearchOSError):
    """Raised when LLM generation fails."""


class RateLimitError(ResearchOSError):
    """Raised when an API rate limit is hit."""


class PromptNotFoundError(ResearchOSError):
    """Raised when a prompt template file is not found."""
