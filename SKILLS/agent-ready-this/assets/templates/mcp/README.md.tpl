# MCP integration plan

## Justified capabilities

{{tools_resources_prompts}}

## Transport

{{stdio_or_streamable_http_and_reason}}

## Authentication and authorization

{{identity_scopes_object_level_checks}}

## Tool policy

- separate read-only and mutating tools;
- narrow schemas and bounded outputs;
- explicit side effects;
- confirmation for consequential actions;
- idempotency and audit logs;
- no arbitrary shell, SQL, filesystem, or HTTP proxy.

## Validation

{{contract_functional_negative_security_tests}}
