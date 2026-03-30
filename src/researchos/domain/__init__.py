"""Domain Layer — Pure business logic.

Contains:
- models.py: Pydantic data structures (Paper, Chunk, Query, etc.)
- exceptions.py: Domain-specific error types
- interfaces.py: Protocols that infrastructure must implement
- prompts/: Prompt templates as versionable .txt files

RULES:
- ZERO external dependencies (only Python stdlib + Pydantic)
- All other layers depend on Domain, never the reverse
- NEVER import from application/ or infrastructure/ here
"""
