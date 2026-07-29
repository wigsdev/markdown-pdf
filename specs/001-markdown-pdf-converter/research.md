# Technology Research: Markdown to PDF Converter

**Date**: 2026-07-29

## PDF Engine: WeasyPrint

**Why WeasyPrint**:
- Soporte completo de CSS Paged Media (@page, page-break-inside, size)
- Renderizado HTML → PDF con fidelidad de layout
- Pure Python con bindings a cairo/pango (no necesita headless browser)
- Activamente mantenido, release estable cada ~2 meses
- Soporta CSS Grid, Flexbox parcial, y table layout algorithm

**Limitaciones conocidas**:
- No soporta JavaScript (no es problema — pre-renderizamos Mermaid)
- Requiere dependencias de sistema: libcairo2, libpango, libgdk-pixbuf
- El CSS Flexbox no tiene soporte completo (usamos tables y block layout)

**Instalación de dependencias de sistema**:
```bash
# Debian/Ubuntu
sudo apt install libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev

# macOS
brew install cairo pango gdk-pixbuf libffi

# Docker (basado en python:3.11-slim)
RUN apt-get update && apt-get install -y \
    libcairo2 libpango-1.0-0 libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 libffi-dev
```

## Markdown Parser: markdown-it-py

**Why markdown-it-py**:
- Implementación Python de markdown-it (reference CommonMark parser)
- Plugin ecosystem: mdit-py-plugins (tables, footnotes, anchors, TOC)
- AST accesible y manipulable (tokens)
- GFM tables via plugin `tables`
- Soporte de fenced code blocks con language detection

**Plugins necesarios**:
- `mdit_py_plugins.tables` — GFM table parsing
- `mdit_py_plugins.anchors` — Heading anchors para TOC
- `mdit_py_plugins.footnote` — Footnotes (opcional)

## Mermaid CLI (mmdc)

**Versión**: >= 10.0
**Instalación**: `npm install -g @mermaid-js/mermaid-cli`

**Uso programático**:
```bash
mmdc -i input.mmd -o output.svg -t neutral --backgroundColor transparent
```

**Integración en el pipeline**:
1. Detectar bloques ```mermaid en el AST
2. Extraer contenido a archivo temporal .mmd
3. Ejecutar `mmdc` via subprocess
4. Leer SVG resultante
5. Reemplazar bloque de código con <img> o inline SVG en el HTML

**Manejo de errores**:
- Si mmdc retorna exit code != 0: bloque inválido
- Capturar stderr para mensaje de error al usuario
- Renderizar como code block + warning visual en el PDF

## Syntax Highlighting: Pygments

**Integración con markdown-it-py**:
- Hook en el renderer de fenced code blocks
- Detectar lenguaje del info string (```python, ```javascript, etc.)
- Aplicar Pygments `highlight()` al contenido
- Inyectar CSS de Pygments como parte del tema

**Temas disponibles** (subset seleccionado):
- default → Pygments `default` style
- monokai → Pygments `monokai` style
- github → Pygments `github-dark` style
- solarized-dark → Pygments `solarized-dark` style
- solarized-light → Pygments `solarized-light` style

## CSS Paged Media para Page Breaks

**Propiedades clave**:
```css
/* Evitar cortar elementos entre páginas */
pre, table, .mermaid-diagram {
    page-break-inside: avoid;
    break-inside: avoid;
}

/* Rotación a landscape para tablas anchas */
.table-landscape {
    page: landscape;
}

@page landscape {
    size: A4 landscape;
}

/* Tabla de contenido */
.toc a::after {
    content: leader('.') target-counter(attr(href), page);
}
```

## Table Responsive Strategy

**Algoritmo de decisión**:
1. Calcular ancho natural de cada columna (basado en contenido)
2. Si ancho_total <= ancho_pagina_portrait: layout normal
3. Si ancho_total > portrait pero cabe con font 7pt + wrap: reducir
4. Si aún no cabe: aplicar clase `.table-landscape` → @page landscape

**Implementación**:
- En el preprocessor, analizar cada tabla del AST
- Calcular caracteres por columna como proxy de ancho
- Inyectar wrapper `<div class="table-responsive">` o `<div class="table-landscape">`
- El CSS de WeasyPrint maneja el cambio de orientación de página
