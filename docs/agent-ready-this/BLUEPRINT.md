> Historical design proposal, not executable instructions. Use [SKILL.md](SKILL.md) for current scope and [README.md](README.md) for implemented commands. The current package does not implement the mutation, manifest, or refresh engines described below.

# Agent Ready This — Blueprint de la skill

**Nombre definitivo:** `agent-ready-this`  
**Estado del paquete:** diseño v0.2 + scaffold ejecutable de assessment; todavía no muta repositorios automáticamente.  
**Principio central:** primero analiza, luego recomienda y solo después ejecuta una **Grill Session** cuando faltan decisiones materiales.  
**Última revisión del diseño:** 2026-09-04.

## 1. Posicionamiento

`agent-ready-this` no es un generador de archivos de moda. Es una skill de diagnóstico, decisión, implementación y mantenimiento para transformar un proyecto existente en un sistema que agentes de desarrollo puedan comprender, modificar y validar de forma segura.

Cuando el producto lo justifica, también puede preparar interfaces para que otros agentes lo consuman en runtime. Esa segunda parte es optativa y se gobierna por capacidades, seguridad y valor real.

Su flujo canónico es:

```text
analizar el proyecto
→ verificar evidencia
→ presentar recomendaciones preliminares
→ evaluar el Grill Gate
→ realizar Grill Session solo si hace falta
→ recalcular recomendaciones finales
→ planificar operaciones
→ aplicar con aprobación explícita
→ validar
→ emitir receipt y controlar drift
```

La skill debe evitar dos fallas frecuentes:

1. preguntar al usuario cosas que ya están en el repositorio;
2. agregar `AGENTS.md`, skills, MCP, WebMCP, A2A y otros artefactos sin demostrar para qué sirven en ese proyecto.

## 2. Resultado esperado

Al finalizar un ciclo completo, el proyecto debería ofrecer:

- instalación y comandos de calidad reproducibles;
- instrucciones canónicas, concisas y jerárquicas;
- mapa de arquitectura y ownership verificable;
- workflows repetibles convertidos en Agent Skills cuando aporten valor;
- adapters mínimos para clientes realmente utilizados;
- CI y evals que demuestren agent readiness;
- estrategia de ownership y actualización sin clobbering;
- contratos e interfaces runtime únicamente cuando sean aplicables;
- límites de seguridad, autorización y efectos secundarios explícitos;
- un manifest mantenible y un receipt de lo aplicado.

## 3. Dos planos independientes

### Plano A — Proyecto listo para agentes de desarrollo

Aplica a casi cualquier repositorio mantenido:

- comandos deterministas de instalación, build, lint, typecheck y tests;
- `AGENTS.md` raíz y anidados cuando existan scopes realmente distintos;
- documentación de arquitectura, comandos, constraints, ownership y seguridad;
- Agent Skills locales para procedimientos repetibles;
- adapters finos para Codex, Claude Code, Cursor, Copilot, OpenCode y otros targets confirmados;
- hooks para políticas deterministas;
- CI, evaluaciones y drift detection.

### Plano B — Producto consumible por agentes en runtime

Se activa solo por evidencia e intención:

- `llms.txt` y versiones Markdown para contenido web público;
- OpenAPI, JSON Schema, Arazzo o AsyncAPI para contratos existentes;
- WebMCP para acciones que dependen de una página abierta y su sesión;
- MCP para herramientas o datos utilizables sin depender de una página abierta;
- MCP Apps para resultados que necesitan una UI interactiva;
- A2A cuando el producto es un agente independiente que recibe tareas;
- ARD cuando se publican varios recursos agentic estables;
- packs de protocolos de dominio cuando exista un caso comercial concreto.

Un proyecto puede completar perfectamente el Plano A y omitir por completo el Plano B.

## 4. Principios no negociables

1. **Analyze first.** La skill inspecciona antes de preguntar, recomendar o modificar.
2. **Evidence first.** Comandos, paths y restricciones salen de manifests, CI, código, tests y documentación; nunca de suposiciones.
3. **Recommend before patch.** El usuario ve el diagnóstico y las operaciones propuestas antes de la mutación.
4. **Canonical first.** Una fuente de verdad y adapters pequeños; no seis manuales divergentes.
5. **Capability driven.** Cada artefacto necesita trigger, evidencia, beneficio, costo y condición de exclusión.
6. **Questions must earn their place.** Cada pregunta de Grill debe cambiar una decisión real.
7. **Experimental is opt-in.** Toda superficie experimental requiere feature detection, fallback y aislamiento del flujo crítico.
8. **Human parity.** Las acciones agentic reutilizan auth, authz, validación y lógica de dominio de la experiencia humana.
9. **Least privilege.** Inputs estrechos, separación read/write, scopes, confirmación e idempotencia.
10. **Managed ownership.** No se reemplaza contenido humano silenciosamente.
11. **Cross-platform.** Evitar symlinks y assumptions Unix por defecto; Windows y worktrees son first-class.
12. **Measurable readiness.** La presencia de archivos no alcanza: deben existir checks, evals y receipts.
13. **Partial blocking.** Una incógnita de MCP no debe frenar la mejora segura de `AGENTS.md`, comandos o CI.
14. **No repeated questions.** La conversación, el repositorio y respuestas previas forman parte de la evidencia.

## 5. Flujo operativo canónico

### Etapa 0 — Preflight

- resolver root, worktree y scopes;
- leer instrucciones locales aplicables;
- revisar estado de Git sin descartar cambios;
- identificar archivos humanos, administrados y generados;
- definir un output directory para reportes;
- evitar cualquier mutación de source durante `assess`.

### Etapa 1 — Repository analysis

El inspector detecta:

- lenguajes, frameworks y gestores de paquetes;
- lockfiles y estrategia de instalación;
- topología de paquetes y monorepo;
- scripts de build, lint, typecheck, tests, e2e y format;
- CI, deployment y release workflows;
- tests y fixtures;
- documentación de arquitectura, seguridad y ownership;
- instrucciones agentic y adapters existentes;
- rutas API, contenido público, eventos, auth y persistencia;
- integraciones runtime ya presentes;
- posibles contradicciones y riesgos sin copiar secretos.

La salida es `audit.json`.

### Etapa 2 — Evidence verification

Los hallazgos heurísticos de alto impacto se verifican directamente:

- ejecutar o inspeccionar el comando real;
- contrastar manifest y CI;
- comprobar rutas y scopes;
- confirmar que un contrato coincide con implementation;
- revisar que authn no se esté confundiendo con authz;
- distinguir archivos actuales de vestigios abandonados.

### Etapa 3 — Preliminary recommendations

Antes de preguntar, la skill entrega:

- estado actual;
- fortalezas aprovechables;
- gaps;
- recomendaciones `P0`–`P3`;
- integraciones aplicables, condicionales, bloqueadas y descartadas;
- evidencia y nivel de confianza;
- costo, impacto y riesgo;
- operaciones y artefactos esperados;
- aceptación mínima.

La salida es `recommendations.preliminary.json` y una vista Markdown.

### Etapa 4 — Grill Gate

Se mide si las incógnitas restantes cambian materialmente:

- arquitectura;
- protocolo;
- superficie pública;
- seguridad;
- ownership;
- comandos autoritativos;
- workflows a convertir en skills;
- target clients;
- deployment;
- task lifecycle;
- acceptance criteria.

El gate devuelve:

```text
skipped | useful | required
```

### Etapa 5 — Grill Session

Cuando el gate no se saltea, se presenta un máximo de cinco preguntas por ronda, priorizadas por reducción de riesgo e information gain.

Cada pregunta incluye:

- hallazgo;
- evidencia;
- decisión afectada;
- recomendación actual;
- opciones concretas cuando corresponde;
- default seguro;
- consecuencia de no responder.

### Etapa 6 — Recommendation recomputation

Las respuestas producen:

- actualización de facts y capability graph;
- decision log con fuente de cada respuesta;
- eliminación de preguntas ya irrelevantes;
- `recommendations.final.json`;
- accepted/deferred/rejected/blocked states;
- manifest de operaciones.

### Etapa 7 — Apply

El baseline se aplica primero. Runtime requiere aprobación explícita y Grill blockers resueltos para esa capability.

### Etapa 8 — Validate and receipt

Se ejecutan los gates del proyecto y los validadores agentic. El receipt conserva:

- decisiones;
- respuestas;
- defaults;
- diffs;
- comandos;
- resultados;
- riesgos residuales;
- score;
- hashes y drift state.

## 6. Arquitectura

```mermaid
flowchart TB
  R[Repositorio + contexto del usuario] --> I[Inspector read-only]
  I --> E[Evidence graph]
  E --> P[Project profiler]
  E --> C[Capability inventory]
  S[Standards + adapters registry] --> D[Recommendation engine]
  P --> D
  C --> D
  D --> PR[Preliminary recommendations]
  PR --> G{Grill Gate}
  G -->|skipped| FR[Final recommendations]
  G -->|useful|required| QS[Adaptive Grill Session]
  QS --> DL[Decision log]
  DL --> FR
  FR --> M[Operations manifest]
  M --> B[Development baseline]
  M --> W[Web + contracts]
  M --> X[Runtime interfaces]
  M --> V[Vendor adapters]
  B --> Q[Validation + evals]
  W --> Q
  X --> Q
  V --> Q
  Q --> O[Receipt + score + drift state]
```

### Componentes internos

- **Inspector:** inventario read-only.
- **Evidence graph:** facts con source, confidence y freshness.
- **Project profiler:** clasificación multi-label.
- **Capability inventory:** lo que ya existe, lo que falta y lo que está roto.
- **Standards registry:** metadata versionada por integración.
- **Recommendation engine:** aplicabilidad, acción, prioridad, valor y riesgo.
- **Grill Gate:** materialidad de unknowns.
- **Grill planner:** preguntas adaptativas y rounds.
- **Decision log:** respuestas explícitas, inferencias y defaults.
- **Manifest builder:** operaciones, ownership y acceptance criteria.
- **Renderers:** artefactos canónicos y adapters.
- **Validators/evals:** proof de funcionamiento.
- **Drift manager:** sincronización sin clobbering.

## 7. Modos de operación

| Modo | Mutación de source | Resultado |
|---|---:|---|
| `assess` | No | Análisis, recomendaciones preliminares, Grill Gate y primera ronda opcional |
| `audit` | No | Evidencia cruda; modo interno/debug |
| `plan` | No | Recomendaciones finales, decision log, manifest y aceptación |
| `apply-baseline` | Sí | Instrucciones, docs, skills, adapters, CI, evals y drift |
| `apply-runtime` | Sí, explícita | WebMCP/MCP/MCP Apps/A2A/ARD u otros módulos aprobados |
| `validate` | No salvo reportes | Checks estructurales, proyecto, seguridad y agentic evals |
| `refresh` | Controlada | Actualización de bloques propios y reporte de drift/conflicts |

`assess` es el default. `apply-runtime` jamás se infiere de una solicitud vaga.

## 8. Contrato de la primera respuesta

La primera respuesta de una ejecución normal debe seguir este orden:

```md
# Agent Ready This assessment

## Project snapshot
## Evidence-backed current state
## Do now
## Do next
## Conditional / plan-only
## Blocked
## Do not add now
## Grill Gate
## Grill Session — Round 1   # solo si corresponde
## Safe next action
```

La respuesta no debe abrir con “¿qué agentes usás?” si la respuesta está en archivos existentes o contexto previo.

## 9. Modelo de recomendación

Cada recomendación contiene:

```json
{
  "id": "mcp-server",
  "title": "Headless agent tools and resources",
  "capability": "MCP",
  "layer": "runtime",
  "applicability": "conditional",
  "action": "investigate",
  "priority": "P2",
  "confidence": "medium",
  "impact": "high",
  "effort": "high",
  "risk": "high",
  "reason": "Reusable page-independent actions exist, but caller and authorization boundaries are unresolved.",
  "evidence": ["src/server/actions/export-project.ts"],
  "unknowns": ["Caller, transport, authorization unit and mutation policy."],
  "expected_artifacts": ["src/agent-tools/mcp/*"],
  "prerequisites": ["Shared domain action layer"],
  "acceptance_criteria": ["Cross-tenant access is denied in negative tests."],
  "rejected_alternatives": ["Generic shell or SQL tool"],
  "grill_topics": ["runtime_consumers", "authz_model", "transport_deployment"]
}
```

### Applicability

- `required`;
- `recommended`;
- `conditional`;
- `report-only`;
- `not-applicable`;
- `blocked`.

### Action

- `create`;
- `update`;
- `repair`;
- `validate`;
- `investigate`;
- `skip`.

### Prioridad

- `P0`: bloquea agent readiness básica o seguridad;
- `P1`: alto valor inmediato;
- `P2`: siguiente etapa con valor demostrado;
- `P3`: advanced, experimental o de bajo retorno inicial.

## 10. Grill Gate

### Objetivo

Determinar si vale la pena interrumpir la ejecución para preguntarle algo al usuario.

### Modelo de materialidad

| Factor | Rango |
|---|---:|
| Impacto sobre decisión/arquitectura | 0–3 |
| Impacto de seguridad | 0–3 |
| Irreversibilidad/costo de revertir | 0–2 |
| Gap de evidencia | 0–2 |

Interpretación:

- `0–3`: usar default reversible; no preguntar;
- `4–5`: pregunta menor/útil;
- `6–7`: pregunta mayor;
- `8–10`: pregunta blocking.

### `skipped`

Se usa cuando:

- la evidencia ya resuelve las decisiones;
- el usuario ya respondió;
- solo quedan preferencias cosméticas;
- hay defaults seguros y reversibles;
- las capabilities dudosas pueden quedar `not-applicable` o `plan-only` sin afectar el baseline.

### `useful`

Se usa cuando las respuestas mejorarían:

- elección de workflows para skills;
- targets de adapters;
- orden de rollout;
- definición de success metrics;
- selección entre dos variantes de costo similar.

El baseline puede avanzar mientras tanto.

### `required`

Se usa cuando falta definir:

- autorización o tenancy;
- mutaciones, confirmación o idempotencia;
- exposición pública/privada;
- local versus remote trust boundary;
- task lifecycle de un agente A2A;
- ownership conflictivo;
- comandos P0 imposibles de establecer;
- fallback de un protocolo experimental que entraría en el critical path.

## 11. Grill Session

### Reglas

- se pregunta después del análisis y las recomendaciones;
- máximo cinco preguntas por round;
- máximo quince por default;
- blocking antes que major, major antes que minor;
- cada pregunta afecta al menos una recommendation ID;
- se incluye recomendación actual, no se devuelve el diseño al usuario;
- se acepta respuesta en prosa o por IDs;
- se recalcula después de cada round;
- se eliminan preguntas resueltas indirectamente;
- se detiene cuando ninguna respuesta restante cambiaría el plan;
- se formula en el idioma del usuario.

### Formato

```md
### G-12 — Authorization unit [blocking]

**Finding:** El proyecto tiene auth y persistencia, pero no se encontró authz por recurso.
**Evidence:** `src/auth/*`, `src/db/*`
**Why this changes the plan:** MCP writes no pueden habilitarse sin aislamiento por usuario/proyecto.
**Current recommendation:** reutilizar la capa server-side existente y agregar negative tests cross-tenant.
**Question:** ¿Cuál es la unidad autoritativa de autorización?

- A — usuario
- B — organización
- C — proyecto/recurso

**Safe default:** bloquear writes runtime y permitir solo operaciones locales/read-only.
**Affects:** `mcp-server`, `security-boundaries`
```

### Fuentes de respuestas

- `repository-evidence`;
- `explicit-user-answer`;
- `prior-user-context`;
- `inferred-from-evidence`;
- `safe-default`;
- `deferred`.

La skill no puede etiquetar una inferencia como decisión explícita.

## 12. Perfilado del proyecto

La clasificación es multi-label:

- sitio/documentación;
- SPA;
- full-stack web;
- API/service;
- library/SDK;
- CLI/tool;
- desktop app;
- monorepo;
- game/editor/tooling;
- agent service;
- event-driven service.

Cada perfil incluye `confidence`, `evidence[]` y `unknowns[]`.

## 13. Matriz principal de capacidades

| Capacidad | Trigger | Resultado | Excluir/defer cuando | Grill típico |
|---|---|---|---|---|
| Canonical instructions | Repo mantenido | `AGENTS.md` | No hay código/operación | Conflicto de ownership |
| Scoped instructions | Monorepo/scopes divergentes | `<scope>/AGENTS.md` | Root alcanza | Ownership/comandos por package |
| Project map | Topología no trivial | `docs/agent/*` | Proyecto trivial | Normalmente ninguno |
| Quality contract | Todo repo mantenido | comandos + CI | Nunca; faltantes bloquean | Autoridad de comandos incierta |
| Agent Skills | Workflows repetidos | `.agents/skills/*` | Regla trivial | Prioridad de workflows |
| Vendor adapters | Cliente detectado/target | adapter delta-only | Duplicación | Targets desconocidos |
| llms.txt | Contenido público estable | `/llms.txt` | App privada | Scope público/base URL |
| OpenAPI | API HTTP estable | `openapi.yaml` | API interna inestable | Rutas soportadas |
| Arazzo | Workflows API multi-step | `arazzo.yaml` | CRUD simple | Workflows importantes |
| AsyncAPI | Eventos contractuales | `asyncapi.yaml` | Eventos internos | Consumidores/canales |
| WebMCP | Acción dentro de página | adapter page-local | Debe funcionar headless | Página vs headless, authz, fallback |
| MCP | Tool/data headless | MCP server | Solo UI visual | Caller, transport, authz, writes |
| MCP Apps | Resultado visual | UI resource | JSON/texto alcanza | Necesidad visual concreta |
| A2A | Agente independiente | Agent Card + lifecycle | API/tool normal | Lifecycle, cancellation, artifacts |
| ARD | Varios recursos públicos | catalog | Recurso único/privado | Scope y trust metadata |

## 14. Superestructura de un proyecto preparado

No se generan todos los paths:

```text
repo/
├─ AGENTS.md
├─ apps/*/AGENTS.md                     # solo scopes divergentes
├─ packages/*/AGENTS.md
├─ .agents/
│  └─ skills/
│     ├─ run-quality-gates/SKILL.md
│     ├─ implement-feature-safely/SKILL.md
│     └─ release-project/SKILL.md
├─ docs/
│  └─ agent/
│     ├─ PROJECT_MAP.md
│     ├─ ARCHITECTURE.md
│     ├─ COMMANDS.md
│     ├─ CONSTRAINTS.md
│     ├─ OWNERSHIP.md
│     ├─ TEST_STRATEGY.md
│     └─ SECURITY_BOUNDARIES.md
├─ public/
│  ├─ llms.txt
│  └─ .well-known/
│     ├─ agent-card.json
│     └─ ai-catalog.json
├─ openapi.yaml
├─ arazzo.yaml
├─ asyncapi.yaml
├─ src/agent-tools/
│  ├─ shared-domain-actions/
│  ├─ webmcp/
│  ├─ mcp/
│  └─ mcp-apps/
├─ .github/
│  ├─ workflows/agent-readiness.yml
│  ├─ copilot-instructions.md
│  ├─ instructions/
│  └─ agents/
├─ .cursor/rules/
├─ .claude/rules/
└─ .agent-ready/
   ├─ config.json
   ├─ audit.json
   ├─ recommendations.preliminary.json
   ├─ grill-session.json
   ├─ answers.json
   ├─ decision-log.json
   ├─ recommendations.final.json
   ├─ manifest.json
   ├─ validation.json
   ├─ receipt.json
   └─ report.md
```

## 15. Estructura de la propia skill

```text
agent-ready-this/
├─ SKILL.md
├─ agents/openai.yaml
├─ BLUEPRINT.md
├─ scripts/
│  ├─ inspect_repo.py
│  ├─ decide_integrations.py
│  ├─ build_grill_session.py
│  ├─ assess_project.py
│  └─ validate_artifacts.py
├─ references/
│  ├─ grill-session-protocol.md
│  ├─ project-profiles.md
│  ├─ decision-matrix.md
│  ├─ artifact-catalog.md
│  ├─ vendor-adapters.md
│  ├─ security-model.md
│  ├─ managed-files-policy.md
│  ├─ validation-rubric.md
│  └─ standards-registry.json
├─ schemas/
│  ├─ agent-ready.config.schema.json
│  ├─ audit-report.schema.json
│  ├─ recommendations.schema.json
│  └─ grill-session.schema.json
├─ assets/templates/
└─ evals/evals.json
```

## 16. Fuente canónica y adapters

### Canonical

- `AGENTS.md`: entrada breve y permanente;
- `docs/agent/*`: conocimiento profundo;
- `.agents/skills/*`: workflows cargados por relevancia;
- scripts compartidos: comportamiento determinista;
- `.agent-ready/manifest.json`: ownership, sources y hashes.

### Adapter

Un adapter solo contiene:

1. configuración específica del cliente;
2. referencia al canonical cuando sea posible;
3. deltas sin equivalente portable;
4. metadata de source y generación.

Nunca copia el manual completo.

### Targets

Tier 1 inicial:

- Codex/OpenAI;
- Claude Code;
- Cursor;
- GitHub Copilot;
- OpenCode.

Tier 2 registry-driven:

- Windsurf;
- Cline;
- Kiro;
- Aider;
- Gemini CLI;
- otros clientes confirmados.

## 17. Ownership y edición segura

Clases:

- `human`;
- `managed-blocks`;
- `generated`;
- `proposal`.

Ejemplo:

```md
<!-- agent-ready:start id=quality-commands source=package.json#scripts -->
- `pnpm lint`
- `pnpm typecheck`
- `pnpm test`
<!-- agent-ready:end -->
```

Algoritmo:

1. leer manifest previo;
2. recalcular sources y hashes;
3. leer target actual;
4. crear si no existe;
5. regenerar solo si hash previo coincide;
6. preservar regiones humanas;
7. reportar conflicto si cambió un managed block externamente;
8. nunca resolver conflicto semántico silenciosamente;
9. actualizar manifest solo después de validar.

## 18. Seguridad

Todo runtime module debe exigir:

- inputs pequeños y tipados;
- `additionalProperties: false` cuando aplique;
- authn y authz server-side;
- aislamiento por recurso/tenant;
- separación read/write;
- side effects declarados;
- preview/confirmación para efectos importantes;
- idempotency keys;
- rate limit, timeout, cancellation y cuotas;
- audit log sin secretos;
- sanitización de outputs;
- scopes mínimos y credenciales de corta vida;
- sandbox para procesos locales;
- negative tests;
- fallback humano o API estable para surfaces experimentales.

Bloqueos automáticos:

```text
arbitrary shell
arbitrary SQL
arbitrary filesystem/network
unknown authorization
unknown tenant boundary
unconfirmed destructive writes
secrets embedded in metadata
experimental critical path without fallback
```

## 19. Validación

### Estructural

- frontmatter y nombre de skills;
- jerarquía de `AGENTS.md`;
- recommendations y Grill schemas;
- managed markers;
- `llms.txt` y links;
- OpenAPI/Arazzo/AsyncAPI;
- Agent Card y catalogs;
- vendor formats.

### Proyecto

- clean install;
- build;
- lint;
- typecheck;
- tests;
- e2e/smoke;
- migrations y fixtures;
- scopes correctos;
- cross-platform cuando corresponda.

### Runtime y seguridad

- schemas de tools;
- authz positivo y negativo;
- cross-tenant denial;
- idempotencia/retry;
- confirmation;
- auditability;
- feature detection/fallback;
- cancellation/timeouts;
- transport local/remoto.

### Agentic evals

1. analiza antes de preguntar;
2. no pregunta facts disponibles;
3. recomienda antes de modificar;
4. ubica dónde cambiar sin editar prematuramente;
5. usa el scope y comandos correctos;
6. activa skills solo cuando corresponde;
7. no agrega runtime protocols por default;
8. bloquea únicamente la capability insegura;
9. pide confirmación para acciones sensibles;
10. detecta drift o contradicción;
11. registra fuentes de respuestas Grill;
12. recalcula recomendaciones tras las respuestas.

## 20. Readiness score

| Pilar | Peso |
|---|---:|
| Setup/build/test deterministas | 20 |
| Instrucciones canónicas y scopes | 20 |
| Skills y contexto reutilizable | 15 |
| Interfaces machine-readable aplicables | 15 |
| Seguridad, permisos y ownership | 20 |
| CI, evals y drift | 10 |

### Gates críticos

No se etiqueta “agent-ready” si:

- no existe install/build verificable;
- las instrucciones se contradicen;
- hay secretos expuestos;
- un runtime write carece de authz/confirmation;
- un agent interface evita la lógica de dominio;
- un experimental API es dependencia crítica sin fallback;
- no existe ownership/update strategy;
- hay Grill blockers abiertos para capacidades que se pretende publicar.

## 21. Outputs del assessment

```text
.agent-ready/
├─ audit.json
├─ recommendations.preliminary.json
├─ grill-session.json
└─ assessment.md
```

El scaffold v0.2 ya genera estos cuatro outputs con:

```bash
python scripts/assess_project.py \
  --repo /path/to/repo \
  --output-dir /path/to/assessment
```

Flags permiten declarar intención runtime sin asumirla:

```text
--public-web
--authenticated-ui-actions
--headless-actions
--visual-tool-results
--agent-service
--public-discovery
--sensitive-actions
--target-vendor <name>
--experimental off|report-only|allow
--grill-mode auto|off|force
```

## 22. Roadmap

### Fase 0 — Contract and evidence model

- schemas de audit/recommendations/grill/manifest/receipt;
- evidence graph;
- standards and adapters registry;
- ownership y conflict policy;
- fixtures.

### Fase 1 — Analyze-first MVP

- inspector ampliado;
- profiler;
- preliminary recommendation engine;
- Grill Gate;
- adaptive rounds;
- decision log;
- Markdown report;
- structural validation.

### Fase 2 — Baseline application

- patch planner;
- manifest builder;
- `AGENTS.md` renderer;
- docs agent;
- skill generator;
- adapter generator;
- CI, evals y drift;
- dry-run y three-way conflict handling.

### Fase 3 — Web and contracts

- `llms.txt` y public link validation;
- OpenAPI/JSON Schema;
- Arazzo;
- AsyncAPI;
- contract drift checks.

### Fase 4 — Runtime

- shared domain action layer;
- WebMCP adapter;
- MCP local/remoto;
- MCP Apps;
- auth/scopes/confirmation/idempotency;
- functional and negative evals.

### Fase 5 — Interoperability

- A2A lifecycle y Agent Card;
- ARD catalogs;
- protocol packs;
- plugin packaging;
- registry extensible.

## 23. Backlog inicial

### E00 — Foundation

- T001: config schema definitivo.
- T002: evidence and source model.
- T003: recommendations schema.
- T004: Grill schema and decision log.
- T005: manifest/receipt schemas.
- T006: standards registry con freshness.

### E10 — Inspector

- T010: languages/manifests/package managers.
- T011: commands desde manifests, task runners y CI.
- T012: monorepo y scopes.
- T013: docs/auth/API/events/agent files.
- T014: tracked sensitive filename detector sin leer valores.
- T015: contradiction/staleness detection.

### E20 — Recommendations

- T020: profiles multi-label.
- T021: capability rules.
- T022: priorities, impact, effort, risk.
- T023: rejected alternatives.
- T024: acceptance criteria.
- T025: score y critical gates.

### E30 — Grill Engine

- T030: materiality scoring.
- T031: question library.
- T032: context-based suppression.
- T033: rounds and dependency graph.
- T034: answer source tracking.
- T035: recommendation recomputation.
- T036: early stop and partial blocking.

### E40 — Baseline Renderers

- T040: root/scoped `AGENTS.md`.
- T041: project map/docs.
- T042: Agent Skills.
- T043: vendor adapters.
- T044: CI/evals/drift.
- T045: patch and conflict engine.

### E50 — Web and contracts

- T050: `llms.txt`.
- T051: Markdown alternates.
- T052: OpenAPI/JSON Schema.
- T053: Arazzo.
- T054: AsyncAPI.

### E60 — Runtime

- T060: domain action extraction.
- T061: WebMCP.
- T062: MCP.
- T063: MCP Apps.
- T064: A2A.
- T065: ARD.

### E70 — Security

- T070: read/write policy.
- T071: authn/authz/tenant scopes.
- T072: confirmation/idempotency.
- T073: sandbox and local restrictions.
- T074: audit logs and PII policy.
- T075: negative tests.

### E80 — Distribution

- T080: portable Agent Skill.
- T081: CLI.
- T082: plugin packages.
- T083: registry extension API.
- T084: signed release receipts.

## 24. Alcance recomendado para v1

La primera versión productiva debería resolver muy bien:

1. `assess` read-only;
2. diagnóstico con evidencia;
3. recomendaciones ordenadas;
4. Grill Gate y rounds adaptativos;
5. decision log;
6. baseline planning;
7. `AGENTS.md`, docs, project skills y adapters Tier 1;
8. CI/evals/drift;
9. `llms.txt`, OpenAPI, WebMCP y MCP en plan/scaffold;
10. runtime apply todavía explícito y fuertemente gated.

A2A, ARD, MCP Apps y protocol packs deben permanecer advanced/opt-in hasta que las bases de aplicación, seguridad y mantenimiento sean confiables.

## 25. Fuentes técnicas registradas

- Agent Skills specification: https://agentskills.io/specification
- AGENTS.md: https://agents.md/
- llms.txt proposal: https://llmstxt.org/
- MCP specification: https://modelcontextprotocol.io/specification/
- MCP security guidance: https://modelcontextprotocol.io/docs/
- WebMCP documentation: https://developer.chrome.com/docs/ai/webmcp
- A2A specification: https://a2a-protocol.org/latest/specification/
- OpenAPI Initiative specifications: https://spec.openapis.org/

El standards registry debe conservar versión exacta, estado de madurez, fecha de verificación y validadores; el texto de la skill no debe asumir que una superficie cambiante permanece igual indefinidamente.
