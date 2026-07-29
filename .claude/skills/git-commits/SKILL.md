---
name: git-commits
description: Convenciones de commits del proyecto (Conventional Commits en inglés, scopes válidos, cuerpo del mensaje, cadencia y agrupación de cambios). Usar SIEMPRE antes de redactar un mensaje de commit o de decidir cómo agrupar los cambios de una sesión en commits.
---

# Convenciones de commits

Reglas permanentes (también en CLAUDE.md): commit por tarea lógica, 3–6 por
jornada, mensaje en inglés, y **nunca** commitear sin confirmación del usuario.

## Formato del mensaje

`<type>(<scope>): <description>` — Conventional Commits, en inglés.

**Types:**

- `feat` — new feature or capability
- `fix` — bug fix
- `refactor` — code change that neither fixes a bug nor adds a feature
- `test` — adding or updating tests
- `docs` — documentation only
- `chore` — tooling, dependencies, CI, config
- `style` — formatting, whitespace (no logic change)
- `perf` — performance improvement

**Scopes** (lowercase, una palabra, según capas y componentes del proyecto), como:
`domain`, `application`, `infrastructure`, `llm`, `retrieval`, `ocr`,
`privacy`, `estimator`, `api`, `agent`, `workflow`, `prompts`, `config`,
`deps`, `ci`, `tests`, `docs`, `mlops`, `notebooks`, `rag`.

**Ejemplos:**

```
feat(llm): add streaming support to provider
fix(retrieval): handle empty search results
refactor(agent): switch from inheritance to composition
test(domain): add unit tests for Protocol implementations
docs(architecture): add ADR for prompt loading decision
chore(deps): upgrade pydantic to v2.9
```

## Cuerpo del mensaje (opcional)

Es completamente opcional y debe colocarse únicamente en el caso en que el mensaje
del commit no sea lo suficientemente claro para entender los cambios. Procura solo
emplear el mensaje del commit y el cuerpo solo úsalo cuando los cambios son realmente
grandes o tocan muchos componentes y/o archivos.

Explica el **por qué**, no el qué — el diff ya muestra el qué. Línea en blanco
entre título y cuerpo. Si la decisión no es obvia, explícala:

```
refactor(agent): switch from inheritance to composition

Base class was creating coupling between ResearchAgent and PQRSAgent
because streaming behavior differed. Composition via agent_utils.py
keeps each agent self-contained.
```

En commits que tocan superficie LLM, documentar riesgo OWASP-LLM y mitigación
en el cuerpo (tabla de riesgos en CLAUDE.md).

## Cadencia y agrupación

- Commit por tarea lógica, no por archivo: un provider y sus tests son UN
  commit; el provider y un typo del README son DOS commits (feat + docs).
- Un commit debe poder revertirse sin romper otras cosas y tener un propósito
  claro.
- 3–6 commits por jornada típica: menos = commits demasiado grandes para
  revisar; más = micro-commits que ensucian el historial.
