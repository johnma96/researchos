"""Prompt registry — Loads and renders prompt templates from .txt files.

Prompts are stored as plain .txt files with {variable} placeholders,
rendered using Python's str.format(). No external dependencies (no Jinja2).

Usage:
    from researchos.domain.prompts.registry import load_prompt

    prompt = load_prompt("tasks", "extraction", topic="LLM agents", paper_text="...")
"""

from pathlib import Path

from researchos.domain.exceptions import PromptNotFoundError

PROMPTS_DIR = Path(__file__).parent


def load_prompt(category: str, name: str, **kwargs: str) -> str:
    """Load a prompt template from file and render variables.

    Args:
        category: Subdirectory (e.g., "system", "tasks").
        name: Filename without extension (e.g., "extraction").
        **kwargs: Variables to substitute in the template.

    Returns:
        Rendered prompt string.

    Raises:
        PromptNotFoundError: If the template file doesn't exist.
    """
    path = PROMPTS_DIR / category / f"{name}.txt"
    if not path.exists():
        raise PromptNotFoundError(f"Prompt not found: {path}")
    template = path.read_text(encoding="utf-8")
    return template.format(**kwargs) if kwargs else template
