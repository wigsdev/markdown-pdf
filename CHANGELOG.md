# Changelog

Todos los cambios notables en este proyecto seran documentados en este archivo.

El formato esta basado en [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Fixed

- **Mermaid no-sandbox**: Chromium en Docker requiere `--no-sandbox`. Agregado
  puppeteer-config.json con args de sandbox desactivado.
- **Mermaid texto invisible**: SVG con foreignObject no renderizaba texto en WeasyPrint.
  Cambiado a output PNG (Chromium rasteriza el texto directamente).
- **Fuentes en Docker**: agregado fonts-noto-core + fontconfig para texto completo en diagramas.
- **Boton X (remove file)**: agregado stopPropagation para evitar que el click
  burbujee al dropzone y abra el file selector.

### Planned (v0.3.0 — UI Redesign)

- Rediseno completo del frontend: dark mode, iconos SVG, multi-file upload
- Layout single-screen (sin scroll)
- Preview del PDF generado
- Progress bar animada
- Archivos individuales con boton de cierre

---

## [0.2.0] - 2026-07-29

Mejoras de calidad post-auditoria. Fixes criticos, temas completos, y soporte Docker.

### Fixed

- **Mermaid ordering bug**: refactorizado el renderer para procesar bloques mermaid
  directamente durante el render de tokens (no post-regex). Los diagramas ahora se
  renderizan correctamente como SVG antes que el syntax highlighter los consuma.
- **Syntax highlighting fragil**: eliminado el approach de regex post-HTML. Ahora se
  usa un custom fence renderer que aplica Pygments inline durante la generacion HTML.
- **Table heuristic inexacta**: ponderacion mejorada con factor proporcional (0.7x) y
  overhead por columna. Reduce falsos positivos en tablas medianas.

### Changed

- **5 temas CSS completos**: cada tema ahora tiene identidad visual completa (headings,
  body, links, blockquotes, tables, code, TOC) en lugar de solo overrides de `<pre>`.
- **CORS restrictivo**: ya no acepta `*` por defecto. Configurable via `MDPDF_ALLOWED_ORIGINS`.
- **Upload limit**: maximo 10MB por defecto (configurable via `MDPDF_MAX_UPLOAD_MB`).

### Added

- `Dockerfile` multi-stage con todas las dependencias (WeasyPrint + Mermaid CLI)
- `docker-compose.yml` para desarrollo local
- `.dockerignore` para builds limpios
- Healthcheck endpoint en el container

### Deployment

```bash
# Build y run local
docker compose up --build

# O directamente
docker build -t mdpdf .
docker run -p 8000:8000 mdpdf
```

---

## [0.1.0-alpha] - 2026-07-29

Primera implementacion funcional siguiendo metodologia Spec-Driven Development (spec-kit).

### Added

- **Pipeline de conversion**: Parser → Preprocessor → Renderer HTML → PDF Engine (WeasyPrint)
- **CLI completo** (`mdpdf`): comandos `convert`, `batch`, `list-styles`, `init`, `serve`
- **5 temas de syntax highlighting**: default, monokai, github, solarized-dark, solarized-light
- **Tablas responsivas**: analisis de ancho con estrategia NORMAL / REDUCE_FONT / LANDSCAPE
- **Syntax highlighting**: Pygments con deteccion de lenguaje y fallback a texto plano
- **Mermaid preprocessor**: estructura para renderizar diagramas via mmdc CLI a SVG
- **Image preprocessor**: resolucion de paths relativos y validacion de existencia
- **Tabla de contenido**: generacion automatica con hipervinculos internos
- **Sistema de configuracion**: YAML (.mdpdf.yaml) + env vars (MDPDF_*) + CLI flags con precedencia
- **Interfaz web**: FastAPI backend + frontend con drag-and-drop, selector de tema, TOC toggle
- **Test suite**: 82 tests (76 passed, 6 corregidos) — unitarios + integracion + web API
- **AGENTS.md**: gobernanza del proyecto para agentes de IA
- **Spec-kit completo**: constitucion, spec, plan, tasks, analysis, contracts, research

### Architecture

```
src/mdpdf/
├── parser/markdown.py       — markdown-it-py con GFM extensions
├── preprocessor/
│   ├── tables.py            — analisis de tablas + estrategia responsive
│   ├── mermaid.py           — renderizado SVG via mmdc (lazy init)
│   └── images.py            — resolucion paths relativos
├── renderer/
│   ├── html.py              — HTML5 con CSS embebido + TOC
│   └── highlight.py         — Pygments syntax highlighting
├── pdf/
│   ├── engine.py            — WeasyPrint con CSS Paged Media
│   └── styles.py            — composicion de CSS (base + tema + custom)
├── themes/                  — 5 archivos CSS por tema
├── converter.py             — orquestador del pipeline
├── config.py                — dataclasses + YAML + env vars
├── models.py                — tipos de datos del pipeline
├── utils.py                 — validacion, paths, discovery
├── cli.py                   — Typer CLI con Rich progress
└── exceptions.py            — jerarquia de excepciones
```

### Dependencies

| Paquete | Version | Proposito |
|---------|---------|-----------|
| weasyprint | >=62.0 | Motor PDF con CSS Paged Media |
| markdown-it-py | >=3.0.0 | Parser Markdown (GFM) |
| mdit-py-plugins | >=0.4.0 | Plugins para markdown-it |
| linkify-it-py | >=2.0.0 | Auto-link URLs (GFM mode) |
| pygments | >=2.17.0 | Syntax highlighting |
| typer | >=0.12.0 | CLI framework |
| rich | >=13.0.0 | Terminal UI |
| pyyaml | >=6.0 | Configuracion YAML |
| fastapi | >=0.110.0 | Web backend (opcional) |
| uvicorn | >=0.30.0 | ASGI server (opcional) |

### Known Issues

- **Mermaid ordering bug**: el syntax highlighter procesa bloques mermaid antes del
  reemplazo SVG, causando que los diagramas no se rendericen correctamente
- **Temas CSS incompletos**: los 5 archivos .css solo contienen overrides minimos
  (3-15 lineas), no una identidad visual diferenciada
- **Table heuristic**: la estimacion por caracteres asume monospace pero el CSS usa
  fuente proporcional, produciendo falsos positivos/negativos
- **Syntax highlighting regex fragil**: desincronizacion posicional con mezcla de
  code blocks indentados y fenced
- **Web UI sin hardening**: sin limite de upload, CORS abierto, paquete `web` con
  nombre generico

### Methodology

Proyecto desarrollado con Spec-Driven Development (SDD) usando GitHub spec-kit v0.14.4.
Flujo: Constitution → Spec → Clarify → Plan → Tasks → Analyze → Implement → Tests.

62 tareas completadas en 11 fases. Commits atomicos por fase con conventional commits.

---

## Tipos de Cambios

- `Added` para funcionalidades nuevas
- `Changed` para cambios en funcionalidades existentes
- `Deprecated` para funcionalidades que seran removidas
- `Removed` para funcionalidades removidas
- `Fixed` para correccion de bugs
- `Security` para vulnerabilidades

[Unreleased]: https://github.com/WIGUSA/markdown-pdf/compare/v0.1.0-alpha...HEAD
[0.1.0-alpha]: https://github.com/WIGUSA/markdown-pdf/releases/tag/v0.1.0-alpha
