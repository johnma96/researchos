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
Tamaños de caja habituales: tarjeta **160×60** o **170×60**, almacén **≈190×44**, actor **48×60**.

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
que en el diagrama, con `sourcePoint`/`targetPoint` en la geometría en lugar de `source`/`target` — y
**chips** de color usando el `fillColor`/`strokeColor` de cada arquetipo:

```
# Línea de muestra (sin nodos): reutiliza el EDGE real, solo cambia los puntos
<mxCell id="lg-e-green" style="edgeStyle=none;html=1;flowAnimation=1;strokeColor=#66CC00;strokeWidth=3;startArrow=none;endArrow=classic;" edge="1" parent="1">
  <mxGeometry relative="1" as="geometry">
    <mxPoint x="60" y="1080" as="sourcePoint"/><mxPoint x="104" y="1080" as="targetPoint"/>
  </mxGeometry>
</mxCell>
# Chip de color de caja (usa el fillColor/strokeColor del arquetipo)
rounded=1;arcSize=6;absoluteArcSize=1;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;
```

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
- **Etiquetas de flecha** (`202`, `Post`): ponlas donde el tramo esté libre; si caen sobre un nodo,
  mueve el nodo o añade un waypoint para desplazar el punto medio.
- **Contenedor/zona**: dibújalo primero (queda detrás), `fillColor=none`; el título va en una esquina
  (`align=left`), no centrado sobre el paso de las flechas.

### Verificar con el linter (obligatorio antes de entregar)

`drawio_kit.write()` corre `check_layout` y avisa. Para el detalle:

```bash
python scripts/check_layout.py <archivo>.drawio
```

Reporta **nodos-superpuestos**, **etiqueta-sobre-nodo**, **flecha-cruza-nodo** y
**etiqueta-flecha-sobre-nodo**. Itera reubicando nodos / añadiendo waypoints hasta que no queden
traslapes **duros** (nodos-superpuestos, flecha-cruza-nodo). Es heurístico (el ruteo real de draw.io
difiere), así que confirma también visualmente en draw.io.

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
