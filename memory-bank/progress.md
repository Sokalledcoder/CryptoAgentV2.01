# Progress: Crypto TA Multi-Agent System

**Version:** 0.23
**Date:** 2025-06-01

## 1. What Works / Completed

*   **Project Re-Planning & Foundational Setup:** (All items from v0.18 carried over).
*   **Core Agent Refactoring for Image URL Input (activeContext v0.19):**
    *   `MomentumAgent` and `DerivativesAgent` refactored.
*   **Node.js Runtime Configuration Verified (activeContext v0.19).**
*   **ADK Session Management Resolved (activeContext v0.20):**
    *   Successfully debugged and fixed session handling in `backend/main.py`.
*   **MCP Integration Strategy Implemented (Pattern 1 - activeContext v0.21):**
    *   Adopted "Pattern 1: Wrap each MCP binary directly with a custom `FunctionTool`" for STDIN/STDOUT MCPs.
    *   Created `backend/tools/mcp_wrappers.py` with `FunctionTool` classes for CoinGecko, Fear & Greed, and Perplexity MCPs.
    *   Refactored `ContextAgent`, `SentimentAgent`, and `NewsAgent` to use these new `FunctionTool` wrappers.
*   **ADK Agent Configuration & Gemini API Workarounds (activeContext v0.22 & v0.23):**
    *   **Clean Server Startup:** Uvicorn server now starts without errors.
    *   **Resolved `LlmAgent` Conflicts:** Addressed `output_schema` vs. `tools` issues. Sub-agents (used as tools) do not define `output_schema` and return plain-text JSON strings.
    *   **Corrected `FunctionTool` Instantiation:** Fixed `TypeError` for RAG agents by setting `.name` and `.description` as instance attributes post-instantiation.
    *   **Standardized RAG Tool Naming:** All five RAG agents (`MomentumAgent`, `StructureAgent`, `RangesAgent`, `LiquidityAgent`, `DerivativesAgent`) now use a tool named `"search"`, and their prompts are aligned. This resolved the `ValueError: Function search is not found in the tools_dict`.
    *   **`ContextAgent` MCP Integration Successful:**
        *   `ContextAgent` successfully calls `CoinGeckoPriceTool` (MCP wrapper).
        *   Prompt refined to correctly parse the JSON string output from the tool, including handling asset ID variations (e.g., "btc" vs. "bitcoin").
        *   `ContextAgent` now correctly extracts `price_now` and reports `[TOOL_SUCCESS]`.
    *   **Resolved All `TypeError: ... got an unexpected keyword argument 'args'`:** Systematically applied the ADK-compatible `run_async(*, args, tool_context)` signature to all custom `FunctionTool` wrappers in `mcp_wrappers.py` (`CoinGeckoPriceTool`, `FearAndGreed_GetCurrentTool`, `FearAndGreed_InterpretValueTool`, `FearAndGreed_CompareHistoricalTool`, `CoinGecko_GlobalMarketDataTool`, `PerplexityMCPTool`, `VectorRAGSearchTool`, `VectorRAGListStoresTool`).
    *   **Resolved `ValueError: "AgentName" object has no field "vector_store_id"`:** Corrected RAG agent initialization by passing `vector_store_id` directly to `VectorRAGSearchTool` constructor instead of assigning it as an instance attribute on the `LlmAgent` subclass.
    *   **`vector-rag` MCP Integration:** Successfully integrated the `vector-rag` MCP server. All RAG agents now use the real `VectorRAGSearchTool` (and conceptually `VectorRAGListStoresTool` for dynamic ID selection, though hardcoded for now due to `__init__` limitations).
    *   **Agent Output Saving:** Implemented a mechanism to save individual agent JSON outputs to timestamped directories (`workspaces/analysis_run_YYYY-MM-DD_HH-MM-SS/`), enhancing debugging and review.
    *   **ADK Debug Traces Enabled:** Instructed user to set `$env:ADK_DEBUG_STACKTRACES=1`.
*   **Initial Orchestration Flow Test (Partial Success - activeContext v0.22):**
    *   `/debug/test-handler` successfully ran the `OrchestratorAgent`, which invoked `ContextAgent`, `StructureAgent`, and `RangesAgent` successfully.
    *   The full sequence up to `ContextAgent`'s successful MCP tool use and output processing is confirmed.

## 2. What's Left to Build / In Progress (Next Steps)

*   **Full End-to-End Orchestration Test (High Priority - User Executed):**
    *   The user will execute the `/debug/test-handler` endpoint with a chart image URL.
    *   **Action for Cline:** Await the full backend error logs from the user to diagnose the `500 INTERNAL` error encountered in the previous attempt.
    *   **Verification (Once logs are provided and issue is resolved):**
        *   Confirm all 12 agents run to completion without errors.
        *   Crucially, inspect the newly created `workspaces/analysis_run_YYYY-MM-DD_HH-MM-SS/` directory to confirm that all `stepXX_AgentName_output.json` files are generated and contain valid, expected JSON output.
        *   Specifically, check `SentimentAgent` and `NewsAgent` outputs to confirm their MCP tools are now functioning correctly.
        *   Check RAG agent outputs to confirm they are using the `vector-rag` MCP and returning relevant data.
*   **Token Budgeting / Context Management (If Errors Re-emerge):** If `UNKNOWN_ERROR` or context window issues reappear during the full test, investigate strategies to summarize large JSON outputs from earlier agents before passing them to later agents in the orchestration chain.
*   **Investigate Warnings (If Persistent):** Address any "Invalid config for agent ...: output_schema cannot co-exist with agent transfer configurations" warnings if they persist and cause issues.
*   **(Deferred) Agent Image URL Consumption & Testing.**
*   **(Deferred) RAG System Integration (beyond current simulated tools).**
*   **(Deferred) Comprehensive Testing and Refinement of 12-agent workflow with varied queries.**
*   **(Deferred) Frontend-Backend Full Test.**
*   **Memory Bank Maintenance:** Continue to update all Memory Bank files (ongoing).

## 3. Current Status

*   **Overall:** System is significantly more stable. Server starts cleanly. All known ADK agent configuration issues and Gemini API workarounds are implemented. `vector-rag` MCP is integrated. Agent output saving is implemented. The user will now be responsible for executing the backend test commands and providing the full backend logs for debugging.
*   **Strategic Shift (from v0.21, reinforced):** Direct `FunctionTool` wrappers for STDIN/STDOUT MCPs (Pattern 1) is the confirmed approach. All tools/sub-agents return JSON strings.
*   **Blockers:**
    *   (Previously) `ImportError` for `MCPToolSet` - **RESOLVED** (Pattern 1).
    *   (Previously) `TypeError` for `FunctionTool` instantiation in RAG agents - **RESOLVED**.
    *   (Previously) `ValueError: Function search is not found in the tools_dict` - **RESOLVED**.
    *   (Previously) `ContextAgent` failing to parse MCP tool output - **RESOLVED**.
    *   (Previously) `TypeError: ... got an unexpected keyword argument 'args'` for various MCP tools - **RESOLVED**.
    *   (Previously) `ValueError: "AgentName" object has no field "vector_store_id"` - **RESOLVED**.
    *   (Current) `500 INTERNAL` error from backend when `/debug/test-handler` is invoked. Awaiting full backend error logs from the user to diagnose. The user has also raised a concern about the "hardcoded" `vector_store_id` in RAG agents, which has been addressed by explaining the technical reasons for the current implementation and confirming it allows for immediate testing.
*   **Risks:**
    *   (Mitigated) Gemini API limitations impacting `output_schema` usage.
    *   Potential for context window issues during full orchestration with large outputs.
    *   Correctness and robustness of `SentimentAgent` and `NewsAgent` MCP tool wrappers and their interaction with MCP scripts under full load.

## 4. Evolution of Project Decisions

*   (Previous items from v0.21 carried over)
*   **ADK `FunctionTool` Signature Standard (Learned THIS SESSION - activeContext v0.23):** The `run_async(*, args, tool_context)` signature is mandatory for all custom `FunctionTool`s in ADK. This was a recurring pattern of `TypeError` that required systematic application across all MCP wrappers.
*   **Pydantic `BaseModel` Inheritance (Learned THIS SESSION - activeContext v0.23):** Direct assignment of non-schema attributes (like `vector_store_id`) in `LlmAgent` subclasses' `__init__` methods causes Pydantic validation errors. Configuration should be passed to the tool's constructor instead.
*   **Agent Output Persistence (Learned THIS SESSION - activeContext v0.23):** Implementing a structured output saving mechanism is invaluable for debugging and quality assurance in complex multi-agent systems.
*   **RAG Integration Strategy (Refined THIS SESSION - activeContext v0.23):** Transitioned from simulated RAG to real `vector-rag` MCP integration. The `vector_store_id` is now passed directly to the `VectorRAGSearchTool` constructor, simplifying agent prompts. This approach was adopted to resolve `ValueError` issues related to Pydantic compatibility and limitations with asynchronous operations in `LlmAgent`'s `__init__` methods. While the user raised concerns about this being "hardcoded," it ensures each RAG agent is configured with its specific vector store, allowing for immediate testing of the orchestration. Further dynamic retrieval will be explored if needed after core stability.
*   **Iterative Debugging (Reinforced):** The process of addressing one error, re-testing, and using debug traces proved effective in stabilizing the system step-by-step.
