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

// --- Subclass Approach for CopilotRuntime v1.8.x (and compatible next releases) ---
// This avoids the ES module binding issue by subclassing instead of reassigning the import.
// The subclass overrides getAdapter() in the constructor to ensure our geminiRuntimeAdapter is used.
class PatchedRuntime extends CopilotRuntime {
  constructor(opts: any) {
    super(opts);
    // Override the getAdapter method to return our Gemini adapter
    (this as any).getAdapter = () => geminiRuntimeAdapter;
  }
}

// Configure CopilotRuntime using the patched subclass.
const runtime = new PatchedRuntime({
  remoteEndpoints: [
    { url: FASTAPI_BACKEND_ENDPOINT_URL }
  ],
  actions: [], // No local Node.js actions defined
});

console.log("✅ PatchedRuntime (CopilotRuntime subclass) created with GoogleGenerativeAIAdapter override.");
console.log(`CopilotKit Runtime (@copilotkit/runtime@^1.8.14-next.2) configured with remoteEndpoints.`);
console.log(`GoogleGenerativeAIAdapter (model: gemini-2.5-flash-preview-05-20) injected via subclass.`);

// Use copilotRuntimeNextJSAppRouterEndpoint
// The runtime instance itself is now LLM-aware via the subclass.
// CRITICAL: Use geminiRuntimeAdapter as serviceAdapter instead of emptyServiceAdapter
// to ensure the endpoint handler uses our Gemini adapter for primary processing.
const { POST: corePOST } =
  copilotRuntimeNextJSAppRouterEndpoint({
    runtime,
    endpoint: "/api/copilotkit",
    serviceAdapter: geminiRuntimeAdapter, // Changed from emptyServiceAdapter to geminiRuntimeAdapter
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
