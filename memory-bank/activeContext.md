## Handoff Report: Crypto Technical Analysis Multi-Agent System (Pivoting to MCP Strategy)

**Date of Handoff:** 2025-05-31
**Project Version (Memory Bank):** `activeContext.md` (this report, v0.20), `progress.md` (v0.18, will be updated next).
**Previous Handoff:** Report dated 2025-05-31 (v0.19, detailing agent refactoring for image URL consumption).

**1. Current Work & Overall Mission:**
*   **Mission:** Build a multi-agent system for cryptocurrency technical analysis using Google ADK (Python), FastAPI, and React/CopilotKit.
*   **Current Stage:** Debugging initial ADK agent execution flow, specifically the `OrchestratorAgent` calling `ContextAgent`, and its internal tool calls. Pivoting to discuss MCP server integration strategy before further debugging.
*   **Work Done This Session (Continuing from v0.19):**
    *   **ADK Session Management Resolved:**
        *   Iteratively debugged and fixed session errors in `backend/main.py`.
        *   Confirmed `Runner.run_async()` requires `user_id` and `session_id` as keyword-only arguments.
        *   Discovered (with user's research) that `InMemorySessionService.create_session()` is `async` and requires `app_name`, `user_id`, and `session_id` as keyword arguments in this ADK version.
        *   Successfully patched `adk_orchestrator_action_handler` to `await session_service.create_session(...)` with all required arguments, resolving previous "Session not found" errors and `RuntimeWarning`s.
    *   **Encountered Gemini API Error (Post-Session Fix):**
        *   Once session issues were resolved, a `google.genai.errors.ClientError: 400 INVALID_ARGUMENT` ("Function calling with a response mime type: 'application/json' is unsupported") occurred. This happened when the `OrchestratorAgent` (LLM) attempted to call the `ContextAgent` (as a tool), likely due to `ContextAgent`'s `output_schema` implying a JSON response.
    *   **Attempted Workaround for Gemini API Error:**
        *   Modified `backend/agents/context_agent.py` by removing `output_schema` from `ContextAgent` to avoid the `application/json` MIME type declaration for the tool's response.
    *   **Encountered `ContextAgent` Internal Tool Calling Error:**
        *   After removing `output_schema`, the `ContextAgent` (when called by `OrchestratorAgent`) failed internally with `ValueError: Function _simulated_mcp_get_price is not found in the tools_dict.`. This indicated that the `ContextAgent`'s LLM was attempting to call its internal price-fetching tool using the Python function's actual name (`_simulated_mcp_get_price`) instead of its declared tool name.
    *   **Last Action (Before Pivot):**
        *   Updated `backend/agents/context_agent.py` to rename the internal tool to `fetch_current_price` and modified its prompt to use this new name, in an attempt to resolve the internal tool calling error. (The direct outcome of this very last change was not fully tested before deciding to pivot).

**2. Key Technical Concepts & Decisions (Updated):**
*   **ADK Session Management:** `InMemorySessionService.create_session()` is `async` and requires `app_name`, `user_id`, `session_id` (keyword arguments) in the current ADK version. `Runner.run_async()` also requires `user_id` and `session_id`. Pre-creating the session with `await` is crucial.
*   **Gemini API Function Calling Limitation:** The Gemini API (specifically observed with `gemini-2.5-flash-preview-05-20`) does not support function/tool calls that are declared with a response MIME type of `application/json`. This impacts ADK `LlmAgent`s that use `output_schema` when they are wrapped as `AgentTool`s.
*   **ADK `LlmAgent` Internal Tool Calling:** Potential issue where an `LlmAgent` (especially if `output_schema` is removed but it still has `FunctionTool`s) might have its LLM attempt to call internal tools by their Python function name rather than the explicitly set `FunctionTool.name`. This requires careful prompting and tool name definition.
*   **MCP Server Integration Strategy:** User has indicated existing MCP servers are STDIN/STDOUT based and wants to discuss a new integration strategy. This is the new priority.

**3. Relevant Files and Code (Current State - Major Updates):**
*   **HEAVILY MODIFIED THIS SESSION:**
    *   `backend/main.py` (Iterative fixes for ADK session handling in `adk_orchestrator_action_handler`).
*   **MODIFIED THIS SESSION:**
    *   `backend/agents/context_agent.py` (Removed `output_schema`; renamed internal tool to `fetch_current_price` and updated prompt).
*   **(Files from v0.19, no new changes this segment):**
    *   `backend/agents/momentum_agent.py`
    *   `backend/agents/derivatives_agent.py`
    *   `copilotkit-runtime-node/src/app/api/copilotkit/route.ts` (Verified, no changes)

**4. Problem Solving (Summary of this session):**
*   Successfully diagnosed and resolved complex ADK session management errors by correctly identifying `async` nature and required arguments for `InMemorySessionService.create_session` and `Runner.run_async`.
*   Identified a Gemini API limitation regarding JSON response MIME types for function calls.
*   Attempted a workaround for the Gemini API error by modifying `ContextAgent`.
*   Encountered and attempted to fix an issue with `ContextAgent`'s internal tool invocation.
*   Pivoted strategy to address MCP server integration before further debugging current agent tool-call issues.

**5. Pending Tasks and Next Steps (New Focus):**
1.  **Initiate New Chat/Task:** To discuss MCP server integration strategy. User has existing STDIN/STDOUT MCPs but wants to explore options for ADK integration.
2.  **In the New Chat - MCP Discussion Points:**
    *   Clarify how STDIN/STDOUT MCP servers are currently invoked.
    *   Discuss preferred methods for ADK agents to communicate with MCPs (e.g., wrapping STDIN/STDOUT calls, building thin HTTP wrappers for existing MCPs, or re-implementing MCP logic directly as Python tools/ADK agents if simpler).
    *   Define how ADK `FunctionTool`s within agents like `ContextAgent`, `NewsAgent`, `SentimentAgent` will call these (potentially new) MCP interfaces.
3.  **(Deferred) Resolve `ContextAgent` internal tool call:** If the `fetch_current_price` rename didn't fix it, this will need revisiting after MCP strategy is clear.
4.  **(Deferred) Address Gemini API `application/json` error:** If removing `output_schema` isn't a viable long-term solution for all agents, explore other ADK configurations or architectural patterns.

**6. System Architecture Status:**
*   **✅ RESOLVED**: ADK Session Management in `backend/main.py`.
*   **⚠️ CURRENT BLOCKER (Execution Path):** `ContextAgent`'s internal tool (`fetch_current_price`) invocation was failing (LLM requesting `_simulated_mcp_get_price`). Last attempt was to rename tool and prompt.
*   **⚠️ KNOWN LIMITATION:** Gemini API's incompatibility with `application/json` response MIME type for function calls, impacting `LlmAgent`s with `output_schema` when used as tools.
*   **🔄 NEXT (Strategic Pivot):** Discuss and define MCP server integration strategy.

**7. Critical Files Modified This Session (v0.20):**
*   `backend/main.py`
*   `backend/agents/context_agent.py`

**8. Key Learnings for Future Development (This Session):**
*   **ADK `InMemorySessionService` (for v0.6.0+):** `create_session` and `get_session` are `async` methods. `create_session` requires `app_name`, `user_id`, and `session_id` as keyword-only arguments. Always `await` these calls.
*   **ADK `Runner.run_async`:** Requires `user_id` and `session_id` as keyword-only arguments in this ADK version.
*   **Gemini API Function Calling:** Be aware of limitations, such as the unsupported `application/json` response MIME type. This can affect how ADK agents with `output_schema` are used as tools.
*   **ADK `LlmAgent` Tool Naming:** LLMs might unexpectedly try to call internal tools by their Python function name (`func.__name__`) rather than the `FunctionTool(name="...")`. Ensure prompts are very clear and tool names are robust. If issues persist, aligning `FunctionTool.name` with `func.__name__` could be a fallback.
*   **Debugging Iteration:** Complex issues often require iterative changes and careful log analysis. User feedback and research are invaluable.
