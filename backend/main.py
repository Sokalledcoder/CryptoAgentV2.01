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

# Initialize ADK Runner and Session Service globally
# This ensures they are created once and reused across requests
session_service = InMemorySessionService()
adk_runner = Runner(agent=orchestrator_agent, session_service=session_service, app_name="crypto_ta_backend")

# For diagnostic logging middleware
from fastapi import Request

app = FastAPI(
    title="CopilotKit FastAPI Backend for Crypto TA",
    description="Exposes ADK agents via CopilotKit for AG-UI compliant interaction.",
    version="0.2.4", # Version bump
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

# 2. Define CopilotKit Action Handler for ADK OrchestratorAgent
async def adk_orchestrator_action_handler(**kwargs) -> dict:
    """
    CopilotKit Action handler that receives parameters as keyword arguments.
    Returns a dictionary response (not streaming for now to avoid serialization issues).
    """
    print(f"✅ HANDLER adk_orchestrator_action_handler reached with kwargs: {kwargs}")
    
    query = kwargs.get('query', None)
    
    if query is None:
        print("Warning: 'query' key not found in kwargs.")
        return {"status": "error", "message": "No query parameter provided in arguments"}
    
    print(f"Processing query: '{query}'")

    try:
        print("Attempting to run ADK Orchestrator Agent...")
        content = create_simple_text_content(query, role="user")
        print(f"ADK Runner: Invoking run_async with content: {content}")

        # Collect all ADK events into a result
        adk_results = []
        # Generate unique session ID for each request
        session_id = f"crypto_session_{uuid.uuid4().hex[:8]}"
        user_id = "crypto_user"
        
        # Use the globally defined adk_runner
        async for adk_event in adk_runner.run_async(new_message=content, user_id=user_id, session_id=session_id):
            print(f"ADK Event: {adk_event}")
            # Convert ADK event to serializable format
            if hasattr(adk_event, '__dict__'):
                event_dict = {}
                for key, value in adk_event.__dict__.items():
                    try:
                        # Test if value is JSON serializable
                        json.dumps(value)
                        event_dict[key] = value
                    except (TypeError, ValueError):
                        # If not serializable, convert to string
                        event_dict[key] = str(value)
                adk_results.append(event_dict)
            else:
                adk_results.append(str(adk_event))
        
        final_result = {
            "status": "success",
            "message": "Crypto TA analysis completed successfully",
            "query": query,
            "adk_events": adk_results,
            "analysis_summary": "Multi-agent crypto analysis executed with all 12 specialized agents" # Updated summary
        }
        
        print(f"✅ HANDLER finished. Final result: {json.dumps(final_result, indent=2)}")
        return final_result
        
    except Exception as e:
        print(f"!!! ERROR IN ACTION HANDLER adk_orchestrator_action_handler !!!: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": f"Handler error: {str(e)}"}

# 3. Define the CopilotKit Action
run_orchestrator_adk_action = Action(
    name="runCryptoTaOrchestrator",
    description="Invokes the Crypto Technical Analysis Orchestrator agent with a user query.",
    handler=adk_orchestrator_action_handler, # Now returns dict instead of async generator
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
    
    try:
        result = await adk_orchestrator_action_handler(**test_kwargs)
        print(f"Debug endpoint result: {json.dumps(result, indent=2)}")
        return {"status": "success", "debug_handler_result": result}
    except Exception as e:
        print(f"Error in debug endpoint calling handler: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": f"Debug endpoint error: {str(e)}"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
