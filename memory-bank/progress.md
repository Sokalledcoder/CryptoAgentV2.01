# Progress: Crypto TA Multi-Agent System

**Version:** 0.20
**Date:** 2025-05-31

## 1. What Works / Completed

*   **Project Re-Planning & Foundational Setup:** (All items from v0.18 carried over).
*   **Core Agent Refactoring for Image URL Input (activeContext v0.19):**
    *   `MomentumAgent` and `DerivativesAgent` refactored.
*   **Node.js Runtime Configuration Verified (activeContext v0.19).**
*   **ADK Session Management Resolved (activeContext v0.20):**
    *   Successfully debugged and fixed session handling in `backend/main.py`.
*   **Initial Agent Execution Flow (Partial Success - activeContext v0.20):**
    *   `OrchestratorAgent` starts and calls `ContextAgent`.
*   **MCP Integration Strategy Implemented (Pattern 1 - activeContext v0.21):**
    *   Adopted "Pattern 1: Wrap each MCP binary directly with a custom `FunctionTool`" for STDIN/STDOUT MCPs.
    *   Created `backend/tools/mcp_wrappers.py` with `FunctionTool` classes for CoinGecko, Fear & Greed, and Perplexity MCPs. These wrappers use `anyio.create_subprocess` for execution.
    *   Refactored `ContextAgent`, `SentimentAgent`, and `NewsAgent` to use these new `FunctionTool` wrappers, removing the problematic `MCPToolSet` approach.
    *   Updated prompts in these agents to call the new wrapper tool names.
    *   `PerplexityMCPTool` wrapper handles passing `PERPLEXITY_API_KEY` via environment variables to the subprocess.

## 2. What's Left to Build / In Progress (Next Steps)

*   **Testing New MCP Integration (NEW PRIORITY):**
    *   Verify that `ContextAgent`, `SentimentAgent`, and `NewsAgent` can successfully execute their respective MCP tools via the new `FunctionTool` wrappers in `mcp_wrappers.py`.
    *   Ensure environment variables (especially `PERPLEXITY_API_KEY`) are correctly passed and utilized.
    *   Monitor logs for errors from `anyio.create_subprocess` or the MCP scripts.
*   **(Deferred) Resolve Gemini API `application/json` Error (activeContext v0.20 & v0.21):**
    *   This remains a concern if agents like `ContextAgent`, `SentimentAgent`, or `NewsAgent` are used as `AgentTool`s by other LLM-based agents and have an `output_schema`. The current workaround (Pattern 1 tools returning strings, LLM parsing them) helps for *tool usage within* these agents. The user's guide suggests: "don’t declare `output_schema` on any agent you expose as a tool; instead ask the sub-agent to *write* JSON text in its prompt".
*   **(Potentially Resolved by Pattern 1) `ContextAgent` Internal Tool Call Error (activeContext v0.20):**
    *   The original `ValueError: Function _simulated_mcp_get_price is not found in the tools_dict.` should be resolved as `ContextAgent` now uses `CoinGeckoPriceTool`. This needs testing.
*   **(Deferred) Agent Image URL Consumption & Testing (activeContext v0.19).**
*   **(Deferred) RAG System Integration.**
*   **(Deferred) Comprehensive Testing and Refinement of 12-agent workflow.**
*   **(Deferred) Frontend-Backend Full Test.**
*   **Memory Bank Maintenance:** Continue to update all Memory Bank files (ongoing).

## 3. Current Status

*   **Overall:** ADK session management is stable. A new MCP integration strategy (Pattern 1) has been implemented for `ContextAgent`, `SentimentAgent`, and `NewsAgent`, replacing the problematic `MCPToolSet` approach. These agents now use custom `FunctionTool` wrappers to call STDIN/STDOUT MCPs.
*   **Strategic Shift:** Successfully pivoted from `MCPToolSet` to direct `FunctionTool` wrappers for STDIN/STDOUT MCPs.
*   **Blockers:**
    *   (Previously) `ImportError` for `MCPToolSet` - **WORKAROUND IMPLEMENTED** (Pattern 1).
    *   (Next) Potential runtime issues with the new MCP wrapper integrations need to be tested.
*   **Risks:**
    *   Gemini API limitations impacting `output_schema` usage when an agent itself is used as an `AgentTool`.
    *   Correctness and robustness of the new `FunctionTool` wrappers and their interaction with the STDIN/STDOUT MCP scripts.
    *   Ensuring LLM prompts correctly guide the use of the new wrapper tools and parsing of their string (JSON text) outputs.

## 4. Evolution of Project Decisions

*   (Previous items from v0.19 carried over)
*   **MCP Integration Strategy (Learned THIS SESSION - activeContext v0.21):**
    *   Pivoted from ADK's `MCPToolSet` due to persistent `ImportError`s.
    *   Adopted "Pattern 1" from user guide: Custom ADK `FunctionTool`s that wrap STDIN/STDOUT MCP executables using `anyio.create_subprocess`. This returns JSON as a string to the LLM, bypassing Gemini's `application/json` MIME type error for tool responses.
    *   `PerplexityMCPTool` wrapper specifically handles passing environment variables to its subprocess.
*   **ADK Version & Dependencies (Learned THIS SESSION - activeContext v0.21):**
    *   Confirmed `google-adk` is v1.1.1.
    *   Corrected `mcp` library from `v1.9.2X` to `v1.9.2`. However, `ImportError` for `MCPToolSet` persisted, leading to the strategy change.
