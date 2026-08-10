# Prompt Management Guide

## Where prompts live

All prompts are in `src/researchos/domain/prompts/`:
- `system/` — System prompts that define agent behavior
- `tasks/` — Task-specific prompts (extraction, summarization, etc.)

## How to add a new prompt

1. Create a `.txt` file in the appropriate subdirectory
2. Use `{variable_name}` for dynamic content
3. Load with `PromptTemplate("category", "name").render(**kwargs)` where **kwargs are variables referenced in the template as {variable_name}.

## How to version prompts

Prompts are plain text files tracked in git. Use meaningful commit messages:
```
feat(prompts): add extraction prompt for medical documents
fix(prompts): improve citation instructions in system prompt
```

## How to evaluate prompts

Use the evaluation script with your golden dataset:
```bash
uv run python scripts/evaluate_agent.py
```

Compare results across prompt versions using Langfuse traces (V3+).
