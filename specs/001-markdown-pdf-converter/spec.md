# Feature Specification: Markdown to PDF Converter

**Feature Branch**: `001-markdown-pdf-converter`

**Created**: 2026-07-29

**Status**: Draft

**Input**: User description: "Construir un conversor de Markdown a PDF de alta calidad que maneje correctamente tablas, bloques de codigo con syntax highlighting, diagramas Mermaid como SVG, y saltos de pagina inteligentes. Disponible como CLI y como interfaz web."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Conversion basica de Markdown a PDF (Priority: P1)

Un desarrollador tiene un archivo README.md con texto, encabezados, listas, links e
imagenes. Ejecuta el comando CLI para convertirlo a PDF y obtiene un documento
profesional con tipografia limpia, tabla de contenido y margenes consistentes.

**Why this priority**: Es la funcionalidad core — sin esto no existe el producto. Todo
usuario necesita convertir al menos un archivo simple a PDF.

**Independent Test**: Se puede probar creando un archivo .md con contenido basico y
verificando que el PDF resultante contiene todo el contenido sin perdida ni corrupcion.

**Acceptance Scenarios**:

1. **Given** un archivo Markdown valido con encabezados, parrafos y listas, **When** el usuario ejecuta `mdpdf convert archivo.md`, **Then** se genera un archivo PDF en el mismo directorio con el contenido completo y formateado.
2. **Given** un archivo Markdown valido, **When** el usuario especifica `--output ./pdfs/`, **Then** el PDF se genera en el directorio especificado.
3. **Given** un archivo Markdown con encabezados H1-H3, **When** la conversion se ejecuta con TOC habilitado, **Then** el PDF incluye una tabla de contenido con hipervinculos internos funcionales.

---

### User Story 2 - Tablas renderizadas sin overflow (Priority: P1)

Un ingeniero tiene documentacion tecnica con tablas de especificaciones (5-10 columnas).
Al convertir a PDF, las tablas se ajustan al ancho de pagina sin cortarse, con texto
legible y columnas proporcionadas al contenido.

**Why this priority**: Las tablas desbordadas son el problema #1 de los conversores
existentes. Es el diferenciador principal del producto.

**Independent Test**: Convertir un archivo con una tabla de 8 columnas y verificar que
todas las columnas son visibles dentro de los margenes de pagina.

**Acceptance Scenarios**:

1. **Given** un archivo con una tabla de 5 columnas con contenido corto, **When** se convierte a PDF, **Then** la tabla ocupa el ancho disponible con columnas proporcionadas y texto completamente legible.
2. **Given** un archivo con una tabla de 10 columnas con contenido mixto, **When** se convierte a PDF, **Then** la tabla se ajusta (reduccion de fuente, word-wrap) sin que ninguna columna se salga del margen.
3. **Given** un archivo con una tabla cuyo contenido es extremadamente ancho, **When** se convierte a PDF, **Then** la tabla aplica word-wrap y/o reduccion de fuente (minimo 7pt) para mantenerse dentro de margenes.

---

### User Story 3 - Bloques de codigo con syntax highlighting (Priority: P1)

Un desarrollador documenta snippets de codigo en multiples lenguajes (Python, JavaScript,
SQL, YAML). Al convertir a PDF, los bloques de codigo tienen colores de sintaxis,
fuente monospace y nunca se cortan entre paginas.

**Why this priority**: Documentacion tecnica sin code blocks legibles no tiene utilidad
para el publico objetivo (desarrolladores).

**Independent Test**: Convertir un archivo con bloques de codigo en 3 lenguajes distintos
y verificar que cada uno tiene highlighting correcto y fondo diferenciado.

**Acceptance Scenarios**:

1. **Given** un bloque de codigo Python con fenced syntax (```python), **When** se convierte a PDF, **Then** el bloque tiene syntax highlighting con colores, fuente monospace y fondo diferenciado.
2. **Given** un bloque de codigo con lineas de 120+ caracteres, **When** se convierte a PDF, **Then** las lineas largas hacen word-wrap sin perder indentacion visual ni cortarse.
3. **Given** un bloque de codigo al final de una pagina que no cabe completo, **When** se convierte a PDF, **Then** el bloque se mueve a la pagina siguiente en lugar de cortarse a mitad.

---

### User Story 4 - Diagramas Mermaid renderizados como graficos (Priority: P2)

Un arquitecto de software incluye diagramas Mermaid en su documentacion (flowcharts,
sequence diagrams, class diagrams). Al convertir a PDF, los diagramas aparecen como
graficos vectoriales legibles, no como texto plano.

**Why this priority**: Mermaid es el estandar de facto para diagramas en Markdown
tecnico. Sin soporte, el conversor pierde utilidad para documentacion de arquitectura.

**Independent Test**: Convertir un archivo con un flowchart Mermaid y verificar que
aparece como imagen/SVG renderizada en el PDF.

**Acceptance Scenarios**:

1. **Given** un archivo con un bloque ```mermaid con un flowchart valido, **When** se convierte a PDF, **Then** el diagrama aparece renderizado como grafico vectorial (no como texto).
2. **Given** un bloque Mermaid con sintaxis invalida, **When** se convierte a PDF, **Then** el sistema muestra un warning y renderiza el bloque como codigo con un mensaje de error visible.
3. **Given** un diagrama Mermaid que excede el ancho de pagina, **When** se convierte a PDF, **Then** el diagrama se escala proporcionalmente para caber dentro de los margenes.

---

### User Story 5 - Interfaz web con drag and drop (Priority: P2)

Un usuario no tecnico (PM, technical writer) quiere convertir un documento Markdown
sin usar terminal. Abre la interfaz web, arrastra su archivo, selecciona opciones y
descarga el PDF generado.

**Why this priority**: Expande el publico objetivo mas alla de desarrolladores. Pero
el CLI es el producto principal — la web es un complemento.

**Independent Test**: Abrir la interfaz web, subir un archivo .md via drag-and-drop,
hacer clic en convertir y verificar que se descarga un PDF valido.

**Acceptance Scenarios**:

1. **Given** la interfaz web abierta en un navegador, **When** el usuario arrastra un archivo .md a la zona de drop, **Then** el archivo se muestra como seleccionado con nombre y tamano.
2. **Given** un archivo seleccionado y opciones configuradas, **When** el usuario hace clic en "Convertir", **Then** se genera el PDF y se ofrece para descarga automatica.
3. **Given** un archivo invalido (.txt, .docx), **When** el usuario intenta subirlo, **Then** se muestra un mensaje de error indicando las extensiones permitidas.

---

### User Story 6 - Conversion en lote (Priority: P3)

Un equipo necesita convertir toda una carpeta de documentacion (20+ archivos .md)
a PDF de una vez. Ejecutan un comando batch y obtienen todos los PDFs en un directorio
de salida.

**Why this priority**: Necesario para pipelines de CI/CD y documentacion a escala,
pero la mayoria de usuarios empiezan con archivos individuales.

**Independent Test**: Crear una carpeta con 5 archivos .md y ejecutar batch conversion,
verificando que se generan 5 PDFs correspondientes.

**Acceptance Scenarios**:

1. **Given** un directorio con multiples archivos .md, **When** el usuario ejecuta `mdpdf batch ./docs/ --output ./pdfs/`, **Then** se genera un PDF por cada archivo Markdown encontrado.
2. **Given** un batch de 10 archivos donde 1 tiene errores, **When** se ejecuta la conversion, **Then** los 9 archivos validos se convierten exitosamente y se reporta el error del archivo fallido.

---

### User Story 7 - Configuracion personalizable (Priority: P3)

Un equipo quiere que todos sus documentos usen el mismo tema, margenes y opciones de
TOC. Crean un archivo de configuracion en la raiz del proyecto y todas las conversiones
lo respetan automaticamente.

**Why this priority**: Mejora la experiencia para uso repetido y equipos, pero el
producto funciona perfectamente con defaults sensibles sin configuracion.

**Independent Test**: Crear un archivo .mdpdf.yaml con un tema especifico y verificar
que la conversion usa ese tema sin necesidad de flags CLI.

**Acceptance Scenarios**:

1. **Given** un archivo `.mdpdf.yaml` con `theme: github`, **When** el usuario ejecuta `mdpdf convert doc.md` sin flags, **Then** el PDF usa el tema GitHub.
2. **Given** una configuracion YAML y un flag CLI `--style monokai`, **When** se ejecuta la conversion, **Then** el flag CLI tiene precedencia sobre el archivo de configuracion.

---

### Edge Cases

- Que pasa cuando el archivo Markdown esta vacio?
- Que pasa cuando el archivo tiene encoding BOM (Windows)?
- Que pasa cuando una tabla tiene celdas con contenido multilinea?
- Que pasa cuando un bloque de codigo tiene 500+ lineas?
- Que pasa cuando el Mermaid CLI no esta instalado en el sistema?
- Que pasa cuando el archivo referencia imagenes con paths relativos?
- Que pasa cuando el Markdown contiene HTML embebido?
- Que pasa cuando la ruta de salida no existe y no se puede crear?
- Que pasa cuando se procesan archivos >10MB?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema DEBE convertir archivos Markdown (.md, .markdown, .mdown) a PDF con formato profesional.
- **FR-002**: El sistema DEBE generar tabla de contenido automatica basada en encabezados, con hipervinculos internos funcionales.
- **FR-003**: El sistema DEBE renderizar tablas dentro de los margenes de pagina. Estrategia: reducir fuente hasta 7pt con word-wrap; si aun no cabe, rotar la pagina a landscape automaticamente.
- **FR-004**: El sistema DEBE aplicar syntax highlighting a bloques de codigo fenced con deteccion de lenguaje.
- **FR-005**: El sistema DEBE renderizar diagramas Mermaid como graficos vectoriales (SVG embebido) en el PDF. Mermaid CLI (mmdc) es dependencia obligatoria del sistema.
- **FR-006**: El sistema DEBE implementar saltos de pagina inteligentes que no corten tablas, bloques de codigo ni diagramas.
- **FR-007**: El sistema DEBE soportar multiples temas de estilo (minimo: default, monokai, github, solarized-dark, solarized-light).
- **FR-008**: El sistema DEBE ofrecer una interfaz CLI con comandos: convert (individual), batch (directorio), list-styles, init (configuracion).
- **FR-009**: El sistema DEBE ofrecer una interfaz web con upload via drag-and-drop, seleccion de opciones y descarga del PDF.
- **FR-010**: El sistema DEBE soportar configuracion via archivo YAML con opciones de output, estilo, TOC y flags.
- **FR-011**: El sistema DEBE manejar archivos con encoding UTF-8 (con y sin BOM), normalizando line endings.
- **FR-012**: El sistema DEBE comunicar al usuario UNICAMENTE cuando su sintaxis Mermaid es invalida, mostrando el error especifico del diagrama. Mermaid CLI es dependencia obligatoria del despliegue — su ausencia es un error de instalacion, no del usuario.
- **FR-013**: El sistema DEBE soportar imagenes con paths relativos al archivo Markdown fuente.
- **FR-014**: El sistema DEBE generar PDFs con tipografia profesional, interlineado 1.5 y margenes consistentes.

### Key Entities

- **MarkdownDocument**: Archivo fuente con contenido Markdown. Atributos: ruta, contenido, encoding, metadata frontmatter.
- **PDFDocument**: Archivo de salida generado. Atributos: ruta, tamano, paginas, tema aplicado.
- **ConversionConfig**: Conjunto de opciones que controlan la conversion. Fuentes: CLI flags, archivo YAML, env vars, defaults.
- **Theme**: Conjunto de estilos visuales aplicables (colores de sintaxis, tipografia, spacing). Identificado por nombre.
- **MermaidDiagram**: Bloque de codigo Mermaid dentro del Markdown. Puede estar en estado: valido (renderizable), invalido (fallback a texto), ausente (dependencia no disponible).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Los usuarios pueden convertir un archivo Markdown de 50 paginas a PDF en menos de 30 segundos.
- **SC-002**: El 100% de las tablas en el PDF generado se mantienen dentro de los margenes de pagina.
- **SC-003**: El 100% de los bloques de codigo tienen syntax highlighting visible y nunca se cortan entre paginas.
- **SC-004**: Los diagramas Mermaid validos se renderizan como graficos en el 100% de los casos cuando la dependencia esta disponible.
- **SC-005**: El usuario web puede subir un archivo y descargar el PDF en menos de 3 clics.
- **SC-006**: El sistema funciona sin configuracion previa (zero-config) con resultados profesionales usando defaults.
- **SC-007**: La conversion en lote de 20 archivos se completa exitosamente reportando progreso individual.
- **SC-008**: El sistema maneja gracefully archivos malformados o dependencias ausentes sin crash, siempre con mensaje de error descriptivo.

## Assumptions

- Los usuarios tienen un sistema operativo moderno (Linux, macOS o Windows con WSL).
- El publico principal son desarrolladores y technical writers que ya usan Markdown.
- La interfaz web es para uso local o en red interna — no se disena para produccion con miles de usuarios concurrentes.
- Los archivos Markdown siguen la especificacion CommonMark con extensiones GFM (GitHub Flavored Markdown).
- Mermaid CLI (mmdc) es dependencia obligatoria del sistema. Debe estar instalado en el entorno de despliegue.
- El motor de PDF es WeasyPrint, que soporta CSS Paged Media para control de page breaks y layout.
- Los temas de syntax highlighting se basan en Pygments, que soporta 500+ lenguajes.
- El tamano maximo de archivo razonable es 10MB de Markdown fuente.
- Las imagenes referenciadas en el Markdown deben ser accesibles desde la ruta del archivo fuente.
- Cuando una tabla no cabe en portrait (incluso con font 7pt), se rota automaticamente a landscape.
