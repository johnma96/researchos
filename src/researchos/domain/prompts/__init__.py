"""Prompt template loader for ResearchOS.

Prompts are stored as plain .txt files using Python str.format() syntax
and organized into subdirectories by purpose:

    domain/prompts/
    ├── system/     ← system prompts that define agent persona/behavior
    └── tasks/      ← task-specific prompts (extraction, summarization, etc.)

No external dependencies — only Python stdlib. This keeps domain/ pure.

Variables in templates use str.format() syntax: {variable_name}

Keeping prompts as .txt files means they are:
    - Versionable and diffable in git
    - Editable without touching Python code
    - Testable independently from the rest of the system

Usage:
    from researchos.domain.prompts import PromptTemplate

    template = PromptTemplate("tasks", "extraction")
    rendered = template.render(topic="LLM agents", paper_text="...")
"""

from pathlib import Path

from researchos.domain.exceptions import PromptNotFoundError

_PROMPTS_DIR = Path(__file__).parent


class PromptTemplate:
    """Loads and renders a prompt template from a .txt file.

    Templates live in subdirectories under domain/prompts/:
        - system/   -> agent system prompts
        - tasks/    -> task-specific prompts

    Variables in templates use Python str.format() syntax: {variable_name}

    Example:
        template = PromptTemplate("tasks", "extraction")
        rendered = template.render(topic="LLM agents", paper_text="...")

    Args:
        category: Subdirectory name (e.g., "system", "tasks").
        name: Template filename without the .txt extension.

    Raises:
        PromptNotFoundError: If the template file does not exist.
    """

    def __init__(self, category: str, name: str) -> None:
        """Load the prompt template file from disk.

        Args:
            category: Subdirectory name under ``domain/prompts/``
                (e.g. ``"system"``, ``"tasks"``).
            name: Template filename without the ``.txt`` extension
                (e.g. ``"extraction"``).

        Raises:
            PromptNotFoundError: If the file ``{category}/{name}.txt``
                does not exist inside the prompts directory.
        """
        self._path = _PROMPTS_DIR / category / f"{name}.txt"
        if not self._path.exists():
            raise PromptNotFoundError(
                f"Prompt template not found: {category}/{name}.txt. "
                f"Expected file at: {self._path}"
            )
        self._template = self._path.read_text(encoding="utf-8")

    def render(self, **kwargs: str) -> str:
        """Render the template with the provided variables.

        Args:
            **kwargs: Variables referenced in the template as {variable_name}.

        Returns:
            The rendered prompt string.

        Raises:
            KeyError: If a variable referenced in the template is missing from kwargs.
        """
        return self._template.format(**kwargs) if kwargs else self._template

    def __repr__(self) -> str:
        """Return an unambiguous string representation of the template.

        Returns:
            String of the form ``PromptTemplate('<category>/<name>.txt')``
            relative to the prompts directory root.
        """
        return f"PromptTemplate('{self._path.relative_to(_PROMPTS_DIR)}')"
