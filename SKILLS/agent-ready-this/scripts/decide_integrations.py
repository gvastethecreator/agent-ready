#!/usr/bin/env python3
"""Create evidence-backed preliminary recommendations from an agent-ready-this audit."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

GENERATOR = "agent-ready-this@0.3.0-plan"
ACTIVE = {"required", "recommended", "conditional", "report-only", "blocked"}


def rec(
    *,
    id: str,
    title: str,
    capability: str,
    layer: str,
    applicability: str,
    action: str,
    priority: str,
    confidence: str,
    impact: str,
    effort: str,
    risk: str,
    reason: str,
    evidence: list[str] | None = None,
    unknowns: list[str] | None = None,
    expected_artifacts: list[str] | None = None,
    prerequisites: list[str] | None = None,
    acceptance_criteria: list[str] | None = None,
    rejected_alternatives: list[str] | None = None,
    grill_topics: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "id": id,
        "title": title,
        "capability": capability,
        "layer": layer,
        "applicability": applicability,
        "action": action,
        "priority": priority,
        "confidence": confidence,
        "impact": impact,
        "effort": effort,
        "risk": risk,
        "reason": reason,
        "evidence": evidence or [],
        "unknowns": unknowns or [],
        "expected_artifacts": expected_artifacts or [],
        "prerequisites": prerequisites or [],
        "acceptance_criteria": acceptance_criteria or [],
        "rejected_alternatives": rejected_alternatives or [],
        "grill_topics": sorted(set(grill_topics or [])),
        "grill_question_ids": [],
    }


def integration_paths(integrations: dict[str, Any], key: str) -> list[str]:
    value = integrations.get(key, [])
    return [str(item) for item in value] if isinstance(value, list) else []


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit", required=True)
    parser.add_argument("--output")
    parser.add_argument("--public-web", action="store_true")
    parser.add_argument("--authenticated-ui-actions", action="store_true")
    parser.add_argument("--headless-actions", action="store_true")
    parser.add_argument("--visual-tool-results", action="store_true")
    parser.add_argument("--agent-service", action="store_true")
    parser.add_argument("--public-discovery", action="store_true")
    parser.add_argument("--sensitive-actions", action="store_true")
    parser.add_argument("--target-vendor", action="append", default=[])
    parser.add_argument("--experimental", choices=["off", "report-only", "allow"], default="report-only")
    args = parser.parse_args()

    audit_path = Path(args.audit)
    audit = json.loads(audit_path.read_text(encoding="utf-8"))
    signals = audit.get("signals", {})
    inventory = audit.get("inventory", {})
    docs = inventory.get("documentation", {})
    integrations = inventory.get("integrations", {})
    vendor_paths = inventory.get("vendor_paths", {})
    agent_paths = inventory.get("agent_paths", [])
    quality = signals.get("quality_commands", {})
    quality_found = quality.get("found", {}) if isinstance(quality, dict) else {}
    missing_core = quality.get("missing_core", []) if isinstance(quality, dict) else []
    monorepo = list(signals.get("monorepo_evidence", []) or [])
    detected_vendors = list(signals.get("vendor_clients_detected", []) or [])
    explicit_vendors = sorted(set(args.target_vendor))
    target_vendors = sorted(set(detected_vendors + explicit_vendors))
    is_web = bool(signals.get("web_candidate"))
    is_server = bool(signals.get("server_candidate"))
    has_public_content = bool(signals.get("public_content_candidate"))
    has_auth = bool(signals.get("auth_candidate"))
    has_database = bool(signals.get("database_candidate"))
    has_ci = bool(signals.get("ci_candidate"))
    has_events = bool(signals.get("event_driven_candidate"))
    sensitive_runtime = bool(args.sensitive_actions or signals.get("runtime_risk_candidate"))

    recommendations: list[dict[str, Any]] = []

    root_agents = [p for p in agent_paths if p.lower() == "agents.md"]
    other_instruction_files = [
        p for p in agent_paths
        if p not in root_agents and p.rsplit("/", 1)[-1].lower() in {"agents.md", "claude.md", "gemini.md"}
    ]
    instruction_unknowns = (
        ["Existing instruction files may have overlapping ownership or contradictory rules."]
        if len(other_instruction_files) > 1
        else []
    )
    if root_agents and root_agents[0] != "AGENTS.md":
        instruction_unknowns.append(
            f"The root file is named {root_agents[0]}; tools on case-sensitive filesystems look for AGENTS.md."
        )
    recommendations.append(
        rec(
            id="canonical-instructions",
            title="Canonical project instructions",
            capability="AGENTS.md",
            layer="development-baseline",
            applicability="required",
            action="validate" if root_agents else "create",
            priority="P0",
            confidence="high",
            impact="high",
            effort="low",
            risk="low",
            reason=(
                "A root AGENTS.md exists and should be validated as the canonical entry point."
                if root_agents
                else "The repository needs one concise, evidence-backed instruction entry point for coding agents."
            ),
            evidence=root_agents + other_instruction_files[:5],
            unknowns=instruction_unknowns,
            expected_artifacts=["AGENTS.md"],
            acceptance_criteria=[
                "Commands and paths are verified against the repository.",
                "The file links to deeper documentation instead of duplicating it.",
                "Nearest-scope override behavior is documented.",
            ],
            rejected_alternatives=["Copy the same full instruction manual into every vendor file."],
            grill_topics=["ownership_conflicts"] if len(other_instruction_files) > 1 else [],
        )
    )

    recommendations.append(
        rec(
            id="scoped-instructions",
            title="Scoped instructions for divergent packages",
            capability="nested AGENTS.md",
            layer="development-baseline",
            applicability="recommended" if monorepo else "conditional",
            action="create" if monorepo else "investigate",
            priority="P1" if monorepo else "P2",
            confidence="high" if monorepo else "medium",
            impact="high" if monorepo else "medium",
            effort="medium",
            risk="low",
            reason=(
                "Workspace evidence suggests package-level commands or constraints may differ."
                if monorepo
                else "Nested instructions are useful only when a subtree has genuinely different commands or constraints."
            ),
            evidence=monorepo,
            unknowns=["Package ownership and divergent quality gates must be verified."] if monorepo else [],
            expected_artifacts=["<scope>/AGENTS.md"],
            prerequisites=["Map package boundaries and authoritative commands."],
            acceptance_criteria=["Each nested file contains only scope-specific deltas."],
            rejected_alternatives=["Create an AGENTS.md in every folder regardless of scope differences."],
            grill_topics=["package_scope_ownership"] if monorepo and not docs.get("codeowners") else [],
        )
    )

    architecture_exists = bool(docs.get("architecture"))
    recommendations.append(
        rec(
            id="project-map",
            title="Agent-readable project map and architecture boundaries",
            capability="project documentation",
            layer="documentation",
            applicability="recommended",
            action="validate" if architecture_exists else "create",
            priority="P1",
            confidence="high",
            impact="high",
            effort="medium",
            risk="low",
            reason=(
                "An architecture document exists but should be checked for current paths and ownership."
                if architecture_exists
                else "Agents need a compact map of entry points, package responsibilities, data flow, and forbidden boundaries."
            ),
            evidence=[docs.get("architecture")] if architecture_exists else [],
            expected_artifacts=["Existing architecture doc, or one concise map linked from AGENTS.md"],
            acceptance_criteria=[
                "Every documented path exists.",
                "The map distinguishes source, generated files, fixtures, and deployment code.",
                "Architectural boundaries include concrete validation guidance.",
            ],
        )
    )

    quality_evidence: list[str] = []
    core_first = sorted(quality_found, key=lambda name: ("build", "lint", "typecheck", "test").index(name)
                        if name in ("build", "lint", "typecheck", "test") else 9)
    for capability in core_first:
        for match in quality_found[capability][:3]:
            quality_evidence.append(match.get("evidence") or f"{match.get('path')}#scripts.{match.get('script')}")
    convention_only = quality.get("convention_only", []) if isinstance(quality, dict) else []
    quality_applicability = "required"
    quality_priority = "P0"
    if missing_core:
        quality_action = "investigate"
        quality_reason = (
            "Core quality commands are missing or cannot be identified reliably: " + ", ".join(missing_core)
            + ". Check CI, README, and task runners before asking."
        )
        quality_unknowns = ["The authoritative command or accepted substitute for each missing quality gate is unknown."]
        quality_topics = ["quality_commands"]
    else:
        quality_action = "validate"
        quality_reason = "Build, lint, typecheck, and test commands were detected; they still need clean-environment verification."
        if convention_only:
            quality_reason += " Inferred from stack conventions and unverified: " + ", ".join(convention_only) + "."
        quality_unknowns = []
        quality_topics = []
    recommendations.append(
        rec(
            id="quality-command-contract",
            title="Deterministic install and quality command contract",
            capability="build/test commands",
            layer="quality",
            applicability=quality_applicability,
            action=quality_action,
            priority=quality_priority,
            confidence="high",
            impact="high",
            effort="medium" if missing_core else "low",
            risk="medium" if missing_core else "low",
            reason=quality_reason,
            evidence=quality_evidence,
            unknowns=quality_unknowns,
            expected_artifacts=["Commands section in AGENTS.md", "Existing CI gate, when present"],
            prerequisites=["Resolve package scope and environment requirements."],
            acceptance_criteria=[
                "Install works from a clean checkout with the detected lockfile.",
                "Each documented command is executed in the correct scope.",
                "Failures return non-zero status and actionable output.",
            ],
            grill_topics=quality_topics,
        )
    )

    skill_paths = [p for p in agent_paths if "/skills/" in f"/{p}"]
    recommendations.append(
        rec(
            id="project-agent-skills",
            title="Project-local Agent Skills for repeated workflows",
            capability="Agent Skills",
            layer="development-baseline",
            applicability="recommended" if skill_paths else "conditional",
            action="validate" if skill_paths else "investigate",
            priority="P1" if skill_paths else "P2",
            confidence="high" if skill_paths else "medium",
            impact="high",
            effort="medium",
            risk="low",
            reason=(
                "Project-local skills already exist and should be validated for trigger quality and deterministic procedures."
                if skill_paths
                else "Create skills only for repeated, multi-step workflows that benefit from progressive context and scripts."
            ),
            evidence=skill_paths[:20],
            unknowns=[] if skill_paths else ["The highest-value repeated agent workflows have not been established."],
            expected_artifacts=[".agents/skills/<workflow>/SKILL.md"],
            acceptance_criteria=[
                "Each skill has a narrow trigger and verifiable completion criteria.",
                "Scripts contain deterministic operations that should not be reimplemented in prompts.",
            ],
            rejected_alternatives=["Turn every repository rule into a separate skill."],
            grill_topics=[] if skill_paths else ["critical_workflows"],
        )
    )

    if target_vendors:
        adapters_applicability = "recommended"
        adapters_action = "validate" if detected_vendors else "create"
        adapters_reason = "First-class agent clients are detected or explicitly targeted: " + ", ".join(target_vendors) + "."
        adapters_unknowns: list[str] = []
        adapters_topics: list[str] = []
        adapters_evidence = [p for vendor in target_vendors for p in vendor_paths.get(vendor, [])]
    else:
        adapters_applicability = "conditional"
        adapters_action = "investigate"
        adapters_reason = "Vendor adapters should be generated only after first-class clients are known."
        adapters_unknowns = ["No first-class coding-agent clients were detected or explicitly named."]
        adapters_topics = ["target_agents"]
        adapters_evidence = []
    recommendations.append(
        rec(
            id="vendor-adapters",
            title="Thin vendor adapters",
            capability="client-specific instructions",
            layer="vendor-adapter",
            applicability=adapters_applicability,
            action=adapters_action,
            priority="P2",
            confidence="high" if target_vendors else "medium",
            impact="medium",
            effort="medium",
            risk="low",
            reason=adapters_reason,
            evidence=adapters_evidence,
            unknowns=adapters_unknowns,
            expected_artifacts=["Detected client-specific rule/config files"],
            prerequisites=["Establish AGENTS.md and project docs as the canonical source."],
            acceptance_criteria=["Every adapter contains only vendor-specific deltas and source metadata."],
            rejected_alternatives=["Generate every registered vendor file preemptively."],
            grill_topics=adapters_topics,
        )
    )

    recommendations.append(
        rec(
            id="ci-readiness",
            title="CI enforcement for agent-relevant quality gates",
            capability="CI",
            layer="quality",
            applicability="recommended" if has_ci else "conditional",
            action="validate" if has_ci else "investigate",
            priority="P1" if has_ci else "P2",
            confidence="high",
            impact="high" if has_ci else "medium",
            effort="low" if has_ci else "medium",
            risk="low",
            reason=(
                "CI exists and should enforce the same commands agents are instructed to run."
                if has_ci
                else "No CI detected. Add it only for a required merge or release gate: one job running an existing local command."
            ),
            evidence=list(inventory.get("ci_paths", [])),
            expected_artifacts=["Existing CI workflow"] if has_ci else ["One workflow running an existing local command, if required"],
            prerequisites=["Resolve the quality command contract."],
            acceptance_criteria=["CI and local instructions invoke equivalent gates in the correct scopes."],
            rejected_alternatives=["Add jobs, matrices, or runtimes beyond the required gate."],
        )
    )

    security_exists = bool(docs.get("security"))
    recommendations.append(
        rec(
            id="security-boundaries",
            title="Explicit security, data, and mutation boundaries",
            capability="agent security policy",
            layer="governance",
            applicability="required" if sensitive_runtime else "recommended",
            action="validate" if security_exists else "create",
            priority="P0" if sensitive_runtime else "P1",
            confidence="high",
            impact="high",
            effort="medium",
            risk="high" if sensitive_runtime else "medium",
            reason=(
                "The project contains server, authentication, or persistence signals; agent actions need explicit resource-level boundaries."
                if sensitive_runtime
                else "Even a development-only baseline should define secrets, prohibited operations, and escalation rules."
            ),
            evidence=(
                ([docs.get("security")] if security_exists else [])
                + list(signals.get("auth_dependencies", []))
                + list(signals.get("database_dependencies", []))
            ),
            unknowns=(
                ["Resource-level authorization, tenancy, and destructive-action policy are not proven by dependency detection."]
                if sensitive_runtime
                else []
            ),
            expected_artifacts=["Security section in AGENTS.md, or the existing SECURITY.md"],
            acceptance_criteria=[
                "Secrets and sensitive data handling are explicit.",
                "Read, write, destructive, and external-effect operations have separate rules.",
                "Runtime tools cannot bypass domain authorization.",
            ],
            grill_topics=["authz_model", "mutation_policy"] if sensitive_runtime and (args.authenticated_ui_actions or args.headless_actions) else [],
        )
    )

    recommendations.append(
        rec(
            id="agentic-evals-and-drift",
            title="Agentic evals and documentation drift detection",
            capability="evals and drift",
            layer="quality",
            applicability="conditional",
            action="investigate",
            priority="P2",
            confidence="medium",
            impact="medium",
            effort="medium",
            risk="low",
            reason=(
                "Readiness is shown by tasks agents complete, not file presence. Add an eval only for a repeated "
                "agent task whose failure is costly; reuse existing tests and checks first."
            ),
            evidence=[],
            expected_artifacts=["One behavior eval per repeated, costly agent task, if justified"],
            prerequisites=["Establish canonical sources and ownership metadata."],
            acceptance_criteria=["Each eval covers a real repeated task and names the failure it catches."],
            rejected_alternatives=["Build an eval suite or drift pipeline by default."],
        )
    )

    llms_existing = integration_paths(integrations, "llms_txt")
    public_web = bool(args.public_web or (is_web and has_public_content))
    if llms_existing:
        llms_app, llms_action, llms_priority = "recommended", "validate", "P2"
        llms_reason = "An llms.txt file exists and should be checked against intentionally public, current content."
    elif public_web:
        llms_app, llms_action, llms_priority = "recommended", "create", "P2"
        llms_reason = "The project appears to publish stable web content that may benefit from a concise model-oriented index."
    else:
        llms_app, llms_action, llms_priority = "not-applicable", "skip", "P3"
        llms_reason = "No intentionally public stable content surface is established."
    recommendations.append(
        rec(
            id="llms-txt",
            title="Public model-readable content index",
            capability="llms.txt",
            layer="web-discovery",
            applicability=llms_app,
            action=llms_action,
            priority=llms_priority,
            confidence="medium",
            impact="medium",
            effort="low",
            risk="medium" if public_web else "low",
            reason=llms_reason,
            evidence=llms_existing,
            unknowns=["Which content and base URL are intentionally public?"] if public_web and not llms_existing else [],
            expected_artifacts=["public/llms.txt", "optional Markdown alternates"],
            acceptance_criteria=["Every link resolves and exposes only intentionally public content."],
            rejected_alternatives=["Treat llms.txt as access control or publish private documentation paths."],
            grill_topics=["public_scope"] if public_web and not llms_existing else [],
        )
    )

    openapi_existing = integration_paths(integrations, "openapi")
    if openapi_existing:
        openapi_app, openapi_action, openapi_reason = "recommended", "validate", "An OpenAPI contract exists and should be checked against live routes and authorization behavior."
    elif is_server:
        openapi_app, openapi_action, openapi_reason = "conditional", "investigate", "A server/API candidate exists, but the stable HTTP surface and intended consumers must be verified before generating a contract."
    else:
        openapi_app, openapi_action, openapi_reason = "not-applicable", "skip", "No stable HTTP API evidence was detected."
    recommendations.append(
        rec(
            id="openapi-contract",
            title="HTTP API contract",
            capability="OpenAPI and JSON Schema",
            layer="contract",
            applicability=openapi_app,
            action=openapi_action,
            priority="P2",
            confidence="high" if openapi_existing else "medium",
            impact="high" if is_server else "low",
            effort="medium",
            risk="medium",
            reason=openapi_reason,
            evidence=openapi_existing + list(inventory.get("api_route_paths", []))[:10],
            unknowns=["Which routes are stable and intended for machine consumption?"] if is_server and not openapi_existing else [],
            expected_artifacts=["openapi.yaml", "schemas/*.json"],
            acceptance_criteria=["Contract validation passes and representative requests match implementation."],
            grill_topics=["api_contract_scope"] if is_server and not openapi_existing else [],
        )
    )

    arazzo_existing = integration_paths(integrations, "arazzo")
    if arazzo_existing:
        arazzo_app, arazzo_action, arazzo_reason = "recommended", "validate", "An Arazzo workflow document exists and should be validated against the referenced OpenAPI operations."
    elif openapi_existing:
        arazzo_app, arazzo_action, arazzo_reason = "conditional", "investigate", "Arazzo is useful only if agents must execute important multi-step API workflows."
    else:
        arazzo_app, arazzo_action, arazzo_reason = "not-applicable", "skip", "No validated OpenAPI foundation or multi-step API workflow is established."
    recommendations.append(
        rec(
            id="arazzo-workflows",
            title="Multi-step API workflow contracts",
            capability="Arazzo",
            layer="contract",
            applicability=arazzo_app,
            action=arazzo_action,
            priority="P3",
            confidence="medium",
            impact="medium",
            effort="medium",
            risk="low",
            reason=arazzo_reason,
            evidence=arazzo_existing,
            unknowns=["Which cross-operation workflows are stable and high value?"] if arazzo_app == "conditional" else [],
            expected_artifacts=["arazzo.yaml"],
            acceptance_criteria=["Every referenced operation and workflow transition validates."],
            grill_topics=["api_workflows"] if arazzo_app == "conditional" else [],
        )
    )

    asyncapi_existing = integration_paths(integrations, "asyncapi")
    if asyncapi_existing:
        asyncapi_app, asyncapi_action, asyncapi_reason = "recommended", "validate", "An AsyncAPI contract exists and should be checked against real channels and payloads."
    elif has_events:
        asyncapi_app, asyncapi_action, asyncapi_reason = "conditional", "investigate", "Event or queue dependencies exist; a contract is valuable only for stable inter-service channels."
    else:
        asyncapi_app, asyncapi_action, asyncapi_reason = "not-applicable", "skip", "No stable event-driven interface was detected."
    recommendations.append(
        rec(
            id="asyncapi-contract",
            title="Event and messaging contracts",
            capability="AsyncAPI",
            layer="contract",
            applicability=asyncapi_app,
            action=asyncapi_action,
            priority="P3",
            confidence="high" if asyncapi_existing else "medium",
            impact="medium",
            effort="medium",
            risk="medium",
            reason=asyncapi_reason,
            evidence=asyncapi_existing + list(signals.get("event_dependencies", [])),
            unknowns=["Which channels are contractual rather than internal implementation details?"] if asyncapi_app == "conditional" else [],
            expected_artifacts=["asyncapi.yaml"],
            acceptance_criteria=["Channel, message, and payload schemas match representative events."],
            grill_topics=["event_contract_scope"] if asyncapi_app == "conditional" else [],
        )
    )

    webmcp_existing = integration_paths(integrations, "webmcp_code_mentions")
    webmcp_requested = bool(args.authenticated_ui_actions)
    if webmcp_existing:
        webmcp_app, webmcp_action = "recommended", "validate"
        webmcp_reason = "WebMCP-like registration code exists and needs feature detection, authorization, fallback, and negative tests."
    elif is_web and webmcp_requested:
        webmcp_app = "conditional" if args.experimental == "allow" else "report-only"
        webmcp_action = "investigate"
        webmcp_reason = "Page-local signed-in actions are requested, but the browser surface must remain optional and backed by existing domain authorization."
    else:
        webmcp_app, webmcp_action = "not-applicable", "skip"
        webmcp_reason = "No requirement for agent actions tied to an open browser page was established."
    webmcp_topics: list[str] = []
    if webmcp_requested or webmcp_existing:
        webmcp_topics.extend(["page_vs_headless", "runtime_consumers", "authz_model"])
        if args.experimental != "allow":
            webmcp_topics.append("experimental_fallback")
        if sensitive_runtime:
            webmcp_topics.append("mutation_policy")
    recommendations.append(
        rec(
            id="webmcp",
            title="Page-local agent actions",
            capability="WebMCP",
            layer="runtime",
            applicability=webmcp_app,
            action=webmcp_action,
            priority="P3",
            confidence="medium",
            impact="medium",
            effort="high",
            risk="high" if sensitive_runtime else "medium",
            reason=webmcp_reason,
            evidence=webmcp_existing,
            unknowns=(
                ["Caller, page/session dependency, authorization, mutations, and fallback behavior must be explicit."]
                if webmcp_topics
                else []
            ),
            expected_artifacts=["src/agent-tools/webmcp/*", "feature detection", "human UI fallback", "negative tests"],
            prerequisites=["Reuse existing authenticated domain actions; do not duplicate business logic."],
            acceptance_criteria=[
                "Unsupported clients retain full human functionality.",
                "Every tool enforces resource-level authorization server-side.",
            ],
            rejected_alternatives=["Use WebMCP for actions that must work without the page open."],
            grill_topics=webmcp_topics,
        )
    )

    mcp_existing = integration_paths(integrations, "mcp_dependencies")
    mcp_requested = bool(args.headless_actions)
    if mcp_existing:
        mcp_app, mcp_action = "recommended", "validate"
        mcp_reason = "MCP dependencies exist and the server/tool boundary should be validated for narrow domain capabilities and least privilege."
    elif mcp_requested:
        mcp_app, mcp_action = "conditional", "investigate"
        mcp_reason = "Page-independent agent actions are requested; MCP is applicable only after callers, transport, authorization, and tool scope are defined."
    else:
        mcp_app, mcp_action = "not-applicable", "skip"
        mcp_reason = "No page-independent tool or resource requirement was established."
    mcp_topics: list[str] = []
    if mcp_existing or mcp_requested:
        mcp_topics.extend(["runtime_consumers", "transport_deployment", "authz_model"])
        if sensitive_runtime:
            mcp_topics.append("mutation_policy")
    recommendations.append(
        rec(
            id="mcp-server",
            title="Headless agent tools and resources",
            capability="MCP",
            layer="runtime",
            applicability=mcp_app,
            action=mcp_action,
            priority="P2",
            confidence="high" if mcp_existing else "medium",
            impact="high",
            effort="high",
            risk="high" if sensitive_runtime else "medium",
            reason=mcp_reason,
            evidence=mcp_existing,
            unknowns=["Caller, transport, authorization unit, and mutating tool policy are unresolved."] if mcp_topics else [],
            expected_artifacts=["src/agent-tools/mcp/*", "tool schemas", "auth policy", "functional and negative tests"],
            prerequisites=["Define narrow domain actions and reuse application authorization."],
            acceptance_criteria=[
                "No tool exposes arbitrary shell, SQL, filesystem, or network access.",
                "Read and write tools are separated and auditable.",
            ],
            rejected_alternatives=["Expose a generic execute-command or execute-SQL tool."],
            grill_topics=mcp_topics,
        )
    )

    mcp_applicable = mcp_app in ACTIVE and mcp_app != "not-applicable"
    if mcp_applicable and args.visual_tool_results:
        mcp_apps_app, mcp_apps_action, mcp_apps_reason = "conditional", "investigate", "Some MCP results are explicitly visual or editable; an app surface may improve usability."
    else:
        mcp_apps_app, mcp_apps_action, mcp_apps_reason = "not-applicable", "skip", "No MCP result has been shown to require an interactive visual surface."
    recommendations.append(
        rec(
            id="mcp-apps",
            title="Interactive UI for MCP results",
            capability="MCP Apps",
            layer="runtime",
            applicability=mcp_apps_app,
            action=mcp_apps_action,
            priority="P3",
            confidence="medium",
            impact="medium",
            effort="high",
            risk="medium",
            reason=mcp_apps_reason,
            evidence=[],
            unknowns=["Which result genuinely needs a map, table, editor, preview, or approval UI?"] if mcp_apps_app == "conditional" else [],
            expected_artifacts=["MCP UI resource and host-compatible fallback"],
            prerequisites=["A validated MCP tool and a concrete visual interaction need."],
            acceptance_criteria=["The UI adds material value over structured text and preserves non-UI fallback."],
            grill_topics=["visual_tool_need"] if mcp_apps_app == "conditional" else [],
        )
    )

    a2a_existing = integration_paths(integrations, "a2a_agent_card")
    a2a_requested = bool(args.agent_service)
    if a2a_existing:
        a2a_app, a2a_action = "recommended", "validate"
        a2a_reason = "An Agent Card exists and should be validated against the actual delegated task lifecycle."
    elif a2a_requested:
        a2a_app, a2a_action = "conditional", "investigate"
        a2a_reason = "The product is intended to operate as an independent agent, but task state, cancellation, artifacts, and trust boundaries must be designed."
    else:
        a2a_app, a2a_action = "not-applicable", "skip"
        a2a_reason = "The project has not been identified as an independent task-managing agent."
    recommendations.append(
        rec(
            id="a2a-agent",
            title="Agent-to-agent task interface",
            capability="A2A",
            layer="interoperability",
            applicability=a2a_app,
            action=a2a_action,
            priority="P3",
            confidence="high" if a2a_existing else "medium",
            impact="high",
            effort="high",
            risk="high",
            reason=a2a_reason,
            evidence=a2a_existing,
            unknowns=["Task lifecycle, caller identity, cancellation, progress, artifacts, and authorization are unresolved."] if a2a_requested or a2a_existing else [],
            expected_artifacts=["public/.well-known/agent-card.json", "task lifecycle implementation", "security tests"],
            prerequisites=["The product must be an agent, not merely an API or tool collection."],
            acceptance_criteria=["Task state transitions, cancellation, retry, and artifact delivery are tested."],
            rejected_alternatives=["Present a normal API as an autonomous agent without a task lifecycle."],
            grill_topics=["agent_task_lifecycle", "runtime_consumers", "authz_model"] if a2a_requested or a2a_existing else [],
        )
    )

    ard_existing = integration_paths(integrations, "ard_catalog")
    ard_requested = bool(args.public_discovery)
    if ard_existing:
        ard_app, ard_action = "recommended", "validate"
        ard_reason = "A public agentic resource catalog exists and should be checked for current resources, identity, and trust metadata."
    elif ard_requested:
        ard_app = "conditional" if args.experimental == "allow" else "report-only"
        ard_action = "investigate"
        ard_reason = "Multiple public agentic resources need discovery, but the catalog should remain optional and version-verified."
    else:
        ard_app, ard_action = "not-applicable", "skip"
        ard_reason = "No need for public discovery across multiple agentic resources was established."
    recommendations.append(
        rec(
            id="ard-catalog",
            title="Public agentic resource discovery",
            capability="ARD",
            layer="interoperability",
            applicability=ard_app,
            action=ard_action,
            priority="P3",
            confidence="medium",
            impact="medium",
            effort="medium",
            risk="medium",
            reason=ard_reason,
            evidence=ard_existing,
            unknowns=["Which resources are intentionally public and what identity/trust metadata is authoritative?"] if ard_requested else [],
            expected_artifacts=["public/.well-known/ai-catalog.json"],
            prerequisites=["At least two stable public agentic resources and a maintained publication policy."],
            acceptance_criteria=["Every catalog entry resolves and contains intentionally public metadata."],
            grill_topics=["discovery_scope", "experimental_fallback"] if ard_requested and not ard_existing else [],
        )
    )

    counts = Counter(item["applicability"] for item in recommendations)
    highest_priority = [
        item["id"]
        for item in recommendations
        if item["priority"] in {"P0", "P1"} and item["applicability"] in ACTIVE
    ]
    safe_to_proceed = [
        item["id"]
        for item in recommendations
        if item["layer"] not in {"runtime", "interoperability"}
        and item["applicability"] in {"required", "recommended"}
        and not item["grill_topics"]
        and not (item["risk"] in {"critical", "high"} and item["unknowns"])
    ]
    blocked = [item["id"] for item in recommendations if item["applicability"] == "blocked"]

    result = {
        "schema_version": 1,
        "generator": GENERATOR,
        "source_audit": str(audit_path),
        "phase": "preliminary",
        "policy": {
            "experimental": args.experimental,
            "explicit_target_vendors": explicit_vendors,
            "runtime_intent": {
                "authenticated_ui_actions": args.authenticated_ui_actions,
                "headless_actions": args.headless_actions,
                "visual_tool_results": args.visual_tool_results,
                "agent_service": args.agent_service,
                "public_discovery": args.public_discovery,
                "sensitive_actions": args.sensitive_actions,
            },
        },
        "summary": {
            "counts": dict(sorted(counts.items())),
            "highest_priority": highest_priority,
            "safe_to_proceed": safe_to_proceed,
            "blocked": blocked,
        },
        "recommendations": recommendations,
        "note": "Preliminary recommendations are evidence-backed but must be recomputed after any material Grill Session answers.",
    }

    text = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
