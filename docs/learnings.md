# ResearchOS — Diario de aprendizaje (learnings.md)

> Registra lo aprendido cada semana: conceptos, errores, decisiones, reflexiones.
> Herramienta de aprendizaje + activo de portfolio para entrevistas.

---

## Semana 1 — Setup + RAG básico

### **Fecha:** 30/03/2026
#### REACT
- Chain of Taought como estrategia para prompting es una caja negra estática ya que el MODELO USA SUS REPRESENTACIONES INTERNAS PARA GENERAR EL PENSAMIENTO Y  NO LO ALIMENTA DEL MUNDO EXTERIOR. ReAct propone "Razonar para actuar" al tiempo que se "Actúa para razonar". Los modelos de tipo "acción" carecen de la capacidad de llevar objetivos de alto nivel o complejos por lo que es difícil un reflexión profunda.

- Idea central REACT: Aumentar el espacio de acción A del agente de manera que A = A U L, donde L es el espacio del lenguaje. Una acción en L será referida como "pensamiento" o "traza de razonamiento". Esta acción en el espacio L no afecta el exterior y por tanto no obtiene observación como feedback. Lo que hace es obtener información para razonar sobre el contexto c_t y actualizarlo.

- Modelo: PalM-540B con pesos congelados es solicitado with few-shot in-context examples

- Se abordaron tipos de pensamiento como: descomponer metas, inyectar conocimiento de sentido común, extraer partes importantes, rastrear el progreso y manejar excepciones. Además, en función de la pregunta, se tienen razonamiento para tareas de razonmiento en cada paso (pensar-accion-observacion) o pensamientos dispersos para tareas de toma de decisiones (los pensamientos solo están en posiicones relevantes de la trayectoria). Durante las pruebas, un humano podía ir modificanco y controlando el pensameinto del modelo

- Los resultados demostraron una mejor trabajo con ReAct VS Act, especialmente sintetizando la respuesta final

- ReAct VS CoT: Mejor en HotpotQA, y levemente inferior en Fever
    - Alucinaciones es un problema serio en CoT
    - Si bien la intercalación de pasos de razonamiento, acción y observación mejora la solidez y la fiabilidad de ReAct, dicha restricción estructural también reduce su flexibilidad a la hora de formular pasos de razonamiento, lo que da lugar a una tasa de errores de razonamiento mayor que la de CoT. Observamos que existe un patrón de error frecuente específico de ReAct, en el que el modelo genera repetidamente los pensamientos y acciones anteriores, y lo clasificamos como parte de los «errores de razonamiento», ya que el modelo no logra razonar sobre cuál es la siguiente acción adecuada a tomar y salir del bucle.
    - La recuperación de información es crítica para ReAct: Cuanod no la obitiene se descarrilla el razonamiento y le cuesta recuperarse
    - En el fine tunning, con la estrategia ReAct se obtuvo significativamente mejor desempeño que haciendo ajuste fino con las otras estrategias

Insights:
1. Costo de la Autonomía: La flexibilidad de ReAct tiene un "impuesto" de tokens y tiempo. Úsalo solo cuando el camino a la respuesta no sea previsible.

2. Observación como Correctivo: La gran ventaja de ReAct no es que "piense mejor", sino que "escucha" lo que el mundo (las herramientas) le devuelve y corrige su rumbo.

3. Determinismo vs. Agencia: Si la tarea es clasificar (PQRS), el determinismo del RAG gana. Si la tarea es diagnosticar/decidir (Pensiones), la agencia de ReAct es superior.

### Lo que construí
Cliente de Claude API (`AnthropicLLM`) que implementa el Protocol `LLMProvider` con dos métodos: `generate()` para respuestas completas y `stream()` para respuestas token a token.

### Conceptos aprendidos

**async/await**
`async def` declara una función que puede pausarse. `await` es el punto de pausa: el event loop atiende otras tareas mientras espera la respuesta externa. Sin async, el programa se bloquea esperando.

**AsyncMock vs MagicMock**
- `MagicMock` — simula objetos y atributos síncronos
- `AsyncMock` — simula funciones async (las que necesitan `await`)
- Para `async with` hay que mockear `__aenter__` y `__aexit__`
- Para `async for` se necesita un generador async (`async def` + `yield`), no un `iter()` normal

**Tests unitarios vs integración**
- Unitario: sin llamadas reales, cliente reemplazado por mock, rápido, sin costo
- Integración: llamada real a la API, marcado con `@pytest.mark.integration`, consume tokens
- `make test` corre solo `@pytest.mark.unit`. `make test-all` corre todo.

**pre-commit**
Guardián que corre antes de cada commit. Si encuentra errores autocorregibles, los corrige y bloquea el commit. Solo hay que volver a hacer el commit con los archivos ya corregidos.

**Claude Pro vs Anthropic API**
Son productos separados. Claude Pro cubre claude.ai (interfaz web). La API requiere créditos independientes en console.anthropic.com.

### Decisiones técnicas
- `_format_messages()` separa el system prompt de los mensajes de conversación antes de enviar a la API
- Re-exports explícitos (`Document as Document`) requeridos por ruff para imports públicos en `__init__.py`
- Notebooks excluidos del linting de ruff en `pyproject.toml`

### ¿Qué no entendí bien?
- Cuándo usar async-await: debo reforzar este concepto porque veo que está muy rlacionado con el uso de APIs
- Protocol: Entiendo que es más como una maqueta que le dice a python que el método debe cumplir X cosas: Eso hace que cuando alguien quiera implementar un nuevo proveedor, mínimamente debe ajustarse al contrato?
- test: el uso de mocks es complejo, seguir profundizando y tal vez buscar hacer ejercicios?

**Fecha:** 09/04/2026

### ¿Qué aprendí?
-  En la creación de los repos hermanos debo customizar el CLAUDE.md para que sepa hacia dónde apunta el proyecto y sus pormenores
- También aprendía acerca de .pre-commit y solucioné algunos inconvenientes con su uso, entendí que usa ruff y linter para mantener el código limpio y ordenado
- Establecí una rutina para hacer commits que se basa en hacer cerca de 4 a 6 commits diarios de manera que el avance sea continuo pero contenido, y además se estableció Conventional Commits con una estructura <type>(<scoper>): <description> y se incluyó en los CLAUDE.md para que el asistente de código ayude a hacer commits y avice cuando note que ya es hora.
- Aprendía sobre uv y su uso para la gestión de dependecias: actualmente es un estandar en python porque permite mantener ambienestes aislados, disminuye el consumo de recursos ya que trabaja como apuntador a librerías que ya se han descargado en lugar de descargar cada una en el ambiente particular; y como bonues es mucho más rápido que la estrategia pip + venv.

### Que no entendí bien
- Aún tengo dudas sobre el uso de arquitectura limpia y sus beneficios
- También debo de ahondar en cuál es la importnacia de establecer modelos y protocolos que además están aislados de la infraestructura

### Decisiones de diseño
- Se modificó el CLAUDE.md
- Se replanteó el desarrollo de múltiples proyectos al tiempo
- Hay que actualizar algunas cosas en el template clean-agents-template (NO URGENTE)

**Fecha:** _[completar]_

### ¿Qué aprendí?
-

### ¿Qué no entendí bien?
-

### Decisiones de diseño
-

### Errores interesantes
-

---
<!-- Copiar plantilla para cada semana -->
