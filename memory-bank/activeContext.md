# Active Context: Crypto TA Multi-Agent System

**Version:** 0.8 (Updated from Handoff Report 2025-05-30)
**Date:** 2025-05-30

## 1. Current Work Focus & Overall Mission:
*   **Mission:** Build a multi-agent system for cryptocurrency technical analysis using Google ADK (Python), FastAPI, and React/CopilotKit.
*   **Current Stage:** Phase 1 (Backend Refactoring for CopilotKit Python SDK & AG-UI Compliance, Node.js Runtime Setup, Basic Frontend Setup, Initial End-to-End Testing).
*   **Work Done This Session (Leading to this Handoff):**
    *   Successfully set up a Node.js project (`copilotkit-runtime-node`) using Next.js for the CopilotKit Runtime middleware.
    *   Installed and configured `@copilotkit/runtime` and related packages.
    *   Iteratively debugged and refactored the Next.js API route (`copilotkit-runtime-node/src/app/api/copilotkit/route.ts`) to correctly handle requests, forward them to the FastAPI backend, and manage CORS. This involved significant troubleshooting of TypeScript type errors related to `@copilotkit/runtime` API versions and type definitions.
    *   The final successful approach for `route.ts` utilized "Pattern C" (Custom Adapter - `FastApiAdapter`) from the user-provided "Decoder Ring", which correctly defines `CopilotRuntimeChatCompletionResponse` as `Response & { threadId: string; }` and uses robust query extraction.
    *   Successfully set up a basic React project (`copilotkit-react-frontend`) using Vite + TypeScript.
    *   Installed `@copilotkit/react-core` and `@copilotkit/react-ui`.
    *   Configured the React app with `<CopilotKit url="...">` provider pointing to the Node.js runtime and included the `<CopilotChat />` component.
    *   Upgraded all relevant `@copilotkit/*` packages in both Node.js runtime and React frontend projects to their latest versions.
    *   Attempted end-to-end testing:
        *   All three services (FastAPI backend, Next.js runtime, React frontend) were started successfully.
        *   CORS issues between the React frontend and the Next.js runtime were resolved.
        *   Initial network handshakes (OPTIONS, POST) from the frontend to the Node.js runtime were successful.
        *   However, sending a message via the `<CopilotChat />` UI using automated browser actions proved problematic; the send action did not reliably trigger. A late log indicated a POST request might have gone through after browser closure, but UI verification was not possible.

## 2. Key Technical Concepts & Decisions (Updates/Reinforcements):
*   **Node.js Runtime (`copilotkit-runtime-node/src/app/api/copilotkit/route.ts`):**
    *   Final implementation uses a custom `FastApiAdapter` (implementing `CopilotServiceAdapter`) to proxy requests to the FastAPI backend.
    *   The adapter's `process` method correctly extracts the user query and "decorates" the `Response` object from `fetch` with a `threadId` to satisfy the `CopilotRuntimeChatCompletionResponse` type (`Response & { threadId: string; }`).
    *   `CopilotRuntime` is instantiated minimally, and `copilotRuntimeNextJSAppRouterEndpoint` is configured with this `runtime` instance, the `endpoint` path, and the `FastApiAdapter` instance.
    *   CORS is handled robustly with a dedicated `OPTIONS` handler and by wrapping the `POST` handler's response. Allowed headers now include `X-CopilotKit-Runtime-Client-Gql-Version`.
*   **CopilotKit Versioning & API Changes:**
    *   Significant learning about API changes between `@copilotkit/runtime` versions (e.g., `CustomHttpAgent` being refactored, `CopilotRuntime.response()` removed, structure of `langserve` parameters and `RemoteChainParameters` changing from object with `targetUrl` in ~v1.5.x to a string alias in v1.8.x for `RemoteChainParameters` when used in `langserve` array).
    *   The "Decoder Ring" provided by the user was crucial for understanding these version-specific type definitions and API usage patterns.
*   **ADK `Runner` & FastAPI Backend:** No changes this session, but remains the core backend logic being called by the Node.js runtime via the `FastApiAdapter`.
*   **React Frontend Setup:** Standard Vite + TypeScript with `@copilotkit/react-core` and `@copilotkit/react-ui`. `<CopilotKit>` provider and `<CopilotChat />` component are in place.

## 3. Relevant Files and Code (Current State - Key Files):**
*   **`copilotkit-runtime-node/src/app/api/copilotkit/route.ts` (Heavily Refactored - Key Achievement):**
    *   This is the most critical file from this session. Its final state implements "Pattern C" from the user's "Decoder Ring".
    *   **Content (as per Handoff Report):**
      ```typescript
      import { NextRequest, NextResponse } from "next/server";
      import {
        CopilotRuntime,
        copilotRuntimeNextJSAppRouterEndpoint,
        CopilotServiceAdapter,
        CopilotRuntimeChatCompletionRequest,
        CopilotRuntimeChatCompletionResponse, // This is Response & { threadId: string }
      } from "@copilotkit/runtime";

      const FASTAPI_BACKEND_ENDPOINT_URL = "http://localhost:8000/copilotkit";

      const allowedOrigin = "http://localhost:5173";
      const CORS_HEADERS = {
        "Access-Control-Allow-Origin": allowedOrigin,
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers":
          "Content-Type,Authorization,Baggage,Sentry-Trace," +
          "X-CopilotKit-Referral,X-CopilotKit-Runtime-Client-Gql-Version",
        "Access-Control-Allow-Credentials": "true",
      } as const;

      class FastApiAdapter implements CopilotServiceAdapter {
        constructor(private readonly url: string) {}

        async process(
          req: CopilotRuntimeChatCompletionRequest
        ): Promise<CopilotRuntimeChatCompletionResponse> {
          const lastMessage = req.messages.at(-1);
          let query: string = "";
          if (lastMessage) {
            const messageContent = (lastMessage as any).content;
            if (typeof messageContent === 'string') {
              query = messageContent;
            } else if (Array.isArray(messageContent) && messageContent.length > 0) {
              const textPart = messageContent.find(part => part.type === 'text');
              if (textPart && typeof (textPart as any).text === 'string') {
                query = (textPart as any).text;
              }
            }
          }
          if (!query && lastMessage) {
            console.warn("Could not extract query string from last message:", lastMessage);
          }
          const payload = { query: query };
          const backendResponse = await fetch(this.url, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
          });
          if (!backendResponse.ok) {
            const errorText = await backendResponse.text();
            console.error(`Error from FastAPI backend: ${backendResponse.status} ${errorText}`);
            throw new Error(`Backend request failed: ${backendResponse.status} ${errorText}`);
          }
          const responseWithThreadId = backendResponse as any; 
          responseWithThreadId.threadId = req.threadId ?? `thread_${Date.now()}`;
          return responseWithThreadId as CopilotRuntimeChatCompletionResponse;
        }
      }

      const serviceAdapter = new FastApiAdapter(FASTAPI_BACKEND_ENDPOINT_URL);
      const runtime = new CopilotRuntime({});
      const { POST: corePOST } =
        copilotRuntimeNextJSAppRouterEndpoint({
          runtime,
          endpoint: "/api/copilotkit", 
          serviceAdapter: serviceAdapter, 
      });

      export async function POST(req: NextRequest): Promise<Response> {
        const res = await corePOST(req);
        const newHeaders = new Headers(res.headers);
        Object.entries(CORS_HEADERS).forEach(([key, value]) => {
          newHeaders.set(key, value);
        });
        return new Response(res.body, {
          status: res.status,
          statusText: res.statusText,
          headers: newHeaders,
        });
      }

      export function OPTIONS() {
        return new Response(null, { status: 204, headers: CORS_HEADERS });
      }
      ```
*   **`copilotkit-runtime-node/package.json` (Implicitly Updated):** `@copilotkit/runtime` and `@copilotkit/backend` updated to `@latest`.
*   **`copilotkit-react-frontend/package.json` (Implicitly Updated):** `@copilotkit/react-core` and `@copilotkit/react-ui` updated to `@latest`.
*   **`copilotkit-react-frontend/src/main.tsx` (Configured):** Sets up `<CopilotKit url="http://localhost:3000/api/copilotkit">`.
*   **`copilotkit-react-frontend/src/App.tsx` (Configured):** Uses `<CopilotChat />`.
*   **`backend/main.py` (Unchanged this session):** Still the FastAPI backend with CopilotKit Python SDK, being called by the Node.js runtime.
*   **Memory Bank Files:**
    *   `memory-bank/progress.md` to be updated to v0.8.
    *   This file (`activeContext.md`) is now v0.8.
    *   Other core memory bank files (v0.2).

## 4. Problem Solving & Key Learnings (Focus on previous session):**
*   **TypeScript Hell with `@copilotkit/runtime`:** The majority of the previous session was spent battling TypeScript errors in the Node.js runtime.
*   **"Decoder Ring" was Pivotal:** Essential for understanding version-specific API details and type structures.
*   **CORS Resolution:** Successfully configured CORS in the Next.js API route.
*   **Package Upgrades:** Ensured all `@copilotkit/*` packages were updated to `@latest`.
*   **Frontend Interaction Blocker:** Automated browser testing of `<CopilotChat />` message sending was unsuccessful. This requires manual testing.
*   **Query Extraction:** Refined logic in `FastApiAdapter` for robust query extraction.

## 5. Pending Tasks and Next Steps (for this session):**
1.  **Manual End-to-End Test:**
    *   Start all three servers (FastAPI, Next.js runtime, Vite frontend).
    *   Manually open `http://localhost:5173` in a browser.
    *   Attempt to send a message (e.g., "Hello") using the `<CopilotChat />` UI.
    *   Verify:
        *   The message appears in the UI.
        *   Network requests flow correctly (Frontend -> Node -> FastAPI). Check browser dev tools (Network tab) and server logs.
        *   The ADK agent in FastAPI processes the request.
        *   A response is streamed back and displayed in the UI.
    *   Troubleshoot any issues, particularly with the frontend component's send functionality or response rendering. Check the "Frontend sanity checklist" from the user's run-book.
2.  **Further Agent Development (Phase 1):**
    *   Once basic end-to-end communication is confirmed, begin developing the 12 specialized ADK Task Agents.
    *   Integrate these into the `OrchestratorAgent`.
    *   Implement MCP tool calls within these agents.
3.  **Memory Bank Update:** Ensure all Memory Bank files are updated with the latest architectural decisions and learnings from this session (this handoff report serves as a major update to `activeContext.md` and `progress.md`). (This step is partially complete by updating this file).

## 6. Active Decisions & Considerations
*   The current setup relies on the `FastApiAdapter` in the Node.js runtime to correctly proxy requests and handle the response structure for CopilotKit.
*   Manual testing is critical to confirm the frontend interaction with `<CopilotChat />` works as expected.
*   The custom Pydantic models in `adk_message_types.py` remain essential for the internal ADK `Runner` invocation within the FastAPI backend.

## 7. Important Patterns & Preferences (User-Defined)
*   Emphasis on detailed, step-by-step planning before implementation.
*   Requirement for comprehensive documentation (Memory Bank).
*   Preference for using Google's AI/agent ecosystem where appropriate.
*   Need for a frictionless RAG implementation.
*   Desire for a responsive front-end experience (AG-UI, CopilotKit).
*   **CRITICAL:** Do not assume command success without full terminal output confirmation.

## 8. Learnings & Project Insights (From previous session)
*   The project is complex, involving multiple cutting-edge protocols and SDKs.
*   Clear, iterative planning and strong documentation are crucial for success.
*   The user has a well-defined existing workflow (12 prompts) which provides a strong blueprint for the multi-agent design.
*   **Operational Rigor:** Explicit confirmation of command execution success is paramount.
*   **SDK Specifics & Versioning:** API changes and type definitions in SDKs like `@copilotkit/runtime` can be a major source of friction. Careful attention to versioning and documentation (or "decoder rings") is necessary.
*   **CORS:** Requires careful configuration, especially with custom headers.
