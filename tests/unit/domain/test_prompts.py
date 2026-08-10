"""Unit tests for prompt registry."""

import pytest

from researchos.domain.exceptions import PromptNotFoundError
from researchos.domain.prompts import PromptTemplate


@pytest.mark.unit
class TestPromptRegistry:
    def test_load_system_prompt(self):
        prompt = PromptTemplate("system", "agent").render()
        assert "ResearchOS" in prompt

    def test_load_task_prompt_with_variables(self):
        prompt = PromptTemplate("tasks", "extraction").render(
            topic="LLM agents", paper_text="Test content"
        )

        assert "LLM agents" in prompt
        assert "Test content" in prompt

    def test_load_nonexistent_prompt_raises(self):
        with pytest.raises(PromptNotFoundError):
            PromptTemplate("tasks", "nonexistent_prompt").render()
