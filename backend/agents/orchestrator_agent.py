from google.adk.agents import LlmAgent
from google.adk.tools.agent_tool import AgentTool # Corrected import path
from backend.agents import context_agent as context_agent_instance # Import from backend.agents module

# Wrap the ContextAgent (imported as context_agent_instance) as a tool
# The name of the tool should be descriptive for the OrchestratorAgent's LLM.
# The description should guide the LLM on when to use this tool.
context_analysis_tool = AgentTool(
    agent=context_agent_instance # Removed description argument
    # input_schema can often be inferred if the target agent has a clear input structure,
    # or can be explicitly defined if needed. For now, we'll let it be inferred or rely on
    # the Orchestrator's ability to pass a string input.
)

ORCHESTRATOR_INSTRUCTION = """
You are an Orchestrator Agent for a cryptocurrency technical analysis system.
Your primary role is to manage the workflow by calling specialized agents.

For the initial step, when you receive input (which should include chart information or a user request),
you MUST use the 'analyze_chart_context' tool to get the initial analysis from the ContextAgent.
Pass the user's input directly to this tool.

After the 'analyze_chart_context' tool returns its JSON result, present this JSON result as your final output.
Ensure your entire output is ONLY the JSON received from the tool.
"""

root_agent = LlmAgent(
    model="gemini-2.5-flash-preview-05-20", # Using the same model for consistency for now
    name="orchestrator_agent",
    description="Orchestrates calls to specialized TA agents. Starts with ContextAgent.",
    instruction=ORCHESTRATOR_INSTRUCTION,
    tools=[context_analysis_tool]
)

# To test this agent with adk web:
# 1. In backend/agents/__init__.py, expose this agent:
#    from .orchestrator_agent import root_agent as orchestrator_agent
# 2. (Temporarily) In backend/__init__.py, change the main root_agent to be this orchestrator_agent:
#    from .agents import orchestrator_agent as root_agent
# 3. Run `adk web` and select the 'backend' app.
# 4. Input: "Analyze chart: BTCUSDT 1H, image_url: fake.png"
