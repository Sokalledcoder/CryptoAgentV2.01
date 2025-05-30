# Progress: Crypto TA Multi-Agent System

**Version:** 0.12
**Date:** 2025-05-31

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
    *   **Resolved Node.js `CopilotRuntime` LLM Adapter Configuration (COMPLETED THIS SESSION - Constructor Patch for @next tag):**
        *   Confirmed `@copilotkit/runtime` is at version `^1.8.14-next.2` after clean install using the `next` dist-tag.
        *   Implemented the "constructor patch" workaround in `copilotkit-runtime-node/src/app/api/copilotkit/route.ts` as direct constructor injection of the adapter was still resulting in fallback to `EmptyAdapter`. This patch involves:
            *   Instantiating `GoogleGenerativeAIAdapter` with `model` ("gemini-2.5-flash-preview-05-20") and `apiKey` (options cast `as any` to handle potential type mismatches in `^1.8.14-next.2`).
            *   Replacing the `CopilotRuntime` constructor with a patched version that calls the original constructor and then explicitly overwrites the instance's `getAdapter` method to return the configured `geminiRuntimeAdapter`.
        *   This advanced workaround aims to definitively ensure the custom adapter is used, bypassing issues with internal closures in 1.8.x-like versions.
        *   TypeScript errors for `apiKey` (in adapter options) and the constructor patch assignment have been addressed with `as any` casts.
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

*   **Phase 1 - Manual End-to-End Test (CRITICAL NEXT STEP - System Ready):**
    *   With the Node.js runtime LLM adapter now configured, the system is ready for a full E2E test.
    *   Start all three servers (FastAPI backend at `http://localhost:8000`, Next.js runtime at `http://localhost:3000`, Vite frontend at `http://localhost:5173`).
    *   Manually open `http://localhost:5173` in a browser.
    *   Attempt to send a message (e.g., "Hello") using the `<CopilotChat />` UI.
    *   **Verify:**
        *   POST requests to `/copilotkit/info` from Node.js runtime to FastAPI backend occur.
        *   When a message is sent from the UI, the Node.js runtime does not call `EmptyAdapter.process()` (it should now use `geminiAdapter` or directly invoke the remote action).
        *   The FastAPI backend receives a `tool_calls` (or similar SDK-formatted) request to execute `runCryptoTaOrchestrator`.
        *   The `adk_orchestrator_action_handler` in FastAPI is invoked and streams its response.
        *   The Next.js runtime correctly processes this stream and the `this.callback is not a function` error (if previously occurring due to `EmptyAdapter`) is resolved.
        *   The React frontend displays the streamed response.
    *   Troubleshoot any issues. Consult the "Frontend sanity checklist" from the user's run-book if issues arise.
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

*   **Overall:** Backend (FastAPI with CopilotKit Python SDK), Node.js CopilotKitRuntime (Next.js with `@copilotkit/runtime` at `^1.8.14-next.2`, configured with the constructor patch for `GoogleGenerativeAIAdapter`, and `remoteEndpoints`), and React/CopilotKit frontend are set up.
*   **Blocker:** Node.js runtime LLM adapter configuration implemented using the constructor patch for `@copilotkit/runtime@^1.8.14-next.2`. The system is now ready for a decisive E2E test.
*   **Risks:**
    *   The constructor patch, while robust for 1.8.x behavior, is a workaround and might have unforeseen side effects or break with future non-major updates to the runtime if its internal structure changes.
    *   The `next` tagged pre-release version (`^1.8.14-next.2`) might have its own instabilities.
    *   Potential issues in the frontend's interaction with the CopilotKit SDK or the Node.js runtime during E2E testing.
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
    *   The constructor patch for `CopilotRuntime` in `copilotkit-runtime-node/src/app/api/copilotkit/route.ts` is the current configuration for enabling LLM-driven remote action dispatch with `@copilotkit/runtime@^1.8.14-next.2`.
