# Progress: Crypto TA Multi-Agent System

**Version:** 0.19
**Date:** 2025-05-31

## 1. What Works / Completed

*   **Project Re-Planning & Foundational Setup:** (All items from v0.18, sections 1-10, carried over as completed foundational work).
*   **Core Agent Refactoring for Image URL Input (activeContext v0.19):**
    *   `MomentumAgent` and `DerivativesAgent` refactored with detailed instruction prompts to parse and use image URLs from their input string.
*   **Node.js Runtime Configuration Verified (activeContext v0.19):**
    *   Confirmed `copilotkit-runtime-node/.../route.ts` correctly proxies actions.
*   **ADK Session Management Resolved (activeContext v0.20):**
    *   Successfully debugged and fixed session handling in `backend/main.py`.
    *   Confirmed `InMemorySessionService.create_session()` is `async` and requires `app_name`, `user_id`, `session_id`.
    *   Ensured `Runner.run_async()` is called with required `user_id` and `session_id`, and `create_session` is `await`ed. This resolved "Session not found" errors.
*   **Initial Agent Execution Flow (Partial Success - activeContext v0.20):**
    *   `OrchestratorAgent` now successfully starts and calls `ContextAgent` as its first tool.

## 2. What's Left to Build / In Progress (Next Steps)

*   **Strategic Pivot: MCP Server Integration Discussion (NEW PRIORITY):**
    *   **NEXT:** Initiate a new chat/task to discuss strategy for integrating existing STDIN/STDOUT MCP servers (CoinGecko, Fear & Greed, Perplexity) with ADK agents. Explore alternatives like HTTP wrappers or direct Python implementations if more suitable.
*   **(Deferred) Resolve Gemini API Error:**
    *   Investigate and fix `google.genai.errors.ClientError: 400 INVALID_ARGUMENT` ("Function calling with a response mime type: 'application/json' is unsupported"). This occurred when `OrchestratorAgent` called `ContextAgent` (after `output_schema` was initially present on `ContextAgent`).
    *   The workaround of removing `output_schema` from `ContextAgent` led to the next error.
*   **(Deferred) Resolve `ContextAgent` Internal Tool Call Error:**
    *   Investigate and fix `ValueError: Function _simulated_mcp_get_price is not found in the tools_dict.` This occurred within `ContextAgent` after its `output_schema` was removed.
    *   Last attempt involved renaming the tool to `fetch_current_price` in `ContextAgent` and its prompt. The outcome of this specific fix was not fully tested due to the pivot.
*   **(Deferred) Agent Image URL Consumption & Testing:**
    *   Once underlying API and tool-calling issues are resolved, conduct end-to-end testing of image processing flow.
*   **(Deferred) RAG System Integration.**
*   **(Deferred) Comprehensive Testing and Refinement of 12-agent workflow.**
*   **(Deferred) Further MCP Integration (pending strategy discussion).**
*   **(Deferred) Frontend-Backend Full Test (pending fixes).**
*   **Memory Bank Maintenance:** Continue to update all Memory Bank files.

## 3. Current Status

*   **Overall:** ADK session management in the FastAPI backend is now stable. The `OrchestratorAgent` can start and attempt to call its first sub-agent (`ContextAgent`). However, execution is blocked by errors related to Gemini API function calling (response MIME type) and subsequent errors in the `ContextAgent`'s internal tool invocation.
*   **Strategic Shift:** Prioritizing discussion on MCP server integration strategy before further debugging the current agent execution path.
*   **Blockers:**
    *   (Previously) ADK Session errors - **RESOLVED**.
    *   (Current - Deferred) Gemini API `application/json` response MIME type error.
    *   (Current - Deferred) `ContextAgent` internal tool call error.
*   **Risks:**
    *   Gemini API limitations impacting ADK `output_schema` usage with `AgentTool`.
    *   Complexity of ADK `LlmAgent` internal tool naming and invocation.
    *   Defining a robust and maintainable strategy for integrating STDIN/STDOUT MCP servers.

## 4. Evolution of Project Decisions

*   (Previous items from v0.18 carried over)
*   **ADK Session Management (Learned THIS SESSION - activeContext v0.20):**
    *   `InMemorySessionService.create_session` is `async` and requires keyword arguments: `app_name`, `user_id`, `session_id`. Must be `await`ed.
    *   `Runner.run_async` requires `user_id` and `session_id` as keyword-only arguments in the current ADK version.
*   **Gemini API Limitations (Identified THIS SESSION - activeContext v0.20):**
    *   The API error "Function calling with a response mime type: 'application/json' is unsupported" is a significant constraint when using ADK `LlmAgent`s with `output_schema` as tools for other agents.
*   **ADK Agent Tool Naming/Invocation (Observed THIS SESSION - activeContext v0.20):**
    *   `LlmAgent`s may attempt to call internal tools by their Python function name (`func.__name__`) rather than the `FunctionTool.name` if `output_schema` is removed or other misconfigurations occur. This requires careful tool definition and prompting.
*   **Strategic Pivot (THIS SESSION - activeContext v0.20):**
    *   Decision to pause current agent execution debugging and prioritize a discussion in a new chat/task about the integration strategy for the existing STDIN/STDOUT-based MCP servers. This is due to context window limits and the need for a clear path forward on external tool usage.
