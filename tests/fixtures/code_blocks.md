# Code Blocks Test Document

## Python

```python
from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol


class Converter(Protocol):
    """Protocol for document converters."""

    def convert(self, input_path: Path, output_path: Path) -> None:
        """Convert a document from input to output format."""
        ...


@dataclass
class ConversionResult:
    success: bool
    output_path: Path | None = None
    pages: int = 0
    warnings: list[str] = field(default_factory=list)
    error: str | None = None

    @property
    def has_warnings(self) -> bool:
        return len(self.warnings) > 0
```

## JavaScript

```javascript
class EventEmitter {
  constructor() {
    this.listeners = new Map();
  }

  on(event, callback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, []);
    }
    this.listeners.get(event).push(callback);
    return this;
  }

  emit(event, ...args) {
    const callbacks = this.listeners.get(event) || [];
    callbacks.forEach(cb => cb(...args));
  }
}

// Usage
const emitter = new EventEmitter();
emitter.on('data', (payload) => console.log(`Received: ${JSON.stringify(payload)}`));
emitter.emit('data', { id: 1, name: 'test', timestamp: Date.now() });
```

## SQL

```sql
SELECT
    u.id,
    u.username,
    u.email,
    COUNT(o.id) AS total_orders,
    COALESCE(SUM(o.amount), 0) AS total_spent,
    MAX(o.created_at) AS last_order_date
FROM users u
LEFT JOIN orders o ON o.user_id = u.id
WHERE u.created_at >= '2024-01-01'
    AND u.status = 'active'
GROUP BY u.id, u.username, u.email
HAVING COUNT(o.id) > 0
ORDER BY total_spent DESC
LIMIT 50;
```

## YAML

```yaml
services:
  web:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/app
      - REDIS_URL=redis://cache:6379/0
    depends_on:
      - db
      - cache
    volumes:
      - ./src:/app/src
      - ./tests:/app/tests

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: app
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
```

## Bash

```bash
#!/usr/bin/env bash
set -euo pipefail

# Build and deploy script
echo "Building project..."
python -m build
echo "Running tests..."
pytest --cov --cov-fail-under=80
echo "Deploying..."
twine upload dist/*
echo "Done!"
```

## Long Lines (120+ characters - tests word-wrap)

```python
def process_document_with_all_options(input_file: Path, output_dir: Path, theme: str = "default", toc_enabled: bool = True, toc_level: int = 3, verbose: bool = False) -> ConversionResult:
    """This is a function with a very long signature that should trigger word-wrap in the PDF output to verify that long lines are handled correctly without horizontal overflow."""
    result = ConversionResult(success=True, output_path=output_dir / input_file.with_suffix(".pdf").name, pages=0, warnings=[], error=None)
    return result
```
