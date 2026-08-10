---
name: git-workflow
description: Convenciones de git del proyecto — formato y cadencia de commits, scopes válidos, estrategia de ramas (GitHub Flow), duración máxima de ramas, pull requests y tags de versión. Usar SIEMPRE antes de redactar un mensaje de commit, decidir cómo agrupar los cambios de una sesión, crear o cerrar una rama, abrir un PR, o etiquetar el cierre de una versión del roadmap.
---

# Convenciones de git

Fuente única de verdad para todo lo relacionado con git en este proyecto.
`CLAUDE.md` solo conserva dos reglas de comportamiento (nunca commitear sin
confirmación, mensajes en inglés) y apunta a este archivo para el resto.

---

## Commits

### Formato del mensaje

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

**Scopes** (lowercase, una palabra). Los de este proyecto, agrupados por
naturaleza:

*Capas de la arquitectura:* `domain`, `application`, `infrastructure`

*Componentes:* `llm`, `retrieval`, `memory`, `bot`, `api`, `agent`,
`services`, `prompts`, `ingestion`

*Proyecto y tooling:* `config`, `deps`, `ci`, `tests`, `docs`, `scripts`,
`skills`, `system`, `roadmap`, `claude`

Si un cambio no encaja en ningún scope existente, es señal de que el cambio
toca demasiadas cosas o de que falta un scope. Preferí dividir el commit antes
de inventar un scope nuevo.

**Ejemplos reales de este repo:**

```
feat(bot): add Telegram bot adapter wired to vector-only RAG
feat(services): add hybrid search and its tests
refactor(services): split chunking from retrieval service
test(domain): add unit tests for Protocol implementations
docs(roadmap): mark T6-T10 complete, V1 done
docs(claude): document branching strategy and tag convention
chore(skills): add daily-closeout skill
chore(deps): upgrade pydantic to v2.9
```

### Cuerpo del mensaje (opcional)

Completamente opcional. Úsalo solo cuando el título no alcanza para entender
los cambios — típicamente cuando el cambio es grande, toca muchos archivos, o
la decisión detrás no es obvia.

Explica el **por qué**, no el qué: el diff ya muestra el qué. Línea en blanco
entre título y cuerpo.

```
refactor(agent): switch from inheritance to composition

Base class was creating coupling between ResearchAgent and PQRSAgent
because streaming behavior differed. Composition via agent_utils.py
keeps each agent self-contained.
```

Desde V4, los commits que toquen superficie expuesta al usuario (guardrails,
validación de input, PII masking, rate limiting) documentan en el cuerpo qué
riesgo de OWASP LLM Top 10 mitigan y cómo.

### Cadencia y agrupación

Commit por **tarea lógica**, no por archivo.

- Un provider y sus tests son UN commit.
- Un provider y un typo del README son DOS commits (`feat` + `docs`).

Criterio: un commit debe poder revertirse sin romper otras cosas y tener un
propósito único y claro.

**3 a 6 commits por jornada típica.** Menos significa commits demasiado grandes
para revisar; más significa micro-commits que ensucian el historial. Con
sesiones de una hora, 1 o 2 commits por sesión es normal.

**Nunca commitear sin confirmación explícita del usuario.** Al terminar una
tarea: "This task is complete. Suggested commit: `<mensaje propuesto>`. Shall
I proceed?"

---

## Ramas

### Estrategia: GitHub Flow

- `main` siempre en estado desplegable. Desde V4, GitHub Actions despliega a
  Cloud Run desde `main`.
- Las ramas de feature salen de `main` y vuelven vía pull request.
- **No hay `develop` ni `certification`.** Esas ramas existen en los proyectos
  corporativos de Protección porque hay ambientes reales de staging y
  certificación detrás. ResearchOS es un proyecto de un solo desarrollador sin
  esos ambientes, así que las ramas extra son ceremonia sin beneficio.

### Nomenclatura

`feature/v{N}-{tema}` en minúsculas con guiones.

Ejemplos: `feature/v2-langgraph-core`, `feature/v2-tools`,
`feature/v3-observability`, `feature/v4-guardrails`.

Para trabajo no atado a una versión del roadmap: `fix/{tema}` o
`refactor/{tema}`.

El nombre debe seguir siendo cierto al final de la rama. Si el alcance cambió
tanto que el nombre ya no describe el contenido, es señal de que la rama creció
más de lo que debía.

### Duración máxima: dos semanas

Si un entregable no cabe en dos semanas, se divide en varias ramas.

Precedente que motiva la regla: V1 se desarrolló en una sola rama
(`feature/v1-infrastructure-setup`) que acumuló 56 commits entre abril y agosto
de 2026 sin mergear. Eso convirtió una rama de feature en una rama de larga
vida, dejó `main` congelada en el esqueleto inicial durante cuatro meses, y
volvió el merge final un evento grande y difícil de revisar. El nombre además
quedó desactualizado: terminó conteniendo el pipeline RAG completo, el sistema
de estudio y el bot de Telegram.

Las ramas ahora corresponden a los bloques de dos semanas del roadmap.

### Crear una rama nueva

```bash
git checkout main
git pull origin main
git checkout -b feature/v2-langgraph-core
```

Siempre desde `main` actualizada. Nunca desde otra rama de feature.

---

## Pull requests

Cada rama cierra con un PR contra `main`, aunque haya un solo desarrollador.

La razón no es revisión de código — es registro. La descripción del PR
documenta qué se construyó, qué decisiones arquitectónicas se tomaron, qué
deuda queda conocida y qué quedó fuera de alcance. Ese registro es material de
portafolio y alimenta el banco de preguntas de entrevista.

### Estructura de la descripción

```markdown
## Scope
{una o dos frases: qué cierra este PR}

## What was built
{agrupado por capa o por componente, con rutas de archivo}

## Key architectural decisions
{cada decisión con su justificación, no solo el qué}

## Known debt
{cada ítem con la versión en que se piensa pagar}

## Out of scope
{lo que deliberadamente no se hizo}
```

### Merge

**Merge commit, no squash.** Los commits individuales son el historial de
aprendizaje del proyecto; aplastarlos destruye la trazabilidad de la que se
alimenta el banco de preguntas.

Después del merge, borrar la rama en remoto y local:

```bash
git branch -d feature/v2-langgraph-core
git push origin --delete feature/v2-langgraph-core
```

---

## Tags

Cada versión del roadmap cierra con un tag anotado sobre `main`:

```bash
git checkout main
git pull origin main
git tag -a v2.0.0 -m "V2: LangGraph agent + morning briefing"
git push origin v2.0.0
```

Los números siguen el roadmap (`v1.0.0` … `v5.0.0`), no versionado semántico
de un paquete publicado. No hay tags intermedios: una rama de dos semanas que
se mergea no genera tag; solo el cierre de versión.

---

## Anti-patrones

- **Push tardío.** Cerrar tarea → commit → **push** → recién entonces reportar
  que está terminado. Ocurrió dos veces en este proyecto que se reportó trabajo
  completo que no estaba en el remoto. Trabajo que no está en el remoto no
  existe para efectos de revisión.
- **Ramas que sobreviven su nombre.** Si al final de la rama el nombre ya no
  describe el contenido, la rama creció demasiado.
- **Squash en cierres de versión.** Destruye el historial de aprendizaje.
- **Commits de "wip" o "cambios varios".** Si no puedes nombrar el propósito
  del commit, el commit agrupa cosas que no van juntas.
- **Ramas salidas de otras ramas de feature.** Genera dependencias de merge
  innecesarias. Siempre desde `main`.
