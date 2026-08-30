# Requirements

Status: DRAFT — not yet approved by the human Product Owner / Chief Engineer.

Produced by `.github/skills/requirements-engineering/SKILL.md`. Every requirement
below has a stable ID referenced by `requirements/traceability-matrix.md`.
Do not delete an ID once assigned, even if the requirement is later dropped —
mark it `Withdrawn` instead, so history stays intact.

## 1. Project

- **Project name**: `<name>`
- **Objective (one paragraph)**: `<what this hardware needs to do and why>`
- **Benchmark / context**: `<e.g. "MCU + IMU + Power Supply" benchmark per docs/architecture.md §11>`

## 2. Functional Requirements

| ID | Requirement | Priority (Must/Should/Could) | Notes |
|---|---|---|---|
| REQ-001 | `<e.g. Read 3-axis acceleration and angular rate at ≥ 100 Hz>` | Must | |

## 3. Electrical Requirements

| ID | Requirement | Priority | Notes |
|---|---|---|---|
| REQ-101 | Supply input: `<voltage range, source type>` | Must | |
| REQ-102 | Logic level: `<e.g. 3.3 V>` | Must | |
| REQ-103 | Total current budget: `<value>` | Must | Feeds `hardware/power-budget.md` |
| REQ-104 | Interfaces required: `<I2C/SPI/UART/etc.>` | Must | |

## 4. Environmental Requirements

| ID | Requirement | Priority | Notes |
|---|---|---|---|
| REQ-201 | Operating temperature range | `<Must/Should>` | UNKNOWN if not yet specified — do not guess |
| REQ-202 | Vibration/shock (if applicable, e.g. rotating body present) | `<Must/Should>` | See `docs/architecture.md` §12 |

## 5. Mechanical / Form Factor Constraints

| ID | Requirement | Priority | Notes |
|---|---|---|---|
| REQ-301 | `<board size / mounting / connector constraints>` | | |

## 6. Safety / Regulatory Constraints

| ID | Requirement | Priority | Notes |
|---|---|---|---|
| REQ-401 | `<e.g. applicable standards, if any — UNKNOWN if not yet determined>` | | See future Safety/Compliance Reviewer role, `docs/architecture.md` §14 |

## 7. Non-functional Requirements

| ID | Requirement | Priority | Notes |
|---|---|---|---|
| REQ-501 | Cost target | | |
| REQ-502 | Schedule target | | |

## 8. Assumptions

- `<list explicit assumptions here — anything not explicitly confirmed by the human or a datasheet is an assumption, not a fact>`

## 9. Open Questions for the Human

- `<questions raised during Requirements Engineering that need a human decision before proceeding>`

## 10. Approval

| Role | Name | Date | Decision |
|---|---|---|---|
| Chief Engineer (Human) | | | Pending |
