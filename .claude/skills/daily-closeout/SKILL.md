---
name: daily-closeout
description: Cerrar la jornada de trabajo — revisar la última entrada de learnings.md por errores conceptuales o de redacción, generar entrada nueva en work_log.md basada en commits reales y archivos modificados del día. Usar cuando el usuario indique "cerremos la jornada", "he finalizado el día", "fin de jornada" o variantes similares.
---

# Cierre de jornada

Skill genérica para cerrar el día de trabajo de forma disciplinada en cualquier
proyecto de código: revisar el último aprendizaje registrado, sintetizar el
work_log desde el trabajo real (git), y dejar todo commiteado. Portable entre
proyectos — no depende de la temática específica del repo.

## Archivos involucrados

- `docs/work_log.md` — bitácora diaria del proyecto (obligatorio)
- `docs/learnings.md` — registro de aprendizajes (opcional; si no existe, se
  saltea la revisión conceptual)

Si estos archivos viven en otras rutas del proyecto (ej. `WORK_LOG.md` en la
raíz), leé el `CLAUDE.md` del repo para detectar la ubicación correcta antes
de operar.

## Comando del usuario

| Comando (aproximado) | Acción del agente |
|---|---|
| "Cerremos la jornada" / "he finalizado el día" / "fin de jornada" | Ejecutá el flujo completo |
| "Cierre sin revisar learnings" | Salteás el paso 3 (útil si no hubo aprendizajes registrados hoy) |

## Flujo

### Paso 1 — Precondiciones

1. Verificá que existe `docs/work_log.md`. Si no existe, ofrecé crearlo con el
   formato base (ver sección "Formato de work_log"). Esperá confirmación.
2. Verificá si existe `docs/learnings.md`. Si no existe, marcá que la revisión
   conceptual del paso 3 no aplica y continuá.
3. Ejecutá `git status`. Si hay cambios sin commitear, avisá al usuario y
   preguntá si quiere commitearlos antes de cerrar la jornada. No cerrás con
   trabajo sin commitear — se pierde la trazabilidad.

### Paso 2 — Recolección de contexto del día

Ejecutá en orden y consolidá los resultados:

1. `git log --since='midnight' --pretty=format:'%h %s%n%b' --stat` — commits
   del día con sus estadísticas de cambios.
2. `git log --since='midnight' --name-only --pretty=format:''` — lista de
   archivos modificados hoy.
3. Leé las últimas 2–3 entradas de `docs/work_log.md` para conocer el formato
   exacto que usa este proyecto (fecha, secciones, viñetas, etc.).
4. Si el proyecto tiene `CLAUDE.md`, leélo para entender contexto general
   (dominio, convenciones, roles) que ayude a interpretar los cambios.

**Regla dura:** si no hay commits del día, avisá al usuario. Un día sin commits
puede ser: (a) legítimo — día de investigación, lectura o reuniones; (b) señal
de problema — trabajo local no commiteado. En cualquier caso, preguntá antes
de escribir en el work_log. Si el día fue legítimamente no-código, el usuario
te va a dar contexto para escribir la entrada.

### Paso 3 — Revisión de learnings.md (si existe)

Leé la última entrada de `docs/learnings.md` (la que corresponde a hoy o a la
sesión más reciente). Verificá tres cosas:

1. **Redacción**: frases confusas, errores ortográficos evidentes, párrafos
   que no fluyen. No corregís estilo personal ni preferencias del autor —
   solo problemas objetivos de claridad.
2. **Conceptos**: afirmaciones técnicas dudosas o incorrectas. Cruzá contra
   tu conocimiento general y contra el código real del repo cuando aplique.
   Ejemplos: si el usuario afirma "usé RRF con rank 0-indexed", verificá en
   el código. Si dice "async paraleliza CPU en Python", es incorrecto y hay
   que señalarlo.
3. **Coherencia**: contradicciones internas en la entrada, o con entradas
   previas cercanas.

**Reporte al usuario** con formato claro:

```
Revisión de learnings.md — entrada del {fecha}:

Redacción:
- {hallazgo 1 o "sin observaciones"}

Conceptos:
- {hallazgo 1 con cita textual y corrección propuesta, o "sin observaciones"}

Coherencia:
- {hallazgo 1 o "sin observaciones"}
```

**Regla dura:** no editás `learnings.md` automáticamente. El usuario decide
qué corregir y lo hace él mismo. Vos solo señalás.

Si el usuario pide que hagas la corrección después de leer tu reporte,
entonces sí modificás el archivo — pero solo bajo instrucción explícita.

### Paso 4 — Propuesta de entrada en work_log.md

Construí la entrada basándote **exclusivamente** en el contexto recolectado en
el paso 2 (commits reales y archivos modificados). No inventés trabajo que no
está en git.

La entrada debe tener dos secciones mínimas:

- **Trabajo desarrollado**: 3–7 viñetas concisas describiendo qué se hizo hoy.
  Cada viñeta refleja uno o varios commits agrupados por tema lógico. Referí
  archivos específicos cuando ayude a la trazabilidad (ej.
  `application/services/retrieval_service.py`).
- **Próximos pasos**: 2–4 viñetas con lo que sigue. Si el usuario mencionó
  explícitamente el plan del día siguiente, usalo. Si no, inferí del contexto
  (tareas pendientes visibles en el código, TODOs, roadmap del proyecto).

Otras secciones opcionales, agregar solo si aplican:

- **Bloqueos**: si detectás en los commits o mensajes que hay algo pendiente
  de decisión externa (input de stakeholder, respuesta de compañero, etc.).
- **Análisis de resultados**: si el día incluyó evaluaciones, tests, o
  benchmarks con métricas.

Respetá el formato exacto del work_log existente. Si el proyecto usa `###`
para subsecciones, usá `###`. Si separa entradas con `---`, respetá el
separador. Si los archivos van en backticks, mantené backticks.

### Paso 5 — Confirmación

Mostrá la entrada propuesta al usuario con el prefijo:

```
Propuesta de entrada para work_log.md (fecha {DD-MM-YYYY}):

---
{contenido propuesto}
---

¿La escribo tal cual, la ajusto, o querés cambiarla?
```

Esperá confirmación explícita. Aceptá pedidos de ajuste (agregar detalle,
recortar, reformular). No escribís en el archivo hasta tener OK claro.

### Paso 6 — Escritura y commit

1. Insertá la entrada nueva en `docs/work_log.md` al final del archivo,
   respetando el formato de separadores.
2. Preparás el mensaje de commit.
   - Si el repo tiene `.claude/skills/git-commits/SKILL.md`, seguí sus
     convenciones estrictamente.
   - Si no la tiene, usá Conventional Commits: `docs(work-log): update for
     YYYY-MM-DD`.
3. **No hacés `git commit` sin confirmación explícita del usuario.** Mostrás
   el comando propuesto y esperás.
4. No hacés `git push` — eso queda a criterio del usuario.

## Formato de work_log (si el archivo no existe)

Formato base a proponer al usuario si `docs/work_log.md` no existe todavía:

```markdown
# Work Log

Bitácora diaria de trabajo del proyecto {nombre}.

---

## YYYY-MM-DD

### Trabajo desarrollado
- {item 1}
- {item 2}

### Próximos pasos
- {item 1}
- {item 2}

---
```

Después de la primera entrada, respetás el formato que el usuario haya
adoptado.

## Anti-patrones

- **No inventar trabajo**. Si no está en los commits, no está en el work_log.
  Si el usuario hizo algo que no commiteó todavía (ej. lectura, diseño en
  papel), pediselo verbalmente y anotálo — pero identificándolo como aporte
  del usuario, no como inferencia tuya.
- **No corregir learnings.md automáticamente**. El aprendizaje pertenece al
  autor; tu rol es señalar, no editar.
- **No cerrar jornada con trabajo sin commitear**. Rompe la trazabilidad y
  el próximo cierre no va a poder reconstruir qué se hizo hoy vs mañana.
- **No inflar la entrada con detalles obvios**. `chore(deps): bump pydantic`
  no necesita tres viñetas de explicación. Una línea alcanza. La densidad
  de información importa más que la cantidad.
- **No incluir información sensible innecesaria**. En proyectos corporativos,
  evitá nombres completos de clientes, cédulas, saldos, o cualquier dato
  personal que aparezca en logs o comments. Referí a personas por rol o
  nombre de pila si es imprescindible.
- **No mezclar work_log con learnings**. Work_log es "qué hice"; learnings
  es "qué aprendí". Si el usuario escribió reflexiones en el work_log, no
  las muevas — solo señalá en el próximo cierre que ese contenido va mejor
  en learnings.

## Portabilidad entre proyectos

Esta skill funciona en cualquier repo con git y con al menos un
`docs/work_log.md`. Para instalarla en otro proyecto:

1. Copiá el archivo `.claude/skills/daily-closeout/SKILL.md` al nuevo repo.
2. Verificá si el nuevo proyecto tiene `docs/work_log.md` — si no, la skill
   ofrecerá crearlo en el primer uso.
3. Opcional: si el nuevo proyecto tiene convenciones de commit distintas,
   asegurate de tener también `.claude/skills/git-commits/SKILL.md` con esas
   convenciones. Sin esa skill, `daily-closeout` cae al default Conventional
   Commits.

La skill no depende del tema del proyecto (RAG, clasificación, agentes,
MLOps, análisis estadístico). Depende solo de git y del formato de work_log.
