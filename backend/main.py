from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles # For serving uploaded images if needed
import uvicorn
import os
import shutil
import uuid
import json
import asyncio # For asyncio.sleep
import datetime # For timestamp in logger

load_dotenv()  # Load environment variables from .env file

# ADK Imports (needed for the Action handler)
from backend.agents import orchestrator_agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from backend.adk_message_types import create_simple_text_content

# CopilotKit Imports
from copilotkit import CopilotKitRemoteEndpoint, Action
from copilotkit.integrations.fastapi import add_fastapi_endpoint

# --- Configuration for Image Uploads ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # c:/Users/Soka/Desktop/CryptoAgentV2.01/backend
PROJECT_ROOT = os.path.dirname(BASE_DIR) # c:/Users/Soka/Desktop/CryptoAgentV2.01
UPLOAD_DIR_NAME = "uploaded_charts"
UPLOAD_DIR = os.path.join(PROJECT_ROOT, "workspaces", UPLOAD_DIR_NAME)

# Ensure upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)
# --- End Configuration for Image Uploads ---


# Initialize ADK Runner and Session Service globally
session_service = InMemorySessionService()
adk_runner = Runner(agent=orchestrator_agent.root_agent, session_service=session_service, app_name="crypto_ta_backend")


app = FastAPI(
    title="CopilotKit FastAPI Backend for Crypto TA",
    description="Exposes ADK agents via CopilotKit for AG-UI compliant interaction. Includes image upload.",
    version="0.2.5", # Version bump for image upload feature
)

# Mount static files directory to serve uploaded images (optional, if file:/// URLs don't work for ADK/Gemini)
# app.mount(f"/static/{UPLOAD_DIR_NAME}", StaticFiles(directory=UPLOAD_DIR), name="uploaded_charts")


# Middleware to log incoming request body for /copilotkit paths
@app.middleware("http")
async def action_logger_middleware(request: Request, call_next):
    request_to_pass_on = request
    if request.method == "POST" and request.url.path.startswith("/copilotkit"):
        print(f"🔥 RAW body logging for {request.method} {request.url.path} @ {datetime.datetime.now()}")
        raw_body_bytes = await request.body()
        try:
            decoded_body = raw_body_bytes.decode()
            print(f"   Raw body content (first 500 chars): {decoded_body[:500]}{'...' if len(decoded_body) > 500 else ''}")
            parsed_json = json.loads(decoded_body)
            print(f"   Parsed JSON body: {json.dumps(parsed_json, indent=2)}")
        except Exception as e:
            print(f"   Raw body content (could not parse as JSON or other error): {raw_body_bytes.decode()[:500]}... Error: {e}")
        async def new_receive():
            return {"type": "http.request", "body": raw_body_bytes, "more_body": False}
        request_to_pass_on = Request(scope=request.scope, receive=new_receive)
    response = await call_next(request_to_pass_on)
    return response

# 1. Configure CORS Middleware
allowed_origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:5173",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Image Upload Endpoint ---
@app.post("/upload-chart-image/")
async def upload_chart_image(file: UploadFile = File(...)):
    try:
        # Ensure UPLOAD_DIR exists (double check, though done at startup)
        os.makedirs(UPLOAD_DIR, exist_ok=True)

        # Sanitize filename and create a unique name
        original_filename = file.filename if file.filename else "unknown_image"
        safe_filename = "".join(c if c.isalnum() or c in ['.', '_'] else '_' for c in original_filename)
        unique_filename = f"{uuid.uuid4().hex[:8]}_{safe_filename}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Generate file URL (file:// scheme for local access by ADK/Gemini if supported)
        # Convert to absolute path and ensure correct slashes for file URI
        abs_file_path = os.path.abspath(file_path)
        file_url = f"file:///{abs_file_path.replace(os.sep, '/')}"
        
        # Alternative: HTTP URL if StaticFiles is mounted and preferred
        # http_file_url = f"{request.base_url}static/{UPLOAD_DIR_NAME}/{unique_filename}"

        return {
            "filename": unique_filename,
            "content_type": file.content_type,
            "file_path": file_path, # Absolute local path
            "file_url": file_url    # file:/// URL
            # "http_file_url": http_file_url # If serving statically
        }
    except Exception as e:
        print(f"Error during image upload: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": f"Image upload failed: {str(e)}"}
# --- End Image Upload Endpoint ---


# 2. Define CopilotKit Action Handler for ADK OrchestratorAgent
async def adk_orchestrator_action_handler(**kwargs) -> dict:
    print(f"✅ HANDLER adk_orchestrator_action_handler reached with kwargs: {kwargs}")
    
    user_query = kwargs.get('query', None)
    image_url = kwargs.get('image_url', None) # New parameter
    
    if user_query is None:
        print("Warning: 'query' key not found in kwargs.")
        return {"status": "error", "message": "No query parameter provided in arguments"}
    
    # Construct the input for the ADK agent, including image_url if present
    # The ContextAgent prompt expects: "A chart-image URL plus the orchestrator’s text context."
    if image_url:
        full_query_to_adk = f"Chart Image URL: {image_url}. User Query: {user_query}"
    else:
        full_query_to_adk = user_query
    
    print(f"Processing full query for ADK: '{full_query_to_adk}'")

    try:
        print("Attempting to run ADK Orchestrator Agent...")
        content = create_simple_text_content(full_query_to_adk, role="user")
        print(f"ADK Runner: Invoking run_async with content: {content}")

        adk_results = []
        session_id = f"crypto_session_{uuid.uuid4().hex[:8]}"
        user_id    = "crypto_user"
        # Use the app_name consistent with the Runner's initialization
        # The Runner is initialized with app_name="crypto_ta_backend"
        app_name   = adk_runner.app_name  # This should be "crypto_ta_backend"

        print(f"--- Pre-creating session for ADK Runner (using await, simplified) ---")
        print(f"Attempting to create session with: app_name='{app_name}', user_id='{user_id}', session_id='{session_id}'")
        
        # ✅  async call *must* be awaited
        # We assume session_id from uuid.uuid4() is unique for each new request,
        # so "Session already exists" ValueError is highly unlikely and can be omitted for brevity here.
        # If it occurs, it would propagate as an unhandled error, which is acceptable for now.
        await session_service.create_session(
            app_name=app_name,
            user_id=user_id,
            session_id=session_id,
        )
        print(f"Successfully pre-created session {session_id}.")
            
        print(f"ADK Runner: Invoking run_async with session_id='{session_id}', user_id='{user_id}'.")
        async for adk_event in adk_runner.run_async(new_message=content, user_id=user_id, session_id=session_id):
            print(f"ADK Event: {adk_event}")
            if hasattr(adk_event, '__dict__'):
                event_dict = {}
                for key, value in adk_event.__dict__.items():
                    try:
                        json.dumps(value)
                        event_dict[key] = value
                    except (TypeError, ValueError):
                        event_dict[key] = str(value)
                adk_results.append(event_dict)
            else:
                adk_results.append(str(adk_event))
        
        final_result = {
            "status": "success",
            "message": "Crypto TA analysis completed successfully",
            "original_query": user_query,
            "image_url_provided": image_url,
            "full_query_to_adk": full_query_to_adk,
            "adk_events": adk_results,
            "analysis_summary": "Multi-agent crypto analysis executed with all 12 specialized agents"
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
    description="Invokes the Crypto Technical Analysis Orchestrator agent with a user query and an optional image URL.",
    handler=adk_orchestrator_action_handler,
    parameters=[
        {
            "name": "query", 
            "type": "string", 
            "description": "The user's query or instruction for the TA agent.", 
            "required": True
        },
        {
            "name": "image_url", # New parameter for image URL
            "type": "string",
            "description": "Optional URL of the chart image to be analyzed. Should be obtained from the /upload-chart-image/ endpoint.",
            "required": False
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
async def test_handler_directly_endpoint(request: Request):
    print("--- DEBUG ENDPOINT (/debug/test-handler) CALLED ---")
    # Example: receive JSON body with query and optional image_url
    try:
        body = await request.json()
        test_query = body.get("query", "Test query from debug endpoint")
        test_image_url = body.get("image_url", None) # e.g., "file:///path/to/your/test_image.png"
        
        test_kwargs = {"query": test_query, "image_url": test_image_url}
        
        result = await adk_orchestrator_action_handler(**test_kwargs)
        print(f"Debug endpoint result: {json.dumps(result, indent=2)}")
        return {"status": "success", "debug_handler_result": result}
    except Exception as e:
        print(f"Error in debug endpoint: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": f"Debug endpoint error: {str(e)}"}

if __name__ == "__main__":
    # Ensure UPLOAD_DIR exists when running directly (also done at top level)
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    print(f"Serving from: {os.getcwd()}")
    print(f"Upload directory configured at: {os.path.abspath(UPLOAD_DIR)}")
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True) # Changed "main:app" to "backend.main:app"
