# RAG y retrieval — banco de preguntas

5 preguntas. Fuente: `docs/interview_prep/bank.md`.

#### [RG-001] Nivel: básico
**Pregunta:** Dame un ejemplo concreto de una query donde BM25 supera a
la búsqueda vectorial, y otro donde vectorial supera a BM25. Explicá por qué.

**Respuesta esperada:** BM25 supera cuando la query contiene siglas,
nombres propios técnicos o términos raros con coincidencia exacta: por
ejemplo `"BERT vs GPT-3"` — un vectorizador puede diluir esas siglas en un
embedding genérico, pero BM25 encuentra ocurrencias exactas. Vectorial
supera cuando la query es semántica y el corpus usa vocabulario distinto:
por ejemplo `"papers on models that reason step by step"` — encuentra
papers de "chain-of-thought" aunque la query no contenga esas palabras.
Son complementarios: por eso hybrid search existe.

**Trampa común:** Pensar que uno es "mejor" en absoluto. Cada uno tiene
un tipo de query donde brilla.

**Ejemplo en el proyecto:** `infrastructure/retrieval/bm25.py` y
`infrastructure/retrieval/chroma.py` — ambos en producción, combinados
vía `application/services/retrieval_service.py`.

---

#### [RG-002] Nivel: intermedio
**Pregunta:** Explicá Reciprocal Rank Fusion (RRF) paso a paso. ¿Por qué
suma las contribuciones cuando un documento aparece en dos rankings, en
lugar de promediarlas o quedarse con la mayor?

**Respuesta esperada:** RRF recibe rankings (no scores) de N retrievers,
cada uno con sus top-K candidatos. Descarta los scores originales — trabaja
solo con posiciones (rank 1, 2, 3...). Por cada documento en cada ranking,
calcula contribución `1 / (rrf_k + rank)` con rank 1-indexed. Cuando un
doc aparece en múltiples rankings, **suma** las contribuciones. Ordena por
score total descendente y devuelve top-K. La suma premia el consenso:
docs que dos retrievers rankean alto suben más que docs rankeados alto
por uno solo. Promediar diluiría la señal (un rank alto se compensaría
con la ausencia); quedarse con la mayor ignoraría el consenso.

**Trampa común:** Decir que RRF "combina scores". No combina scores —
descarta los scores originales precisamente porque tienen escalas
incomparables (BM25 sin límite superior, coseno entre -1 y 1). Combina
**posiciones**, que sí son comparables.

**Ejemplo en el proyecto:** `application/services/retrieval_service.py`
implementa `hybrid_search` con RRF.

---

#### [RG-003] Nivel: intermedio
**Pregunta:** En tu hybrid_search, cada retriever devuelve `k*2`
candidatos aunque al final devuelvas solo `k`. ¿Por qué no pedir
exactamente `k`?

**Respuesta esperada:** Porque después de la fusión hay deduplicación y
reordenamiento. Si dos retrievers devuelven exactamente los mismos `k`
docs, después de deduplicar quedás con `k` únicos y la fusión no aportó
nada — mismo resultado que un solo retriever. Con `k*2`, tenés material
adicional: docs que aparecen en posiciones 4-6 de ambos retrievers son
consensuados aunque ninguno los rankee arriba, y RRF los promueve. En
producción el overlap entre vectorial y BM25 sobre el mismo corpus está
entre 20% y 60%, entonces `k*2` es un colchón razonable.

**Trampa común:** Pensar que el escenario "cero overlap" invalida `k*2`.
Cierto, ahí `k=candidatos` da lo mismo — pero no sabés el overlap antes
de correr, y el default tiene que servir para el caso peor.

**Ejemplo en el proyecto:** `hybrid_search` en `retrieval_service.py`,
parámetro `candidates_per_retriever` con default `k*2` cuando es `None`.

---

#### [RG-004] Nivel: avanzado
**Pregunta:** ¿Cómo evaluarías un sistema RAG en producción sin caer en
data leakage? Mencioná qué medís, cómo obtenés ground truth, y qué hacés
con las queries que fallan.

**Respuesta esperada:** Métricas objetivas: faithfulness (¿el LLM inventa
cosas no soportadas por los docs?), context precision (¿los docs
recuperados son relevantes?), answer relevancy (¿la respuesta contesta la
pregunta?). Todas con LLM-as-judge externo — un modelo distinto al que
genera, para evitar sesgo de auto-evaluación (ej. Gemini Flash mientras
generás con Claude). Ground truth: dos fuentes. (a) curación humana
externa — alguien que NO conoce el corpus escribe queries que representan
cómo un usuario preguntaría, y anota respuesta esperada. (b) feedback en
producción — thumbs up/down, reformulaciones (señal de que la primera
respuesta no sirvió). Queries que fallan: van a un regression dataset,
etiquetadas manualmente, corren en CI/CD, bloquean deploys que degraden
el score.

**Trampa común:** Construir queries de test conociendo el corpus indexado.
Eso es data leakage — el sistema "acierta" porque las queries están
alineadas con el contenido, no porque sea bueno. Mide qué tan bien recuerda
lo que ya sabías que estaba, no calidad de retrieval.

**Ejemplo en el proyecto:** El `learnings.md` del 01/06/2026 documenta
exactamente este problema al observar scores 1.000/1.000 en el eval — la
razón fue leakage por construir queries desde el corpus.

---

#### [RG-005] Nivel: avanzado
**Pregunta:** `build_dependencies()` reconstruye el índice BM25 cargando
**todos** los documentos de Chroma en memoria en cada arranque del bot,
porque BM25 no persiste. ¿Qué problema anticipás cuando el corpus
crezca, y cómo lo abordarías?

**Respuesta esperada:** Hoy es instantáneo porque el corpus es pequeño
(cientos de documentos), pero T21 (briefing matutino) va a ingerir papers
todos los días, así que ese arranque va a crecer linealmente con el tiempo
sin que nada lo frene. El síntoma no es un bug — es una decisión de diseño
(BM25 en memoria, sin persistencia) que funciona mientras una asunción
implícita (corpus chico) sea cierta, y deja de serlo silenciosamente.
Abordajes posibles: persistir el índice BM25 serializado junto a Chroma y
reconstruirlo solo si el corpus cambió; o mover la reconstrucción a un
proceso de fondo desacoplado del arranque del bot, para que un arranque
lento no bloquee la disponibilidad del canal.

**Trampa común:** Descartarlo como "no es un problema hoy" sin dejarlo
anotado. Las asunciones de escala que dejan de cumplirse silenciosamente
son más peligrosas que un error explícito — no hay señal hasta que duele.

**Ejemplo en el proyecto:** `scripts/_wiring.py:38-67` (`build_dependencies`);
pendiente anotado en `docs/work_log.md` del 20/08, ligado a issue
[#9](https://github.com/johnma96/researchos/issues/9) (T21).
