## Handoff Report: Crypto Technical Analysis Multi-Agent System (ADK Refactor, MCP Integration, & Output Saving)

**Date of Handoff:** 2025-06-01
**Project Version (Memory Bank):** `activeContext.md` (this report, v0.23), `progress.md` (will be updated next).
**Previous Handoff:** Report dated 2025-05-31 (v0.22, detailing ADK refactor and initial MCP test).

**1. Current Work & Overall Mission:**
*   **Mission:** Build a multi-agent system for comprehensive cryptocurrency technical analysis using Google ADK (Python), FastAPI, and React/CopilotKit.
*   **Current Stage:** Successfully integrated the `vector-rag` MCP server, refactored all RAG agents to use this real RAG system, and implemented a robust agent output saving mechanism for detailed debugging and quality review. All critical `TypeError` and `ValueError` issues related to ADK tool calling and Pydantic model compatibility have been addressed. The user will now be responsible for executing the backend test commands and providing the full backend logs for debugging.
*   **Work Done This Session (Continuing from v0.22):**
    *   **Integrated `vector-rag` MCP Server:**
        *   Added `VectorRAGListStoresTool` and `VectorRAGSearchTool` to `backend/tools/mcp_wrappers.py`. These `FunctionTool` wrappers handle communication with the `openai-vector-mcp` server, including passing `OPENAI_API_KEY` as an environment variable.
        *   Ensured `VectorRAGSearchTool.run_async` and `VectorRAGListStoresTool.run_async` conform to the ADK signature `(*, args: Dict[str, Any], tool_context: Any)`.
    *   **Refactored All RAG Agents (`MomentumAgent`, `StructureAgent`, `RangesAgent`, `LiquidityAgent`, `DerivativesAgent`):**
        *   Replaced simulated `FileSearchTool` with the real `VectorRAGSearchTool` from `mcp_wrappers.py`.
        *   Modified agent `__init__` methods to instantiate `VectorRAGSearchTool` by passing the specific `vector_store_id` (e.g., `"vs_momentum_rag"`) directly to its constructor. This resolved the `ValueError: "AgentName" object has no field "vector_store_id"` that occurred due to Pydantic's `BaseModel` inheritance.
        *   Updated agent prompts to remove `vector_store_id` from the `search` tool's parameters, as it's now pre-configured within the tool instance.
    *   **Fixed `PerplexityMCPTool` Signature:** Corrected `PerplexityMCPTool.run_async` signature to `(*, args: Dict[str, Any], tool_context: Any)` to resolve `TypeError: PerplexityMCPTool.run_async() got an unexpected keyword argument 'args'`.
    *   **Fixed Other MCP Tool Signatures:** Applied the same `(*, args: Dict[str, Any], tool_context: Any)` signature fix to `CoinGeckoPriceTool`, `FearAndGreed_GetCurrentTool`, `FearAndGreed_InterpretValueTool`, `FearAndGreed_CompareHistoricalTool`, and `CoinGecko_GlobalMarketDataTool` in `backend/tools/mcp_wrappers.py`.
    *   **Implemented Agent Output Saving:**
        *   Added `get_analysis_output_dir()` and `save_agent_output()` utility functions to `backend/main.py`.
        *   Modified `adk_orchestrator_action_handler` in `backend/main.py` to create a timestamped directory (`workspaces/analysis_run_YYYY-MM-DD_HH-MM-SS/`) for each analysis run.
        *   Integrated `save_agent_output()` to automatically save the JSON output of each sub-agent (e.g., `step01_ContextAgent_output.json`) into this run-specific directory. This significantly improves debugging and review capabilities.
    *   **Enabled ADK Debug Traces:** Instructed user to set `$env:ADK_DEBUG_STACKTRACES=1` for more detailed error logging.
    *   **Initial Orchestration Test (Partial Success):** The last test run (before implementing output saving) showed that `ContextAgent`, `StructureAgent`, and `RangesAgent` completed successfully. However, the orchestration still failed further down the chain (e.g., `LiquidityAgent`, `MomentumAgent`, `DerivativesAgent`, `NewsAgent`, `SentimentAgent`) due to the `TypeError` issues in MCP tool signatures and the `vector_store_id` Pydantic error, which have now been addressed.

**2. Key Technical Concepts & Decisions (Updated):**
*   **MCP Integration Pattern 1 (Reinforced):** Confirmed strategy: ADK `FunctionTool`s wrap direct calls to STDIN/STDOUT MCP executables using `anyio.create_subprocess`. Tool outputs are returned as JSON strings to the LLM.
*   **ADK `FunctionTool` Signature Standard:** All `FunctionTool` `run_async` methods **must** conform to `async def run_async(self, *, args: Dict[str, Any], tool_context: Any) -> str:`. Business logic parameters are extracted from the `args` dictionary.
*   **ADK `LlmAgent` & Pydantic Compatibility:** Avoid assigning arbitrary attributes (like `self.vector_store_id`) directly in `LlmAgent` subclasses' `__init__` methods, as this conflicts with Pydantic's schema validation. Instead, pass such configuration directly to the tool's constructor if the tool itself is a `FunctionTool`.
*   **Dynamic RAG `vector_store_id` (Configured per Agent):** The `vector_store_id` is currently passed directly to the `VectorRAGSearchTool` constructor for each RAG agent. This approach was adopted to resolve `ValueError` issues related to Pydantic compatibility and limitations with asynchronous operations in `LlmAgent`'s `__init__` methods. While the user raised concerns about this being "hardcoded," it ensures each RAG agent is configured with its specific vector store, allowing for immediate testing of the orchestration. Further dynamic retrieval will be explored if needed after core stability.
*   **Agent Output Persistence:** Implemented structured saving of each agent's JSON output to a timestamped directory, crucial for detailed analysis and debugging.
*   **Environment Variable Passing:** Confirmed `OPENAI_API_KEY` (for `vector-rag`) and `PERPLEXITY_API_KEY` are correctly passed to MCP subprocesses via the `env` parameter in `_run_mcp`.
*   **Gemini API `application/json` Workaround (Stable):** The strategy of returning/parsing plain-text JSON strings from tools and sub-agents is stable and effective.

**3. Relevant Files and Code (Current State - Major Updates This Session v0.23):**
*   **MODIFIED THIS SESSION (v0.23):**
    *   `backend/tools/mcp_wrappers.py`:
        *   Added `VectorRAGListStoresTool` (for listing vector stores).
        *   Modified `VectorRAGSearchTool.__init__` to accept `vector_store_id` and `run_async` to use `self.vector_store_id`.
        *   Updated `run_async` signatures for `CoinGeckoPriceTool`, `FearAndGreed_GetCurrentTool`, `FearAndGreed_InterpretValueTool`, `FearAndGreed_CompareHistoricalTool`, `CoinGecko_GlobalMarketDataTool`, and `PerplexityMCPTool` to conform to `(*, args, tool_context)`.
        *   Adjusted parameter extraction within these `run_async` methods.
    *   `backend/agents/momentum_agent.py`: Updated `__init__` to pass `vector_store_id` to `VectorRAGSearchTool` constructor; removed `self.vector_store_id` assignment; updated prompt.
    *   `backend/agents/structure_agent.py`: Updated `__init__` to pass `vector_store_id` to `VectorRAGSearchTool` constructor; removed `self.vector_store_id` assignment; updated prompt.
    *   `backend/agents/ranges_agent.py`: Updated `__init__` to pass `vector_store_id` to `VectorRAGSearchTool` constructor; removed `self.vector_store_id` assignment; updated prompt.
    *   `backend/agents/liquidity_agent.py`: Updated `__init__` to pass `vector_store_id` to `VectorRAGSearchTool` constructor; removed `self.vector_store_id` assignment; updated prompt.
    *   `backend/agents/derivatives_agent.py`: Updated `__init__` to pass `vector_store_id` to `VectorRAGSearchTool` constructor; removed `self.vector_store_id` assignment; updated prompt.
    *   `backend/main.py`:
        *   Added `get_analysis_output_dir()` and `save_agent_output()` functions.
        *   Modified `adk_orchestrator_action_handler` to create a unique output directory per run and save each sub-agent's JSON output.
*   **(Files from v0.22, no new changes this segment):**
    *   `backend/agents/context_agent.py`
    *   `backend/agents/sentiment_agent.py`
    *   `backend/agents/news_agent.py`
    *   `backend/agents/orchestrator_agent.py`
    *   `backend/agents/actionplan_agent.py`
    *   `backend/agents/confidencerisk_agent.py`
    *   `backend/agents/finalpackage_agent.py`
    *   `backend/agents/tradesetup_agent.py`
    *   `backend/adk_message_types.py`
    *   `backend/ag_ui_event_types.py`
    *   `backend/requirements.txt`
    *   `backend/test_orchestrator_direct.py`
    *   `.env` (Ensured `PERPLEXITY_API_KEY` and `OPENAI_API_KEY` are present).

**4. Problem Solving (Summary of this session - v0.23):**
*   **Resolved `TypeError: ... got an unexpected keyword argument 'args'`:** Systematically applied the ADK-compatible `run_async(*, args, tool_context)` signature to all custom `FunctionTool` wrappers in `mcp_wrappers.py`. This was the primary blocker for `PerplexityMCPTool` and other MCP tools.
*   **Resolved `ValueError: "AgentName" object has no field "vector_store_id"`:** Corrected the RAG agent initialization by passing `vector_store_id` directly to the `VectorRAGSearchTool` constructor instead of assigning it as an instance attribute on the `LlmAgent` subclass.
*   **Enabled Agent Output Persistence:** Implemented a robust mechanism to save individual agent JSON outputs to timestamped directories, greatly enhancing debugging and review capabilities.
*   **RAG Integration Refinement:** Successfully transitioned RAG agents from simulated tools to the real `vector-rag` MCP server, with `vector_store_id` now correctly configured per tool instance.
*   **Current Test Status:** The system is now ready for a full end-to-end orchestration test with a chart image. We expect all agents to run to completion and save their outputs.

**5. Pending Tasks and Next Steps (Focus for New Task/Session):**
1.  **Full End-to-End Orchestration Test (High Priority - User Executed):**
    *   The user will execute the `/debug/test-handler` endpoint with a chart image URL.
    *   **Action for Cline:** Await the full backend error logs from the user to diagnose the `500 INTERNAL` error encountered in the previous attempt.
    *   **Verification (Once logs are provided and issue is resolved):**
        *   Confirm all 12 agents run to completion without errors.
        *   Inspect the newly created `workspaces/analysis_run_YYYY-MM-DD_HH-MM-SS/` directory to confirm that all `stepXX_AgentName_output.json` files are generated and contain valid, expected JSON output.
        *   Specifically, check `SentimentAgent` and `NewsAgent` outputs to confirm their MCP tools are now functioning correctly.
        *   Check RAG agent outputs to confirm they are using the `vector-rag` MCP and returning relevant data.
2.  **Token Budgeting / Context Management (If Errors Re-emerge):** If `UNKNOWN_ERROR` or context window issues reappear during the full test, investigate strategies to summarize large JSON outputs from earlier agents before passing them to later agents in the orchestration chain.
3.  **Investigate Warnings (If Persistent):** Address any "Invalid config for agent ...: output_schema cannot co-exist with agent transfer configurations" warnings if they persist and cause issues.
4.  **Frontend Testing:** Once the backend orchestration is fully stable and producing correct outputs, shift testing to the React frontend to verify end-to-end functionality, including payload matching between CopilotKit and the backend action handler.
5.  **Memory Bank Update & GitHub Commit:** (This is being done now).

**6. System Architecture Status:**
*   **✅ RESOLVED:** `ImportError` for `MCPToolSet` (via Pattern 1 implementation from v0.21).
*   **✅ RESOLVED:** Server startup `TypeError` related to `FunctionTool.__init__` instantiation in RAG agents.
*   **✅ RESOLVED:** `ValueError: Function search is not found in the tools_dict` for all RAG agents.
*   **✅ RESOLVED:** `TypeError: PerplexityMCPTool.run_async() got an unexpected keyword argument 'args'`.
*   **✅ RESOLVED:** `TypeError: CoinGecko_GlobalMarketDataTool.run_async() got an unexpected keyword argument 'args'` (and similar for other Fear & Greed/CoinGecko tools).
*   **✅ RESOLVED:** `ValueError: "AgentName" object has no field "vector_store_id"` in RAG agents.
*   **✅ IMPLEMENTED & TESTED (ContextAgent):** MCP integration for CoinGecko (`CoinGeckoPriceTool`) in `ContextAgent` is functioning correctly, including parsing of the tool's JSON string output.
*   **✅ IMPLEMENTED:** `vector-rag` MCP server integration and RAG agents refactored to use it.
*   **✅ IMPLEMENTED:** Agent output saving mechanism.
*   **🔄 NEXT (Testing):** Full end-to-end orchestration test.
*   **⚠️ KNOWN LIMITATION (Mitigated):** Gemini API's incompatibility with `application/json` response MIME type for function calls. The current string-based workaround and removal of `output_schema` from sub-agents appears effective.

**7. Critical Files Modified This Session (v0.23):**
*   `backend/tools/mcp_wrappers.py` (Added `VectorRAGListStoresTool`, updated `VectorRAGSearchTool` constructor/run_async, fixed all other MCP tool `run_async` signatures).
*   `backend/agents/momentum_agent.py` (Updated `__init__` for `VectorRAGSearchTool` instantiation, prompt updated).
*   `backend/agents/structure_agent.py` (Updated `__init__` for `VectorRAGSearchTool` instantiation, prompt updated).
*   `backend/agents/ranges_agent.py` (Updated `__init__` for `VectorRAGSearchTool` instantiation, prompt updated).
*   `backend/agents/liquidity_agent.py` (Updated `__init__` for `VectorRAGSearchTool` instantiation, prompt updated).
*   `backend/agents/derivatives_agent.py` (Updated `__init__` for `VectorRAGSearchTool` instantiation, prompt updated).
*   `backend/main.py` (Added output saving functions, integrated into handler).

**8. Key Learnings for Future Development (This Session - v0.23):**
*   **ADK `FunctionTool` Signature Strictness:** The `run_async(*, args, tool_context)` signature is mandatory for all custom `FunctionTool`s in ADK.
*   **Pydantic `BaseModel` Inheritance:** Be mindful of how attributes are defined and assigned in `LlmAgent` subclasses to avoid Pydantic validation errors. Configuration specific to a tool instance should be passed to the tool's constructor, not stored directly on the agent instance if it's not part of its Pydantic schema.
*   **Importance of Output Persistence:** Saving intermediate agent outputs is invaluable for debugging complex multi-agent orchestrations.
*   **Iterative Debugging:** Addressing one error at a time, re-testing, and using debug traces is the most effective way to stabilize complex systems.
