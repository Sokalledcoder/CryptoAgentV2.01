import { NextRequest, NextResponse } from "next/server";
import {
  CopilotRuntime,
  copilotRuntimeNextJSAppRouterEndpoint,
  CopilotServiceAdapter,
  CopilotRuntimeChatCompletionRequest,
  CopilotRuntimeChatCompletionResponse, // This is Response & { threadId: string }
  GoogleGenerativeAIAdapter, // Import GoogleGenerativeAIAdapter from runtime
  // Message type is implicitly part of CopilotRuntimeChatCompletionRequest
  // Parameter is used by RemoteChainParameters, ensure it's available or define if simple
} from "@copilotkit/runtime";
// Note: GoogleGenerativeAI SDK itself is not directly needed here if the adapter handles client creation.
// If Parameter type is complex, it might need its own import or definition.
// For now, assuming it's simple enough or not strictly needed for this basic langserve setup.

const FASTAPI_BACKEND_ENDPOINT_URL = process.env.FASTAPI_URL || "http://localhost:8000/copilotkit";

// CORS Configuration
const allowedOrigin = "http://localhost:5173"; // Vite frontend
const CORS_HEADERS = {
  "Access-Control-Allow-Origin": allowedOrigin,
  "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
  "Access-Control-Allow-Headers":
    "Content-Type,Authorization,Baggage,Sentry-Trace," +
    "X-CopilotKit-Referral,X-CopilotKit-Runtime-Client-Gql-Version",
  "Access-Control-Allow-Credentials": "true",
} as const;

// EmptyAdapter: A fallback service adapter.
// As per research, with CopilotRuntime having its own LLM adapter,
// this serviceAdapter for copilotRuntimeNextJSAppRouterEndpoint might handle
// scenarios not covered by the runtime's primary LLM or remote actions.
class EmptyAdapter implements CopilotServiceAdapter {
  async process(
    req: CopilotRuntimeChatCompletionRequest
  ): Promise<CopilotRuntimeChatCompletionResponse> {
    console.error(
      "EmptyAdapter.process() was called. This might indicate an issue if an LLM-driven response or remote action was expected."
    );
    const errorResponseBase = new Response(
      JSON.stringify({ error: "EmptyAdapter reached; LLM or remote action might not have been triggered." }),
      { status: 500, headers: { "Content-Type": "application/json" } }
    );
    // Ensure the response conforms to CopilotRuntimeChatCompletionResponse
    const errorResponse = Object.assign(errorResponseBase, {
      threadId: req.threadId ?? `err-thread-${Date.now()}`
    }) as CopilotRuntimeChatCompletionResponse;
    return errorResponse;
  }
}
const emptyServiceAdapter = new EmptyAdapter();

// Instantiate the GoogleGenerativeAIAdapter for CopilotRuntime
// The adapter will use the GOOGLE_API_KEY from the environment.
// For v1.8.13, type definitions might be stricter than runtime capabilities.
// Per user research citing 1.8-branch README, try passing apiKey.
// User wants to use "gemini-2.5-flash-preview-05-20".
// With @copilotkit/runtime@^1.8.14-next.2, types for 'apiKey' might still be lagging.
// Cast options to 'any' to bypass potential TypeScript error, assuming runtime compatibility.
const geminiRuntimeAdapter = new GoogleGenerativeAIAdapter({
  model: "gemini-2.5-flash-preview-05-20",
  apiKey: process.env.GOOGLE_API_KEY,
} as any); // Added 'as any' back to options

// --- Constructor Patch for CopilotRuntime v1.8.x (and compatible next releases) ---
// This patch intercepts the CopilotRuntime constructor to overwrite the
// instance-level getAdapter() closure, ensuring our geminiRuntimeAdapter is used.
const CopilotRuntimeOrig = CopilotRuntime;
(CopilotRuntime as any) = function PatchedCopilotRuntime(opts: any) {
  const rt = new CopilotRuntimeOrig(opts);
  // Overwrite the instance's getAdapter method
  (rt as any).getAdapter = () => geminiRuntimeAdapter;
  return rt;
}; // Removed 'as typeof CopilotRuntimeOrig' to simplify type assertion for the assignment
console.log("✅ CopilotRuntime constructor patched to ensure GoogleGenerativeAIAdapter is used for getAdapter().");
// --- End Constructor Patch ---

// Configure CopilotRuntime.
// The 'adapter' option in constructor is ignored by 1.8.x versions including ^1.8.14-next.2 due to internal closure.
// The patch above ensures geminiRuntimeAdapter is used.
const runtime = new CopilotRuntime({
  // No 'adapter' property here; it's handled by the patch.
  remoteEndpoints: [
    { url: FASTAPI_BACKEND_ENDPOINT_URL }
  ],
  actions: [], // No local Node.js actions defined
});

console.log(`CopilotKit Runtime (@copilotkit/runtime@^1.8.14-next.2) configured with remoteEndpoints.`);
console.log(`GoogleGenerativeAIAdapter (model: gemini-2.5-flash-preview-05-20) injected via constructor patch.`);

// Use copilotRuntimeNextJSAppRouterEndpoint
// The runtime instance itself is now LLM-aware.
// The serviceAdapter here acts as a fallback or for other specific purposes.
const { POST: corePOST } =
  copilotRuntimeNextJSAppRouterEndpoint({
    runtime,
    endpoint: "/api/copilotkit",
    serviceAdapter: emptyServiceAdapter, // Retained as per user's research example
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

export function OPTIONS() { // Changed to non-async as per Decoder Ring
  return new Response(null, { status: 204, headers: CORS_HEADERS });
}
