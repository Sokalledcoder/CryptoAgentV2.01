from dotenv import load_dotenv # Import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware # Added for CORS
import uvicorn

load_dotenv() # Load environment variables from .env file
import json 
import uuid
# from datetime import datetime, timezone # No longer needed here, CopilotKit Action handler will manage its own logic
# from sse_starlette.sse import EventSourceResponse # Will be replaced by CopilotKit SDK's streaming

# ADK Imports (needed for the Action handler)
from backend.agents import orchestrator_agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from backend.adk_message_types import create_simple_text_content

# CopilotKit Imports
from copilotkit import CopilotKitRemoteEndpoint, Action
from copilotkit.integrations.fastapi import add_fastapi_endpoint


app = FastAPI(
    title="CopilotKit FastAPI Backend for Crypto TA",
    description="Exposes ADK agents via CopilotKit for AG-UI compliant interaction.",
    version="0.2.0", # Version bump
)

# 1. Configure CORS Middleware
# Adjust origins as needed for development (Node.js runtime, React frontend) and production
allowed_origins = [
    "http://localhost:3000",  # Common port for Next.js dev server (CopilotKitRuntime)
    "http://localhost:5173",  # Common port for Vite React dev server
    # Add production frontend URL(s) here later
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Define CopilotKit Action Handler for ADK OrchestratorAgent
# Temporarily make it synchronous for extreme simplicity in testing dispatch
def adk_orchestrator_action_handler(query: str) -> dict: # Removed async
    print(f"--- SIMPLIFIED ACTION HANDLER --- Received query: {query}")
    # Return a simple dict; CopilotKit SDK should stream this as a result.
    return {"status": "success", "echo": query, "message": "This is a simplified test response."}

# 3. Define the CopilotKit Action
run_orchestrator_adk_action = Action(
    name="runCryptoTaOrchestrator", # This name is used by CopilotKit frontend/LLM
    description="Invokes the Crypto Technical Analysis Orchestrator agent with a user query.",
    handler=adk_orchestrator_action_handler,
    parameters=[
        {"name": "query", "type": "string", "description": "The user's query or instruction for the TA agent.", "required": True}
    ]
)

# 4. Create CopilotKitRemoteEndpoint instance
copilot_service = CopilotKitRemoteEndpoint(
    actions=[run_orchestrator_adk_action]
    # We can add more actions or agents here later
)

# 5. Add CopilotKit endpoint to the FastAPI application
# This will expose the AG-UI compliant endpoint at /copilotkit (or chosen path)
# Trying with all arguments as positional, matching the research:
# add_fastapi_endpoint(app_instance, sdk_instance, path_string)
add_fastapi_endpoint(
    app,                   # First positional: FastAPI app instance
    copilot_service,       # Second positional: CopilotKitRemoteEndpoint instance
    "/copilotkit"          # Third positional: path string
)

# (Optional) A root endpoint for basic health check
@app.get("/")
async def read_root():
    return {"message": "Crypto TA FastAPI Backend with CopilotKit is running!"}

# Comment out or remove the old SSE endpoint
# class OrchestratorInput(BaseModel):
#     query: str
# @app.post("/invoke-orchestrator/")
# async def invoke_orchestrator_sse(data: OrchestratorInput):
#     """
#     Receives a query, runs the OrchestratorAgent, and streams AG-UI events over SSE.
#     """
#     # ... (old implementation) ...
#     pass


if __name__ == "__main__":
    # Ensure uvicorn runs the 'app' instance from this 'main.py' file.
    # The command `python -m uvicorn backend.main:app --reload` from project root is preferred.
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
