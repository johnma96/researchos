# ResearchOS — Diario de aprendizaje (learnings.md)

> Registra lo aprendido cada semana: conceptos, errores, decisiones, reflexiones.
> Herramienta de aprendizaje + activo de portfolio para entrevistas.

---

## Semana 1 — Setup + RAG básico

### Día 1 **Fecha:** 30/03/2026
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
