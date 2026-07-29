---
name: weekly-essay
description: Proponer un tema de ensayo semanal (400–500 palabras) basado en el trabajo real, priorizando huecos conceptuales, decisiones arquitectónicas no triviales, o temas donde el usuario mostró fragilidad en el banco de preguntas. Usar cuando el usuario pida "proponeme un tema de ensayo para esta semana".
---

# Ensayo semanal

Sistema para forzar consolidación conceptual una vez por semana. El usuario
escribe 400–500 palabras sin abrir código, revisa contra la realidad, y
extrae una versión destilada hacia `learnings.md`. El agente **propone el
tema**, no lo escribe.

## Archivos involucrados

- `docs/essays/YYYY-WNN-{slug-tema}.md` — el ensayo escrito por el usuario
- `docs/essays/prompts/YYYY-WNN.md` — propuesta de tema generada por el agente
- `docs/learnings.md` — destino final después de revisión (versión destilada)

## Comando del usuario

| Comando (aprox.) | Acción del agente |
|---|---|
| `Proponeme un tema de ensayo para esta semana` | Crea `essays/prompts/YYYY-WNN.md` |

## Selección del tema

Cuando el usuario pide una propuesta, el proceso es:

1. Ejecutar `git log --since='7 days ago' --stat` para conocer commits y
   archivos tocados.
2. Leer las entradas más recientes de `docs/work_log.md`, `docs/learnings.md`,
   y si existe, `docs/interview_prep/weekly_drafts/YYYY-WNN.md`.
3. Identificar 3–4 temas candidatos según estos criterios de prioridad:
   - **Alta**: decisión arquitectónica no trivial tomada esta semana
     (ej. "por qué composición en vez de herencia en agents"); tema donde
     varias preguntas del banco quedaron marcadas como flojas o mal
     respondidas.
   - **Media**: concepto nuevo que apareció esta semana y aún no está
     consolidado (ej. primera vez tocando LangGraph, primera vez usando
     LLM-as-judge).
   - **Baja**: temas de rutina o cosas ya cubiertas en ensayos previos
     (buscar en `docs/essays/` para evitar repetir).
4. Elegir UN tema principal y proponer 1–2 alternativas.

## Formato de la propuesta

```markdown
# Tema propuesto — Semana YYYY-WNN

## Título sugerido
{título específico y técnico, evitar títulos vagos como "aprendizajes de la semana"}

## Por qué este tema
{2–3 oraciones conectando el tema con commits, decisiones, o huecos concretos
de la semana. Cita archivos o commits específicos.}

## Preguntas guía para arrancar la escritura
- ¿...?
- ¿...?
- ¿...?

## Longitud
400–500 palabras. Escribir sin abrir código ni notas. Después de escribir,
comparar contra el código y anotar lo que no se recordó.

## Alternativas si este no resuena
1. **{título alternativo 1}** — {una oración sobre de qué trataría}
2. **{título alternativo 2}** — {idem}
```

## Cierre del ciclo

El agente **no** escribe el ensayo ni lo revisa. El ciclo completo es:

1. Viernes: el usuario pide propuesta, escribe ensayo en 25–30 min.
2. Lunes siguiente: el usuario lleva el ensayo a un chat con el tutor humano
   o con un modelo externo para revisión estricta (10 min).
3. Aplicar correcciones y extraer versión destilada (5–10 oraciones) hacia
   `docs/learnings.md` con formato estándar.

## Anti-patrones

- No proponer temas vagos ("qué aprendí esta semana", "reflexiones")
- No proponer temas que ya tienen un ensayo previo (revisar `docs/essays/`)
- No escribir el ensayo por el usuario, ni siquiera un draft
- No proponer más de un tema principal — decisión, no menú de indecisión
- No inventar decisiones o commits que no existan; si la semana fue floja
  en commits, decirlo y proponer un tema de repaso conceptual de algo previo
  en vez de forzar novedad
