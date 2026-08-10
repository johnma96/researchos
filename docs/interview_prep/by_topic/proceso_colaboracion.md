# Proceso y colaboración — banco de preguntas

1 pregunta. Fuente: `docs/interview_prep/bank.md`.

#### [PC-001] Nivel: intermedio
**Pregunta:** Trabajaste cuatro meses en una sola rama de feature sin
mergearla a `main`. ¿Qué problemas concretos genera eso y cuál es el criterio
para decidir cuánto debe vivir una rama?

**Respuesta esperada:** Genera cuatro problemas. Primero, `main` no refleja
nada de lo que existe: si alguien clona el repo por defecto, obtiene un
esqueleto vacío. Segundo, el merge final es un evento grande y riesgoso — 56
commits de una sola vez son imposibles de revisar con atención. Tercero, no
hay ningún punto en el historial que marque "acá terminó una versión", así que
no se puede hacer rollback a un estado conocido ni etiquetar hitos. Cuarto, en
equipo la rama divergiría de `main` y acumularía conflictos, aunque en
solitario ese riesgo no se materializa. El criterio de duración es el tamaño
del entregable, no el tamaño de la versión: una rama debe cerrar algo
mostrable y revertible en una o dos semanas. Si un entregable no cabe en dos
semanas, se divide.

**Trampa común:** Justificar la rama larga con "estaba trabajando en una
versión completa". La versión es la unidad del roadmap, no la unidad de la
rama. V2 son siete semanas de roadmap y cuatro ramas de dos semanas cada una.
Otra trampa es proponer squash merge para "limpiar" el historial: en un
proyecto de aprendizaje los commits individuales son el registro del proceso.

**Ejemplo en el proyecto:** `feature/v1-infrastructure-setup` acumuló 56
commits entre abril y agosto de 2026 sin mergear, con `main` congelada en
`e3a6ac2` (el esqueleto inicial). El nombre además quedó desactualizado: la
rama se llamaba `infrastructure-setup` pero terminó conteniendo el pipeline
RAG completo, el sistema de estudio y el bot de Telegram. V2 se estructuró en
cuatro ramas de dos semanas para evitar repetirlo.
