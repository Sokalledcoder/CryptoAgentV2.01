import { NextRequest, NextResponse } from "next/server";
import {
  CopilotRuntime,
  copilotRuntimeNextJSAppRouterEndpoint,
  CopilotServiceAdapter,
  CopilotRuntimeChatCompletionRequest,
  CopilotRuntimeChatCompletionResponse, // This is Response & { threadId: string }
  // Message type is implicitly part of CopilotRuntimeChatCompletionRequest
} from "@copilotkit/runtime";

const FASTAPI_BACKEND_ENDPOINT_URL = "http://localhost:8000/copilotkit/"; // Added trailing slash

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

// Custom Adapter (Pattern C from Decoder Ring)
class FastApiAdapter implements CopilotServiceAdapter {
  constructor(private readonly url: string) {}

  async process(
    req: CopilotRuntimeChatCompletionRequest
  ): Promise<CopilotRuntimeChatCompletionResponse> {
    const lastMessage = req.messages.at(-1); // Renamed 'last' to 'lastMessage' for consistency
    
    // Robust query extraction from user's run-book
    const query =
      typeof (lastMessage as any)?.content === "string"
        ? (lastMessage as any)?.content
        : (lastMessage as any)?.content?.[0]?.text ?? "";

    // The 'if (!query && lastMessage)' warning block is no longer needed
    // as the above line defaults to "" if content is not found or not in expected shape.
    // A console.warn can be added here if lastMessage itself is undefined, if desired.
    if (!lastMessage) {
      console.warn("No last message found in request.");
    } else if (query === "") {
      // Only warn if there was a last message but we couldn't extract a query.
      console.warn("Extracted empty query from last message:", lastMessage);
    }
    
    // const payload = { query: query }; // We will send the whole req object
    
    const backendResponse = await fetch(this.url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      // body: JSON.stringify(payload), // Old: send only query
      body: JSON.stringify(req), // New: send the entire CopilotRuntimeChatCompletionRequest
    });

    if (!backendResponse.ok) {
      const errorText = await backendResponse.text();
      console.error(`Error from FastAPI backend: ${backendResponse.status} ${errorText}`);
      throw new Error(`Backend request failed: ${backendResponse.status} ${errorText}`);
    }

    // Decorate the Response with the required threadId and return it
    const responseWithThreadId = backendResponse as any; 
    responseWithThreadId.threadId = req.threadId ?? `thread_${Date.now()}`;
    return responseWithThreadId as CopilotRuntimeChatCompletionResponse;
  }
}

const serviceAdapter = new FastApiAdapter(FASTAPI_BACKEND_ENDPOINT_URL);

const runtime = new CopilotRuntime({
  // For Pattern C, CopilotRuntime is often minimal, with logic in the adapter.
  // actions: [], // If no Node-side actions.
});

const { POST: corePOST } = // OPTIONS is handled by our custom OPTIONS function
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

export function OPTIONS() { // Changed to non-async as per Decoder Ring
  return new Response(null, { status: 204, headers: CORS_HEADERS });
}
