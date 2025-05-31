## Handoff Report: Crypto Technical Analysis Multi-Agent System (MCP Integration - Pattern 1)

**Date of Handoff:** 2025-05-31
**Project Version (Memory Bank):** `activeContext.md` (this report, v0.21), `progress.md` (v0.19, will be updated next).
**Previous Handoff:** Report dated 2025-05-31 (v0.20, detailing ADK session fixes and initial MCP strategy pivot).

**1. Current Work & Overall Mission:**
*   **Mission:** Build a multi-agent system for cryptocurrency technical analysis using Google ADK (Python), FastAPI, and React/CopilotKit.
*   **Current Stage:** Implementing MCP (Model Context Protocol) server integration for ADK agents, following a user-provided guide. The previous focus was on resolving ADK session issues and initial Gemini API limitations.
*   **Work Done This Session (Continuing from v0.20):**
    *   **MCP Integration Strategy Adopted:** Based on user feedback and a provided guide, "Pattern 1: Wrap each MCP binary directly with a custom `FunctionTool`" was chosen. This approach uses `anyio.create_subprocess` (or wrappers around it) to run existing STDIN/STDOUT MCP scripts and returns their output as JSON strings to the LLM, bypassing Gemini's "application/json" MIME type error for tool responses.
    *   **Created `mcp_wrappers.py`:**
        *   A new file `backend/tools/mcp_wrappers.py` was created.
        *   It contains a helper function `_run_mcp` to execute STDIN/STDOUT processes (though `PerplexityMCPTool` uses a direct `anyio.create_subprocess` call to handle environment variable passing).
        *   Specific `FunctionTool` classes were implemented in this file:
            *   `CoinGeckoPriceTool`: Wraps CoinGecko's `get-price`.
            *   `FearAndGreed_GetCurrentTool`, `FearAndGreed_InterpretValueTool`, `FearAndGreed_CompareHistoricalTool`: Wrap corresponding Fear & Greed MCP tools.
            *   `CoinGecko_GlobalMarketDataTool`: Wraps CoinGecko's `global-market-data`.
            *   `PerplexityMCPTool`: A generic wrapper for Perplexity MCP tools, taking `tool_to_call` and `tool_args`, and handling `PERPLEXITY_API_KEY` via `env` in `anyio.create_subprocess`.
    *   **Refactored ADK Agents for MCP Integration (Pattern 1):**
        *   `backend/agents/context_agent.py`: Updated to use `CoinGeckoPriceTool`. Removed previous `MCPToolSet` (and simulated tool) logic. Prompt updated.
        *   `backend/agents/sentiment_agent.py`: Updated to use `FearAndGreed_GetCurrentTool`, `FearAndGreed_InterpretValueTool`, `FearAndGreed_CompareHistoricalTool`, and `CoinGecko_GlobalMarketDataTool`. Removed previous `MCPToolSet` logic. Prompt updated.
        *   `backend/agents/news_agent.py`: Updated to use `PerplexityMCPTool`. Removed previous `MCPToolSet` logic. Prompt updated.
    *   **Initial `ImportError` Debugging:** Investigated an `ImportError: cannot import name 'MCPToolSet'` which occurred when attempting to use ADK's built-in `MCPToolSet`. This involved checking ADK version (`1.1.1`), `mcp` library version (corrected from `1.9.2X` to `1.9.2`), and inspecting ADK/MCP library files. The persistence of this error, despite files appearing correct, contributed to adopting Pattern 1 from the user's guide as a more robust path forward for STDIN/STDOUT MCPs.

**2. Key Technical Concepts & Decisions (Updated):**
*   **MCP Integration Pattern 1:** ADK `FunctionTool`s wrap direct calls to STDIN/STDOUT MCP executables using `anyio.create_subprocess`. Tool outputs are returned as JSON strings to the LLM.
*   **Environment Variable Passing:** For `PerplexityMCPTool`, environment variables (`PERPLEXITY_API_KEY`, `PERPLEXITY_MODEL`) are passed to the subprocess via the `env` parameter of `anyio.create_subprocess`.
*   **Gemini API `application/json` Workaround:** By having `FunctionTool`s return strings, the direct Gemini error related to JSON MIME types for tool responses is avoided. The LLM is then prompted to parse this string.
*   **ADK `FunctionTool` Naming:** Prompts are updated to call the specific `name` of the registered `FunctionTool` wrapper.

**3. Relevant Files and Code (Current State - Major Updates This Session):**
*   **NEW FILE:**
    *   `backend/tools/mcp_wrappers.py`
*   **HEAVILY MODIFIED THIS SESSION:**
    *   `backend/agents/context_agent.py` (Switched from `MCPToolSet` attempt to Pattern 1 `FunctionTool` wrapper)
    *   `backend/agents/sentiment_agent.py` (Switched from `MCPToolSet` attempt to Pattern 1 `FunctionTool` wrappers)
    *   `backend/agents/news_agent.py` (Switched from `MCPToolSet` attempt to Pattern 1 `FunctionTool` wrapper)
*   **(Files from v0.20, no new changes this segment unless indirectly affected by imports):**
    *   `backend/main.py`

**4. Problem Solving (Summary of this session):**
*   Pivoted from attempting to use ADK's `MCPToolSet` (due to persistent `ImportError`) to implementing "Pattern 1" from user-provided documentation for STDIN/STDOUT MCP integration.
*   Successfully defined and implemented `FunctionTool` wrappers for CoinGecko, Fear & Greed, and Perplexity MCPs.
*   Refactored `ContextAgent`, `SentimentAgent`, and `NewsAgent` to utilize these new wrappers and updated their prompts accordingly.

**5. Pending Tasks and Next Steps (Focus for New Task/Session):**
1.  **Testing MCP Integration:**
    *   Thoroughly test the backend, ensuring `ContextAgent`, `SentimentAgent`, and `NewsAgent` can correctly execute their respective MCP tools via the new wrappers.
    *   Verify that environment variables (especially `PERPLEXITY_API_KEY`) are correctly passed and used.
    *   Monitor logs for any errors from `anyio.create_subprocess` or the MCP scripts themselves.
2.  **Resolve Original `ContextAgent` Issues (Deferred from v0.20):**
    *   The original `ValueError: Function _simulated_mcp_get_price is not found in the tools_dict` should now be resolved as `ContextAgent` uses the new `CoinGeckoPriceTool`. This needs verification.
3.  **Address Gemini API `application/json` for Agent-as-Tool (Deferred from v0.20):**
    *   If agents like `ContextAgent`, `SentimentAgent`, or `NewsAgent` (which now return JSON strings via their `output_schema` being effectively string-based due to LLM parsing the tool's string output) are themselves used as `AgentTool`s by the `OrchestratorAgent`, we need to ensure the `OrchestratorAgent`'s LLM is prompted to expect a JSON string and parse it, or we might still hit the Gemini limitation if an `output_schema` is re-introduced on these sub-agents. The user guide mentioned: "don’t declare `output_schema` on any agent you expose as a tool; instead ask the sub-agent to *write* JSON text in its prompt". This needs careful application.
4.  **Full Orchestration Flow Testing:** Once individual MCP calls are working, test the end-to-end `OrchestratorAgent` workflow.
5.  **Memory Bank Update & GitHub Commit:** (This is being done now).

**6. System Architecture Status:**
*   **✅ RESOLVED (Potentially):** `ImportError` for `MCPToolSet` by switching to Pattern 1.
*   **✅ IMPLEMENTED:** MCP integration for CoinGecko, Fear & Greed, Perplexity using custom `FunctionTool` wrappers for STDIN/STDOUT communication.
*   **🔄 NEXT (Testing):** Verify functionality of the new MCP integration.
*   **⚠️ KNOWN LIMITATION (Still relevant for Agent-as-Tool):** Gemini API's incompatibility with `application/json` response MIME type for function calls, if ADK `LlmAgent`s with `output_schema` are used as tools by other LLM-based agents.

**7. Critical Files Modified This Session (v0.21):**
*   `backend/tools/mcp_wrappers.py` (New)
*   `backend/agents/context_agent.py`
*   `backend/agents/sentiment_agent.py`
*   `backend/agents/news_agent.py`

**8. Key Learnings for Future Development (This Session):**
*   **Alternative MCP Integration:** When built-in library mechanisms (like `MCPToolSet`) prove problematic due to versioning or environment subtleties, direct wrapping of STDIN/STDOUT processes via `anyio.create_subprocess` within custom `FunctionTool`s is a viable and flexible alternative (Pattern 1).
*   **Environment Variables with `anyio`:** `anyio.create_subprocess` allows passing custom environment variables to child processes, crucial for tools requiring API keys.
*   **LLM Prompting for String Parsing:** When tools return JSON as a string (to bypass API limitations), the LLM must be explicitly prompted to parse this string.
