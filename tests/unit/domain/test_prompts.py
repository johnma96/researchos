"""Unit tests for prompt registry."""

import pytest

from researchos.domain.exceptions import PromptNotFoundError
from researchos.domain.prompts.registry import load_prompt


@pytest.mark.unit
class TestPromptRegistry:
    def test_load_system_prompt(self):
        prompt = load_prompt("system", "agent")
        assert "ResearchOS" in prompt

    def test_load_task_prompt_with_variables(self):
        prompt = load_prompt("tasks", "extraction", topic="LLM agents", paper_text="Test content")
        assert "LLM agents" in prompt
        assert "Test content" in prompt

    def test_load_nonexistent_prompt_raises(self):
        with pytest.raises(PromptNotFoundError):
            load_prompt("tasks", "nonexistent_prompt")
