<!-- Sync Impact Report
Version change: 0.0.0 → 1.0.0
Added sections: All (initial constitution)
Removed sections: None
Follow-up TODOs: None
-->

# MDPDF Constitution

## Core Principles

### I. Rendering Quality First
La calidad del PDF generado es la prioridad absoluta del proyecto. Las tablas NUNCA
deben desbordarse del margen de página — se DEBE auto-ajustar columnas, reducir fuente
o aplicar word-wrap antes de permitir overflow. Los bloques de codigo DEBEN renderizarse
con syntax highlighting, word-wrap inteligente y NUNCA cortarse entre paginas. Los
diagramas Mermaid DEBEN renderizarse como SVG embebido, no como texto plano.

### II. Modularidad y Separacion de Concerns
La arquitectura DEBE seguir una pipeline clara: Parser → Preprocessor → Renderer HTML →
PDF Engine. Cada modulo tiene responsabilidad unica, es independientemente testeable y
reemplazable. Las dependencias externas (Mermaid CLI, Pygments, WeasyPrint) DEBEN estar
encapsuladas detras de interfaces internas para permitir fallbacks y testing aislado.

### III. CLI-First con Web Opcional
El producto principal es el CLI (`mdpdf`). TODA funcionalidad DEBE ser accesible via
linea de comandos antes de exponerse en la interfaz web. La interfaz web es un consumidor
del core, no un path paralelo. El CLI DEBE ser autocontenido y funcionar sin servidor.

### IV. Type Safety y Codigo Documentado
Python 3.11+ con type hints estrictos en todo el codigo fuente. mypy en modo strict
DEBE pasar sin errores. Cada modulo, clase y funcion publica DEBE tener docstrings con
Args, Returns y Raises documentados. El codigo DEBE pasar ruff sin warnings.

### V. Testing Riguroso
Cobertura minima del 80% es obligatoria. Los tests DEBEN cubrir edge cases criticos:
tablas con 10+ columnas, bloques de codigo de 200+ caracteres por linea, diagramas
Mermaid malformados, archivos con BOM, y contenido mixto complejo. Tests de integracion
DEBEN validar el PDF generado contra criterios medibles (tablas dentro de margenes,
imagenes renderizadas).

### VI. Configuracion Flexible y Sensible
El sistema DEBE funcionar sin configuracion (sensible defaults). La configuracion
avanzada se gestiona via archivo YAML, variables de entorno y flags CLI, con precedencia
clara: CLI > env vars > archivo YAML > defaults. Cada opcion DEBE estar documentada
con su valor por defecto.

## Estandares de Calidad del PDF

El PDF generado DEBE cumplir estos criterios verificables:
- Tablas: contenido dentro de margenes, texto legible (minimo 7pt), columnas
  proporcionales al contenido
- Codigo: syntax highlighting visible, fuente monospace, lineas largas con wrap
  (no truncadas), fondo diferenciado
- Mermaid: diagramas renderizados como vectores (SVG), legibles a escala de pagina
- Page breaks: nunca cortar tabla, bloque de codigo o diagrama a mitad; insertar
  salto antes si el elemento no cabe en el espacio restante
- TOC: tabla de contenido con hipervinculos internos funcionales
- Tipografia: fuente profesional, interlineado 1.5, margenes consistentes

## Workflow de Desarrollo

- Desarrollo guiado por Spec-Driven Development (spec-kit)
- Commits convencionales: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`
- Branch strategy: main protegido, features en branches, PR con review
- Pre-commit hooks: ruff + mypy + tests antes de cada commit
- Documentacion en espanol, codigo y API en ingles
- CHANGELOG actualizado en cada release siguiendo Keep a Changelog

## Governance

La constitucion es el documento rector del proyecto. Cualquier decision tecnica o de
arquitectura DEBE ser consistente con estos principios. Las enmiendas requieren:
1. Documentar el cambio propuesto con justificacion
2. Actualizar version siguiendo semver
3. Registrar en CHANGELOG

En caso de conflicto entre velocidad de entrega y calidad de renderizado, la calidad
de renderizado prevalece.

**Version**: 1.0.0 | **Ratified**: 2026-07-29 | **Last Amended**: 2026-07-29
