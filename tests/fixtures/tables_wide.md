# Tables Test Document

## Simple Table (3 columns)

| Name | Role | Status |
|------|------|--------|
| Alice | Developer | Active |
| Bob | Designer | Active |
| Carol | PM | On leave |

## Medium Table (5 columns)

| ID | Name | Email | Department | Start Date |
|----|------|-------|------------|------------|
| 001 | Alice Johnson | alice@example.com | Engineering | 2023-01-15 |
| 002 | Bob Smith | bob@example.com | Design | 2023-03-20 |
| 003 | Carol Williams | carol@example.com | Product | 2022-11-01 |
| 004 | Dave Brown | dave@example.com | Engineering | 2024-02-10 |
| 005 | Eve Davis | eve@example.com | Marketing | 2023-07-05 |

## Wide Table (8 columns)

| ID | Feature | Priority | Status | Assignee | Sprint | Estimate | Dependencies |
|----|---------|----------|--------|----------|--------|----------|--------------|
| T-001 | User Authentication | High | In Progress | Alice | Sprint 5 | 8 pts | None |
| T-002 | Dashboard Layout | Medium | To Do | Bob | Sprint 6 | 5 pts | T-001 |
| T-003 | API Rate Limiting | High | Done | Carol | Sprint 4 | 3 pts | None |
| T-004 | Email Notifications | Low | To Do | Dave | Sprint 7 | 5 pts | T-001, T-003 |
| T-005 | Data Export CSV | Medium | In Progress | Eve | Sprint 5 | 3 pts | T-003 |

## Extra Wide Table (10+ columns - should trigger landscape)

| ID | Name | Email | Phone | Address | City | State | Zip | Country | Role | Department | Manager |
|----|------|-------|-------|---------|------|-------|-----|---------|------|------------|---------|
| 1 | Alice Johnson | alice@company.com | +1-555-0101 | 123 Main Street | San Francisco | CA | 94102 | USA | Senior Engineer | Platform | Bob Smith |
| 2 | Bob Smith | bob@company.com | +1-555-0102 | 456 Oak Avenue | New York | NY | 10001 | USA | Engineering Manager | Platform | Carol Williams |
| 3 | Carol Williams | carol@company.com | +1-555-0103 | 789 Pine Road | Seattle | WA | 98101 | USA | VP Engineering | Engineering | Dave Brown |

## Table with Long Content

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `max_retries` | `int` | `3` | Maximum number of retry attempts before failing permanently |
| `timeout_seconds` | `float` | `30.0` | Timeout in seconds for each individual request attempt |
| `backoff_factor` | `float` | `1.5` | Exponential backoff multiplier between retry attempts |
| `retry_on_status_codes` | `list[int]` | `[429, 500, 502, 503]` | HTTP status codes that trigger automatic retry behavior |
