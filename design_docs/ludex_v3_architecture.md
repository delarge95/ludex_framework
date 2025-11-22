# 🏗️ LUDEX v3.0 Architecture Evolution (v2.2 Integration)

**Version**: 3.1.0 (Draft)
**Date**: 2025-11-21
**Based on**: ARA v2.2 Specifications

## 🎯 Objective
Integrate advanced architectural concepts from ARA v2.2 into the LUDEX framework to enhance **User Interaction**, **Risk Analysis**, and **System Robustness**, without sacrificing the simplicity of the current LangGraph implementation.

---

## 1. Interactive Router (The "Director")
*Adapted from v2.2 AdaptiveRouter*

Instead of a purely automated router, we will implement a **Human-in-the-Loop (HITL)** router.

### Concept
The `Director` node is the entry point. It analyzes the user's request and:
1.  **Clarifies**: If the request is vague, it asks questions back to the user (requires frontend support for "Question" state).
2.  **Routes**: Decides the "Production Mode":
    *   **Quick Prototype**: Fast, low-cost, minimal agents (Market -> GDD).
    *   **Full Production**: All agents, deep research.
    *   **Specific Module**: Run only "Mechanics" or "Market Analysis".

### Implementation
- **LangGraph**: Add a conditional edge after `Director` that can return to `User` for input.
- **Frontend**: Update UI to handle `awaiting_input` state from backend.

---

## 2. Advanced Risk Engine (Statistical Analysis)
*Adapted from v2.2 Chaos Engineering & Risk Management*

Enhance the `Producer` agent to move beyond static estimates to **Probabilistic Forecasting**.

### Features
- **Monte Carlo Simulation**: Run 1000 iterations of budget/timeline scenarios based on complexity variables.
- **Output**:
    - "80% confidence project finishes in < 8 months"
    - "Risk of Budget Overrun: 45% (High)"
- **Visualization**: Present these stats in the GDD (ASCII charts or structured JSON for frontend charts).

---

## 3. Interactive Gates (Governance)
*Adapted from v2.2 GateOrchestrator*

Implement explicit **Approval Gates** between major phases.

### Workflow
1.  **Market Analyst** finishes.
2.  **System Pauses**: "Market Analysis Complete. Proceed to Mechanics?"
3.  **User Action**: Approve, Reject (Retry), or Edit.
4.  **Resume**: System continues.

### Implementation
- **LangGraph**: Use `interrupt_before` or explicit `approval_node`.

---

## 4. Telemetry & Observability
*Adapted from v2.2 Telemetry Engine*

- **Structured Logging**: Implement `structlog` for consistent JSON logs.
- **Metrics**: Track "Token Usage", "Agent Latency", and "User Feedback Score".

---

## 📅 Implementation Plan (Sprint 5)

1.  **Design**: Finalize `Director` prompt and LangGraph flow.
2.  **Backend**: Implement `Director` node and Risk Engine logic in `Producer`.
3.  **Frontend**: Add support for "System Questions" and "Approval Buttons".
4.  **Verify**: Test the interactive flow manually.
