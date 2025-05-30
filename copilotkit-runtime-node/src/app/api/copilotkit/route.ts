import { NextRequest, NextResponse } from "next/server";
import {
  CopilotRuntime,
  copilotRuntimeNextJSAppRouterEndpoint,
  CopilotServiceAdapter,
  CopilotRuntimeChatCompletionRequest,
  CopilotRuntimeChatCompletionResponse, // This is Response & { threadId: string }
  GoogleGenerativeAIAdapter, // Import GoogleGenerativeAIAdapter
  // Message type is implicitly part of CopilotRuntimeChatCompletionRequest
  // Parameter is used by RemoteChainParameters, ensure it's available or define if simple
} from "@copilotkit/runtime"; 
import { GoogleGenerativeAI } from "@google/generative-ai"; // Import base Google SDK
// If Parameter type is complex, it might need its own import or definition.
// For now, assuming it's simple enough or not strictly needed for this basic langserve setup.

const FASTAPI_BACKEND_ENDPOINT_URL = "http://localhost:8000/copilotkit"; 

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

// EmptyAdapter as per user's research for langserve approach
class EmptyAdapter implements CopilotServiceAdapter {
  async process(
    req: CopilotRuntimeChatCompletionRequest
  ): Promise<CopilotRuntimeChatCompletionResponse> {
    console.error(
      "EmptyAdapter.process() was called unexpectedly. Langserve should handle requests to remote chains."
    );
    const errorResponseBase = new Response(
      JSON.stringify({ error: "EmptyAdapter should not process requests." }),
      { status: 500, headers: { "Content-Type": "application/json" } }
    );
    const errorResponse = Object.assign(errorResponseBase, {
      threadId: req.threadId ?? `err-thread-${Date.now()}`
    }) as CopilotRuntimeChatCompletionResponse;
    return errorResponse;
  }
}
const emptyServiceAdapter = new EmptyAdapter();

// Instantiate Google Generative AI SDK
// Ensure GOOGLE_API_KEY is set in the environment for this Node.js process
const genAI = new GoogleGenerativeAI(process.env.GOOGLE_API_KEY || ""); 
if (!process.env.GOOGLE_API_KEY) {
  console.warn("GOOGLE_API_KEY is not set. GoogleGenerativeAIAdapter may not function.");
}

// Instantiate the GoogleGenerativeAIAdapter
// Using the model name as per user's preference (can be adjusted)
// The user's example: new GoogleGenerativeAIAdapter({ model: "gemini-1.5-pro" })
// A common model is "gemini-pro". Let's use that as a default.
// Correcting to use 'model' instead of 'modelName' as per user's example and to fix TS error.
const geminiAdapter = new GoogleGenerativeAIAdapter({ 
  model: "gemini-pro", // Or "gemini-1.5-pro-latest" or user preferred
  // generativeAi: genAI, // This might be needed if the adapter doesn't pick up genAI contextually
});

// Configure CopilotRuntime. Removing 'adapter' property due to persistent TS error.
// We will test if remoteEndpoints can function if the client specifies the action.
const runtime = new CopilotRuntime({
  // adapter: geminiAdapter, // Removed due to TS error: 'adapter' does not exist in CopilotRuntimeConstructorParams

  remoteEndpoints: [
    { url: FASTAPI_BACKEND_ENDPOINT_URL } 
  ],
  actions: [], // Explicitly defining actions as empty, as all are remote.
});

console.log(`CopilotKit Runtime configured with remoteEndpoints, targeting FastAPI at: ${FASTAPI_BACKEND_ENDPOINT_URL}`);

// Use copilotRuntimeNextJSAppRouterEndpoint with the remoteEndpoints-configured runtime.
// An EmptyAdapter is still appropriate as the actual action processing is remote.
const { POST: corePOST } = 
  copilotRuntimeNextJSAppRouterEndpoint({
    runtime, // This runtime instance now has remoteEndpoints configured
    endpoint: "/api/copilotkit", // The Next.js API route path
    serviceAdapter: emptyServiceAdapter, // Pass the EmptyAdapter
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
