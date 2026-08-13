# Tokens de estilo — arquitecturas draw.io de la organización

Destilado de los diagramas de referencia de la organización. `scripts/drawio_kit.py` ya trae estos
tokens en los dicts `STYLE` y `EDGE`; este documento es para consulta o para escribir el XML a mano.

## Paleta

| Rol | Color |
|---|---|
| Texto primario | `#4B5259` |
| Texto atenuado | `#9E9E9E` / `#999999` / `#777777` |
| Azul de marca (bordes, edges) | `#4284F3` |
| Azul secundario (acentos/iconos) | `#5184F3` |
| Azul banner (relleno sólido, texto blanco) | `#4DA1F5` |
| Azul icono (actor ios7) | `#0080F0` |
| Verde datos / éxito | `#66CC00` (edges) · `#82b366` (bordes) |
| Borde neutro | `#dddddd` (con `shadow=1`) |

Pasteles estándar de draw.io para categorizar cajas: azul `#dae8fc` (LLM/servicio), verde `#d5e8d4`
(determinista), rojo `#f8cecc` (crítico/PII), naranja `#ffe6cc` (gate), amarillo `#fff2cc` (salida).

## Tipografía y tamaños

Fuente por defecto de draw.io. `fontSize` 12 en nodos, 15 en banners, 10–11 en detalles/almacenes.

Tamaños medidos en los diagramas de referencia de la organización, que son el estándar a igualar:

| Elemento | Tamaño | Etiqueta |
|---|---|---|
| Caja de componente | **~180×56** (mediana real 176–200 × 52–56) | **30–45 caracteres**, 2–3 líneas cortas |
| Almacén (cilindro) | ≈170×44 | Nombre + una línea de detalle |
| Actor | 48×60 | Dos palabras |
| Zona / banda | ancho completo | Título corto alineado a la izquierda |

**Cajas pequeñas y muchas, no pocas y grandes.** Una caja de 300×88 con cuatro líneas de prosa es
media nota al pie disfrazada de componente: ocupa el espacio de tres cajas reales y obliga a bajar
el número de nodos, que es justo lo que vuelve el diagrama incompleto para un lector técnico. Si el
texto no cabe en 45 caracteres, el detalle va a la etiqueta de la flecha, a la zona que agrupa o a
una nota al pie de la página. `check_layout` avisa cuando la mediana de la página se pasa.

## El rojo se concentra, no se rocía

El rojo (`STYLE["warn"]`, `#f8cecc`) marca deuda técnica o violación de capas. **Va agrupado en una
zona rotulada** —«Deuda técnica», «Piezas sin implementar»— donde el lector lo interpreta como una
sección del diagrama. Repartido sobre los pasos de un flujo produce el efecto contrario al buscado:
si cuatro de los diez pasos de un pipeline salen en rojo, el sistema entero se lee como averiado
cuando lo que está mal puede ser solo dónde viven unos imports.

En un flujo, colorea cada paso por **lo que es** (su capa) y saca la deuda a una nota al pie o a una
página aparte; marca en rojo únicamente el punto exacto de la violación. Y cuida que el texto de la
leyenda cubra **todos** los usos que le das al color: si el rojo también señala «duplica el wiring»,
la leyenda no puede decir solo «viola ADR-001». `check_layout` avisa si más del 25 % de las cajas de
una página están en rojo fuera de una zona de deuda.

## Esquinas redondeadas fijas (dos niveles)

Las cajas redondeadas llevan un **radio fijo en píxeles** (`absoluteArcSize`), no la curva grande y
**proporcional al tamaño** que aplica `rounded=1` a secas — esa curva, en cajas anchas o de poca
altura, tapa el texto alineado a la izquierda o lo saca por las esquinas. Se usan **dos niveles**:

- **Cajas de componente** (tarjeta, LLM, determinista, crítico, salida): `arcSize=6;absoluteArcSize=1;`
  — radio muy sutil.
- **Contenedores / zonas** (los recuadros azules punteados grandes): `arcSize=6;absoluteArcSize=2;`
  — un poco más marcado para que la esquina se note en las cajas grandes.

`drawio_kit` ya lo inyecta en `STYLE` (constantes `ARC` y `ARC_ZONE`); si escribes el XML a mano, añádelo.

## Strings de estilo (copiar en draw.io con Ctrl+E)

```
# Banner / cabecera
rounded=0;whiteSpace=wrap;html=1;fillColor=#4DA1F5;strokeColor=none;shadow=1;fontColor=#ffffff;fontSize=15;fontStyle=1;align=center;

# Tarjeta neutra
rounded=1;arcSize=6;absoluteArcSize=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#dddddd;shadow=1;strokeWidth=1;fontColor=#4B5259;fontSize=12;

# Servicio / agente LLM (azul)
rounded=1;arcSize=6;absoluteArcSize=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;shadow=1;fontColor=#4B5259;fontSize=12;

# Núcleo determinista (verde)
rounded=1;arcSize=6;absoluteArcSize=1;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;shadow=1;fontColor=#4B5259;fontSize=12;

# Paso crítico / advertencia (rojo)
rounded=1;arcSize=6;absoluteArcSize=1;whiteSpace=wrap;html=1;fillColor=#f8cecc;strokeColor=#b85450;shadow=1;fontColor=#4B5259;fontSize=12;fontStyle=1;

# Salida / revisión humana (amarillo)
rounded=1;arcSize=6;absoluteArcSize=1;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;shadow=1;fontColor=#4B5259;fontSize=12;

# Gate condicional (rombo naranja)
rhombus;whiteSpace=wrap;html=1;fillColor=#ffe6cc;strokeColor=#d79b00;shadow=1;fontColor=#4B5259;fontSize=11;

# Contenedor / zona (borde azul punteado, fondo transparente) — esquina algo más marcada (arcSize 2)
rounded=1;arcSize=6;absoluteArcSize=2;whiteSpace=wrap;html=1;fillColor=none;strokeColor=#4284F3;dashed=1;verticalAlign=top;align=left;fontColor=#4284F3;fontSize=13;fontStyle=1;spacingLeft=12;spacingTop=6;

# Actor / usuario · Almacén-BD (cilindro, etiqueta DEBAJO, estándar ~120x50) · Documento
shape=mxgraph.ios7.icons.user;html=1;strokeColor=#0080F0;strokeWidth=2;verticalLabelPosition=bottom;verticalAlign=top;align=center;fontColor=#4B5259;
shape=cylinder3;whiteSpace=wrap;html=1;fillColor=#f5f5f5;strokeColor=#999999;verticalLabelPosition=bottom;verticalAlign=top;align=center;fontColor=#4B5259;fontSize=10;
shape=document;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#999999;boundedLbl=1;fontColor=#4B5259;fontSize=11;
```

## Conexiones (la firma de la casa)

Edges **ortogonales y animados** con color **theme-aware** (`light-dark(claro,oscuro)`).
**Obligatorio: TODOS los conectores llevan `flowAnimation=1`** (animación de flujo) — es la firma de
la casa; también las variantes punteadas. El kit ya lo garantiza en `EDGE`.

```
# Flujo principal (animado)
edgeStyle=orthogonalEdgeStyle;flowAnimation=1;rounded=0;html=1;strokeColor=light-dark(#4284F3,#6671E3);strokeWidth=2;

# Datos / RAG (verde) · Excepción/humano (rojo punteado) · Auxiliar (gris punteado) — TODOS animados
edgeStyle=orthogonalEdgeStyle;flowAnimation=1;rounded=0;html=1;strokeColor=#66CC00;strokeWidth=2;
edgeStyle=orthogonalEdgeStyle;flowAnimation=1;rounded=0;html=1;dashed=1;strokeColor=#b85450;strokeWidth=2;
edgeStyle=orthogonalEdgeStyle;flowAnimation=1;rounded=0;html=1;dashed=1;strokeColor=#9E9E9E;strokeWidth=1;
```

## Leyenda descriptiva (obligatoria)

Todo diagrama entregado incluye una leyenda que traduce el color a significado. Convenio de la casa
para las **flechas** (mismo `EDGE` del kit):

| Color | `EDGE` | Significado |
|---|---|---|
| Verde `#66CC00` | `data` | Flujo de datos (lo que se transforma y avanza entre pasos) |
| Azul `light-dark(#4284F3,#6671E3)` | `flow` | Orquestación / control (quién invoca o ejecuta a quién) |
| Gris punteada `#9E9E9E` | `aux` | Consumo de un servicio o recurso compartido (lectura/escritura) |
| Rojo punteado `#b85450` | `warn` | Excepción / intervención humana |

Y para las **cajas**, describe solo los arquetipos que uses (verde = determinista, azul = servicio/LLM,
rojo = orquestador/crítico, blanco = almacén de apoyo, amarillo = salida). Añade las convenciones
extra que apliquen (iconos sueltos = fuentes externas; flechas animadas = sentido del flujo).

Dibújala en una franja al pie (dentro del `pageHeight`) con **edges de muestra reales** — mismo `style`
que en el diagrama — y **chips** de color usando el `fillColor`/`strokeColor` de cada arquetipo:

```python
# Línea de muestra (sin nodos): usa Page.legend_edge(x1, x2, y, style) — NO Page.edge()
p.legend_edge(960, 1005, 756, EDGE["data"])   # swatch verde = flujo de datos
# Chip de color de caja: un node() normal con el estilo del arquetipo
p.node("Paso determinista", 960, 780, 240, 38, STYLE["det"])
```

**Por qué `legend_edge` y no `edge`:** una muestra de flecha en la leyenda no conecta dos nodos reales,
así que es un edge "flotante" — mxGraph exige que declare sus extremos con
`<mxPoint as="sourcePoint">`/`<mxPoint as="targetPoint">` dentro de `mxGeometry`. Sin el atributo `as=`
draw.io no sabe dónde dibujar el segmento y la muestra queda invisible (bug real detectado: el XML
parseaba y el linter de traslapes no lo atrapaba, pero la línea no se veía en draw.io). `legend_edge`
ya emite esos atributos — no construyas el `<mxPoint>` a mano.

## Claridad y anti-traslape (lo más importante para que se entienda)

Reglas de diseño:

- **Separación mínima**: deja ≥ 40 px entre cajas de nodos distintos. Recuerda que la etiqueta de un
  icono se dibuja **debajo** de él (con `verticalLabelPosition=bottom`) y ocupa ~15 px por línea: no
  pongas otro nodo pegado abajo o la etiqueta lo pisará.
- **Fijar los anclajes** con `exit=(fx,fy)` y `entry=(fx,fy)` (fracciones 0–1). Es lo que separa un
  diagrama legible de un enredo de flechas.
- **Fan-out**: salir del origen a distinta Y por rama (`exit=(1,0.3)`, `(1,0.5)`, `(1,0.7)`); entrar
  por el mismo lado del destino → peine paralelo. **Gather**: entrar al destino a distinta Y
  (`entry=(0,0.2)`, `(0,0.5)`, `(0,0.8)`).
- **Almacenes de apoyo** pegados **junto** al nodo que los consume (edge corto), no al otro extremo.
- **Flechas que cruzarían un nodo** → usa `points=[(x,y),...]` en `edge()` para sacar la ruta por
  encima/alrededor (un carril libre), o reubica los nodos. No dejes una flecha atravesando un icono.
- **Etiquetas de flecha: el hueco manda.** Es el traslape más frecuente y el más invisible al
  escribir el script. La etiqueta se dibuja en el punto medio del recorrido, o sea **dentro del hueco
  entre las dos cajas que conecta**; si el hueco es más angosto que la etiqueta, esta se monta sobre
  ambas. Regla operativa: **hueco ≥ 8 px × nº de caracteres de la etiqueta, + 20 px de aire.**
  `search_papers(query)` son 20 caracteres → necesita ~180 px de separación, no 40. Si no tienes ese
  espacio, tienes tres salidas y ninguna es dejarlo así: acortar la etiqueta, moverla a un tramo
  vertical largo con un waypoint, o quitarla y llevar ese dato dentro de la caja destino.
- **Etiquetas de flecha sobre otros nodos**: ponlas donde el tramo esté libre; si caen sobre un nodo,
  mueve el nodo o añade un waypoint para desplazar el punto medio.
- **Contenedor/zona**: dibújalo primero (queda detrás), `fillColor=none`; el título va en una esquina
  (`align=left`), no centrado sobre el paso de las flechas.

### Patrones de composición (resuelven el 90 % de los enredos)

Antes de pelear con waypoints, prueba a cambiar la disposición. Estos patrones vienen de rehacer
diagramas que habían quedado ilegibles:

- **Serpentina para secuencias largas.** Si un flujo no cabe en una fila, no vuelvas al margen
  izquierdo con una flecha de retorno gigante: alterna el sentido por fila (fila 1 →, fila 2 ←,
  fila 3 →) y **baja de fila por la misma columna**, con un tramo vertical corto. Así ninguna
  flecha retrocede ni cruza otra. Es lo que permite meter 12 pasos en una página sin un solo cruce.
- **Pasos numerados** ① ② ③ en la etiqueta de cada caja. El lector sigue números, no flechas; y de
  paso te libera de dibujar los retornos, que son la mitad del enredo en un diagrama de secuencia.
- **Corredores reservados.** Deja carriles (verticales u horizontales) sin ningún nodo, y rutea por
  ahí las flechas largas con `points=`. Un par de corredores en los márgenes convierte un ruteo
  imposible en uno trivial. Reserva el carril **antes** de colocar los nodos, no después.
- **Codifica la capa en el COLOR de la caja, no en bandas**, cuando la página es de flujo. Dibujar
  bandas por capa *y* un flujo encima obliga a que cada paso cruce de banda: es la receta exacta
  para que las etiquetas caigan sobre los títulos. Las bandas son para la vista estática; en la
  dinámica, el color ya dice la capa y la leyenda lo traduce.
- **Sustituye un haz N:M por una tabla.** Una relación aburrida y densa (qué implementa qué
  contrato, qué servicio consume qué cola) son diez flechas cruzadas o una caja de texto con dos
  columnas. Gana la caja: se lee mejor y no gasta presupuesto de flechas.
- **Cuidado con las formas de etiqueta inferior** (cilindro `store`, actor `user`): su huella real
  es la caja **más ~1.7× su ancho** de texto debajo. No las pongas de vecinas apretadas, no las uses
  como chip de leyenda tal cual (el kit ya lo resuelve en `Page.legend`) y no rutees una flecha justo
  por debajo.

### Verificar con el linter (obligatorio antes de entregar)

`drawio_kit.write()` corre `check_layout` y avisa. Para el detalle:

```bash
python scripts/check_layout.py docs/architecture.drawio
```

Reporta ocho tipos de problema: **nodos-superpuestos**, **etiqueta-sobre-nodo**,
**flecha-cruza-nodo**, **etiqueta-flecha-sobre-nodo**, **etiqueta-flecha-sobre-titulo-zona**,
**etiquetas-flecha-encimadas**, **texto-desborda-caja** y **nodo-fuera-de-pagina**. Itera
reubicando nodos / añadiendo waypoints hasta que no queden problemas **duros** (nodos-superpuestos,
flecha-cruza-nodo, nodo-fuera-de-pagina, que hacen salir con código ≠ 0).

Dos notas sobre por qué el linter mira lo que mira:

- Las **zonas se excluyen** de los chequeos de cruce porque contienen nodos por diseño, pero su
  **título** sí se comprueba: vive en una banda de ~26 px arriba y ahí es donde aterrizaban las
  etiquetas de flecha (bug real: el título quedó como `infrastructure/ — SDK[Atom XML]erno`). Para
  que esa detección funcione, dibuja las zonas con `Page.zone()`, que marca la celda como contenedor.
- La posición de una etiqueta de flecha se estima **sobre la polilínea ruteada**, no en el punto
  medio recto origen→destino: con waypoints, ambos puntos no tienen nada que ver.

Sigue siendo heurístico (el ruteo real de draw.io difiere) y **no sustituye la revisión visual**:
el linter no ve fuentes, ni iconos que no cargan, ni palabras pegadas. Confirma siempre con un
export real (ver SKILL.md, sección de verificación).

## Etiquetas: pasar texto crudo (evitar doble escape)

`drawio_kit` ya escapa el XML por ti. En `label` pasa **texto crudo**, no entidades:

- salto de línea → `"\n"` (no `"&#xa;"`);
- `<`, `>`, `&` literales → escríbelos tal cual (`"</> MicroComponent"`, `"Search & Chat"`), no
  `"&lt;"`/`"&amp;"`.

Si pre-codificas entidades, el kit las vuelve a escapar (`&amp;lt;`, `&amp;#xa;`) y draw.io muestra
el texto literal en vez de interpretarlo.

## Higiene de git

- El pre-commit típico **bloquea archivos > 500 KB**. Con iconos SVG embebidos un diagrama pesa
  decenas de KB; no embeber PNG pesados ni cientos de imágenes.
- Tratar las arquitecturas como documentación interna; sin PII ni datos sensibles en etiquetas/notas.
- Revisar y editar el `.drawio` en VS Code con la extensión *Draw.io Integration* (`hediet.vscode-drawio`).
