# Protocols — banco de preguntas

3 preguntas. Fuente: `docs/interview_prep/bank.md`.

#### [PR-001] Nivel: básico
**Pregunta:** ¿Qué es un `Protocol` de Python y en qué se diferencia de
una clase abstracta (`ABC`)?

**Respuesta esperada:** Un Protocol define un contrato **estructural** —
cualquier clase con los métodos y firmas correctas lo satisface, sin
necesidad de heredar. La verificación es típicamente estática (mypy). Una
ABC define un contrato **nominal** — requiere herencia explícita
(`class Foo(BaseClass):`) y hace enforcement en runtime (`TypeError` si
un método abstracto no se implementa al instanciar). Protocol permite
que clases de librerías externas cumplan el contrato sin modificarlas;
ABC obliga a controlar el árbol de herencia.

**Trampa común:** Tratarlos como sinónimos "más modernos" uno del otro.
Son diferentes en runtime behavior y en filosofía de diseño.

**Ejemplo en el proyecto:** `domain/interfaces.py` define
`LLMProvider(Protocol)` con métodos `generate` y `stream`. Cualquier clase
con esos métodos lo satisface, incluyendo mocks de test que no heredan
de nada.

---

#### [PR-002] Nivel: intermedio
**Pregunta:** ¿Por qué en tu proyecto usás Protocols para las abstracciones
de `application/` en lugar de clases abstractas?

**Respuesta esperada:** Los Protocols evitan acoplar `application/` a
jerarquías de herencia. Si Anthropic saca un SDK nuevo con estructura
distinta, la nueva implementación de `LLMProvider` vive en infrastructure
sin necesitar herencia común. También facilita testing: los mocks pueden
ser clases simples sin importar nada de infrastructure. Además, structural
subtyping permite que clases de terceros cumplan el contrato sin tocar
su código.

**Trampa común:** Pensar que "ABC hace lo mismo con más rigor". El
"rigor" adicional de ABC (enforcement al instanciar) es innecesario si
usás mypy en CI — y a cambio pagás con acoplamiento por herencia.

**Ejemplo en el proyecto:** `application/services/rag_service.py` recibe
`llm: LLMProvider` y `store: VectorStore` — no sabe si son AnthropicLLM,
GeminiLLM, ChromaVectorStore o mocks; solo sabe qué métodos puede llamar.

---

#### [PR-003] Nivel: avanzado
**Pregunta:** ¿Cómo se testea código de `application/` que depende de un
Protocol, sin usar implementaciones reales de infrastructure?

**Respuesta esperada:** Se crea una clase mock local (en el test o en
`conftest.py`) que implementa los métodos del Protocol con comportamiento
controlado. Como Protocol es structural, no hace falta heredar de nada —
solo tener los métodos con las firmas correctas. Ejemplo: `MockVectorStore`
en `tests/conftest.py` con `search` y `upsert` que operan sobre una lista
en memoria. Los tests de `application/` inyectan estos mocks y verifican
comportamiento sin tocar Chroma real. Alternativa débil: `unittest.mock.
MagicMock` — funciona pero pierde chequeo estático (podés llamar métodos
que el Protocol no declara y no te avisa).

**Trampa común:** Usar `MagicMock` universalmente por comodidad. Perdés la
señal de mypy sobre si tu test está usando el Protocol correctamente.

**Ejemplo en el proyecto:** `tests/conftest.py` tiene `MockVectorStore` y
mocks de LLMProvider usados en `tests/unit/application/`.
