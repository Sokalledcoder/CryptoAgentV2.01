from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

load_dotenv()  # Load environment variables from .env file
import json 
import uuid
import asyncio # For asyncio.sleep
import datetime # For timestamp in logger

# ADK Imports (needed for the Action handler)
from backend.agents import orchestrator_agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from backend.adk_message_types import create_simple_text_content

# CopilotKit Imports
from copilotkit import CopilotKitRemoteEndpoint, Action
from copilotkit.integrations.fastapi import add_fastapi_endpoint

# For diagnostic logging middleware
from fastapi import Request

app = FastAPI(
    title="CopilotKit FastAPI Backend for Crypto TA",
    description="Exposes ADK agents via CopilotKit for AG-UI compliant interaction.",
    version="0.2.3", # Version bump
)

# Middleware to log incoming request body for /copilotkit paths
@app.middleware("http")
async def action_logger_middleware(request: Request, call_next):
    # Default to original request for call_next
    request_to_pass_on = request 

    if request.method == "POST" and request.url.path.startswith("/copilotkit"):
        print(f"🔥 RAW body logging for {request.method} {request.url.path} @ {datetime.datetime.now()}")
        raw_body_bytes = await request.body() # Consume the body once
        
        # Log the raw body (or a snippet)
        try:
            decoded_body = raw_body_bytes.decode()
            print(f"   Raw body content (first 500 chars): {decoded_body[:500]}{'...' if len(decoded_body) > 500 else ''}")
            # Attempt to parse and pretty-print if JSON, for better readability
            parsed_json = json.loads(decoded_body)
            print(f"   Parsed JSON body: {json.dumps(parsed_json, indent=2)}")
        except Exception as e:
            print(f"   Raw body content (could not parse as JSON or other error): {raw_body_bytes.decode()[:500]}... Error: {e}")

        # Define a new 'receive' awaitable that will yield the already-read body
        async def new_receive():
            return {"type": "http.request", "body": raw_body_bytes, "more_body": False}
        
        # Create a new Request object that uses our 'new_receive'
        # This allows downstream handlers to call request.body() again if needed,
        # and they will get the body we've already read.
        request_to_pass_on = Request(scope=request.scope, receive=new_receive)
    
    response = await call_next(request_to_pass_on)
    return response

# 1. Configure CORS Middleware
allowed_origins = [
    "http://localhost:3000",  # Next.js runtime
    "http://localhost:3001",  # Alternative Next.js port
    "http://localhost:5173",  # Vite React dev server
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Define CopilotKit Action Handler for ADK OrchestratorAgent (Streaming)
async def adk_orchestrator_action_handler(**kwargs): # Removed -> dict, as it's an async generator
    """
    CopilotKit Action handler that receives parameters as keyword arguments.
    Yields a streaming response.
    """
    print(f"✅ HANDLER adk_orchestrator_action_handler reached with kwargs: {kwargs}")
    
    query = kwargs.get('query', None) # Use None to distinguish missing key from empty string
    
    if query is None: # Check if 'query' key was actually missing
        print("Warning: 'query' key not found in kwargs.")
        yield {"event": "copilotkit_error", "data": {"status": "error", "message": "No query parameter provided in arguments"}}
        return
    
    print(f"Processing query: '{query}'")

    try:
        # Simulate streaming response
        yield {"event": "copilotkit_stream_start", "data": {"status": "starting_simple_stream", "query_received": query}}
        await asyncio.sleep(0.1) 

        yield {"event": "copilotkit_chunk", "data": {"chunk_id": 1, "content": f"Streaming response for: '{query}' - Part 1..."}}
        await asyncio.sleep(0.1)

        yield {"event": "copilotkit_chunk", "data": {"chunk_id": 2, "content": "Streaming response - Part 2. Almost done."}}
        await asyncio.sleep(0.1)
        
        final_result_data = {
            "status": "success",
            "final_message": "Simplified stream completed successfully.",
            "echoed_query": query,
            "example_data": { "pair": "BTCUSDT", "timeframe": "1H", "current_price_estimate": 45000.00 }
        }
        yield {"event": "copilotkit_result", "data": final_result_data }
        print(f"✅ HANDLER finished yielding. Final result data: {json.dumps(final_result_data, indent=2)}")

        # TODO: Replace above with actual ADK orchestrator logic and streaming.
        # Example of how ADK streaming might be integrated:
        # """
        # print("Attempting to run ADK Orchestrator Agent...")
        # session_service = InMemorySessionService()
        # runner = Runner(agent=orchestrator_agent, session_service=session_service)
        # content = create_simple_text_content(query, role="user")
        # print(f"ADK Runner: Invoking run_async with content: {content}")
        #
        # async for adk_event in runner.run_async(new_message=content):
        #     print(f"ADK Event: {adk_event}")
        #     # Adapt adk_event to CopilotKit's expected chunk/event structure
        #     # This might involve checking adk_event.type, adk_event.data, etc.
        #     # For example, if adk_event has a 'text' attribute:
        #     if hasattr(adk_event, 'text') and adk_event.text:
        #         yield {"event": "copilotkit_chunk", "data": {"content": adk_event.text}}
        #     # Or if it's a more complex object, map its fields appropriately.
        #     # You might also need to yield 'copilotkit_stream_start' and 'copilotkit_result'
        #     # based on the ADK agent's lifecycle.
        # """
        
    except Exception as e:
        print(f"!!! ERROR IN ACTION HANDLER adk_orchestrator_action_handler !!!: {e}")
        import traceback
        traceback.print_exc()
        yield {"event": "copilotkit_error", "data": {"status": "error", "message": f"Handler error: {str(e)}"}}

# 3. Define the CopilotKit Action
run_orchestrator_adk_action = Action(
    name="runCryptoTaOrchestrator",
    description="Invokes the Crypto Technical Analysis Orchestrator agent with a user query.",
    handler=adk_orchestrator_action_handler, # Async generator
    parameters=[
        {
            "name": "query", 
            "type": "string", 
            "description": "The user's query or instruction for the TA agent.", 
            "required": True
        }
    ]
)

# 4. Create CopilotKitRemoteEndpoint instance
copilot_service = CopilotKitRemoteEndpoint(
    actions=[run_orchestrator_adk_action]
)

# 5. Add CopilotKit endpoint to the FastAPI application
add_fastapi_endpoint(
    app,
    copilot_service,
    "/copilotkit"
)

# Health check endpoint
@app.get("/")
async def read_root():
    return {"message": "Crypto TA FastAPI Backend with CopilotKit is running!"}

# Debug endpoint to test the action handler directly
@app.post("/debug/test-handler")
async def test_handler_directly_endpoint():
    print("--- DEBUG ENDPOINT (/debug/test-handler) CALLED ---")
    test_kwargs = {"query": "Test query from debug endpoint"}
    
    results = []
    try:
        async for item in adk_orchestrator_action_handler(**test_kwargs):
            results.append(item)
        print(f"Debug endpoint collected results: {json.dumps(results, indent=2)}")
        return {"status": "success", "debug_handler_streamed_results": results}
    except Exception as e:
        print(f"Error in debug endpoint calling streaming handler: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": f"Debug endpoint error: {str(e)}", "collected_results_before_error": results}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
