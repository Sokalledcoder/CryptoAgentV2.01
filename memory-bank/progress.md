# Progress: Crypto TA Multi-Agent System

**Version:** 0.8
**Date:** 2025-05-30

## 1. What Works / Completed

*   **Project Re-Planning:** Formulated and agreed upon a revised, more detailed multi-phase project plan. (Carried Over)
*   **Critical Diagnostic Correction & Full Verification (Phase 0 Complete):** (Carried Over)
    *   `hello_agent` in `examples` package fully tested and working.
*   **Phase 1 Progress - Inter-Agent Communication via `AgentTool` (Tested with `adk web`):** (Carried Over)
    *   `ContextAgent` (named `analyze_chart_context`) created.
    *   `OrchestratorAgent` created and successfully calls `ContextAgent` via `adk web`.
*   **FastAPI Programmatic Invocation (RESOLVED):** (Carried Over)
    *   Successfully unblocked programmatic invocation of ADK agents via `Runner.run_async` by creating custom Pydantic models (`backend/adk_message_types.py`) for `new_message`.
*   **Backend Refactoring with CopilotKit Python SDK (COMPLETED):**
    *   Integrated the `copilotkit` Python SDK into the FastAPI backend (`backend/main.py`).
    *   Added `copilotkit` to dependencies and installed it.
    *   Configured CORS middleware.
    *   Defined a CopilotKit `Action` (`runCryptoTaOrchestrator`) that wraps the invocation of the ADK `OrchestratorAgent` using the existing ADK `Runner` setup.
    *   Used `CopilotKitRemoteEndpoint` and `add_fastapi_endpoint` to expose an AG-UI compliant endpoint at `/copilotkit`.
    *   The previous custom SSE implementation is now superseded by the CopilotKit SDK's handling of AG-UI event streaming.
    *   The FastAPI server starts successfully with this new configuration.
*   **Phase 1 - Node.js CopilotKitRuntime Setup & Refinement (COMPLETED):**
    *   Successfully set up a Node.js project (`copilotkit-runtime-node`) using Next.js for the CopilotKit Runtime middleware.
    *   Installed and configured `@copilotkit/runtime` and related packages.
    *   Iteratively debugged and refactored the Next.js API route (`copilotkit-runtime-node/src/app/api/copilotkit/route.ts`) to correctly handle requests, forward them to the FastAPI backend (using a custom `FastApiAdapter`), and manage CORS robustly. This resolved previous TypeScript and API versioning issues.
*   **Phase 1 - Basic Frontend Development (React/CopilotKit) (COMPLETED):**
    *   Successfully set up a basic React project (`copilotkit-react-frontend`) using Vite + TypeScript.
    *   Installed `@copilotkit/react-core` and `@copilotkit/react-ui`.
    *   Configured the React app with `<CopilotKit url="http://localhost:3000/api/copilotkit">` provider and included the `<CopilotChat />` component.
*   **Phase 1 - Package Upgrades (COMPLETED):**
    *   Upgraded all relevant `@copilotkit/*` packages in both Node.js runtime and React frontend projects to their latest versions.
*   **Phase 1 - Initial End-to-End Testing (ATTEMPTED):**
    *   All three services (FastAPI backend, Next.js runtime, React frontend) were started successfully.
    *   CORS issues between the React frontend and the Next.js runtime were resolved.
    *   Initial network handshakes (OPTIONS, POST) from the frontend to the Node.js runtime were successful.
    *   Automated browser testing of `<CopilotChat />` message sending was problematic; the send action did not reliably trigger. Manual verification is required.
*   **Initial Documentation & Memory Bank Update:** Core Memory Bank files updated (including this one and `activeContext.md` based on the latest handoff). (Carried Over & Ongoing)
*   **Asset Collection:** (Carried Over)
    *   User has provided 12 agent-specific prompts. (Carried Over)
    *   User has provided documentation for MCP servers. (Carried Over)
    *   User has provided initial documents for the RAG knowledge base. (Carried Over)
    *   User has provided an example workspace output. (Carried Over)

## 2. What's Left to Build / In Progress (Next Steps)

*   **Phase 1 - Manual End-to-End Test (CRITICAL NEXT STEP):**
    *   Start all three servers (FastAPI backend at `http://localhost:8000`, Next.js runtime at `http://localhost:3000`, Vite frontend at `http://localhost:5173`).
    *   Manually open `http://localhost:5173` in a browser.
    *   Attempt to send a message (e.g., "Hello") using the `<CopilotChat />` UI.
    *   **Verify:**
        *   The message appears in the UI.
        *   Network requests flow correctly: Frontend (`:5173`) -> Node.js Runtime (`:3000/api/copilotkit`) -> FastAPI Backend (`:8000/copilotkit`). Check browser dev tools (Network tab) and server logs for all three services.
        *   The ADK agent in the FastAPI backend processes the request (check FastAPI logs for `OrchestratorAgent` activity).
        *   A response is streamed back from FastAPI -> Node.js Runtime -> Frontend and displayed in the UI.
    *   Troubleshoot any issues, particularly with the frontend component's send functionality or response rendering. Consult the "Frontend sanity checklist" from the user's run-book if issues arise.
*   **Phase 1 - Further Agent Development:** (Post successful E2E Test)
    *   Begin development of the 12 specialized ADK Task Agents based on user-provided prompts.
    *   Integrate these into the `OrchestratorAgent` (likely via `AgentTool`).
    *   Implement MCP tool calls within these specialized agents.
*   **Memory Bank Maintenance:** Continue to update all Memory Bank files with new learnings, decisions, and progress.
*   **Future Phases:** (Carried Over)
    *   Refine inter-agent communication (potentially A2A protocol).
    *   Integrate RAG system.
    *   Advanced features, comprehensive testing, deployment planning.

## 3. Current Status

*   **Overall:** Backend (FastAPI with CopilotKit Python SDK), Node.js CopilotKitRuntime (Next.js with `FastApiAdapter`), and React/CopilotKit frontend are set up. Key configurations for CORS and request proxying are in place. All `@copilotkit/*` packages are at `@latest`.
*   **Blocker:** Successful end-to-end message flow via the `<CopilotChat />` UI needs manual verification. Automated tests were inconclusive.
*   **Risks:**
    *   Potential issues in the frontend's interaction with the CopilotKit SDK or the Node.js runtime.
    *   Complexity of debugging the full three-tier communication flow.

## 4. Evolution of Project Decisions

*   **Initial Plan (OpenAI Agents SDK):** Shifted to Google-centric stack (ADK, A2A). (Carried Over)
*   **Backend AG-UI Streaming:** Shifted from manual SSE implementation to using the `copilotkit` Python SDK for FastAPI, which simplifies AG-UI compliance.
*   **Frontend:** AG-UI with React/CopilotKit.
*   **RAG:** Requirement confirmed, implementation details deferred.
*   **Agent Structure:** 12-specialized-agent model.
*   **ADK Agent Discovery/Invocation:** Refined understanding (`__init__.py`, `root_agent` for `adk web`; `Runner` for programmatic).
*   **Gemini Model Access:** Confirmed Google AI Studio API key (`GOOGLE_GENAI_USE_VERTEXAI=FALSE`).
*   **CRITICAL CORRECTION - Namespace Package & ADK Provider & ADK Web/Tool Discovery:** (Carried Over - Still Relevant)
    *   Key import paths and tool definition methods for ADK v1.1.1 clarified.
    *   Method for constructing `new_message` for `Runner.run_async` (ADK v1.1.1) using custom Pydantic models confirmed.
    *   All agents confirmed working with `gemini-2.5-flash-preview-05-20` when tested via `adk web`.
*   **CopilotKit Versioning & API Nuances:**
    *   Significant learnings regarding API changes and type definitions (e.g., `CopilotRuntimeChatCompletionResponse` being `Response & { threadId: string; }`) across `@copilotkit/runtime` versions. The "Decoder Ring" was vital.
    *   The `FastApiAdapter` pattern in `copilotkit-runtime-node/src/app/api/copilotkit/route.ts` is the current stable solution for integrating with the FastAPI backend.
