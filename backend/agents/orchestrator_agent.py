from google.adk.agents import LlmAgent
from google.adk.tools.agent_tool import AgentTool # Corrected import path
from backend.agents.context_agent import root_agent as context_agent_instance
from backend.agents.structure_agent import root_agent as structure_agent_instance
from backend.agents.ranges_agent import root_agent as ranges_agent_instance
from backend.agents.liquidity_agent import root_agent as liquidity_agent_instance
from backend.agents.sentiment_agent import root_agent as sentiment_agent_instance

# Wrap the specialized agents as tools
context_analysis_tool = AgentTool(
    agent=context_agent_instance
)

structure_analysis_tool = AgentTool(
    agent=structure_agent_instance
)

ranges_analysis_tool = AgentTool(
    agent=ranges_agent_instance
)

liquidity_analysis_tool = AgentTool(
    agent=liquidity_agent_instance
)

sentiment_analysis_tool = AgentTool(
    agent=sentiment_agent_instance
)

ORCHESTRATOR_INSTRUCTION = """
You are an Orchestrator Agent for a cryptocurrency technical analysis system.
Your primary role is to manage the workflow by calling specialized agents in sequence.

When you receive input (which should include chart information or a user request), 
you MUST execute the following workflow:

1. FIRST: Use 'analyze_chart_context' tool to get initial chart context and price data
2. SECOND: Use 'analyze_market_structure' tool to analyze market structure and Monday Range
3. THIRD: Use 'analyze_predictive_ranges' tool to analyze LuxAlgo Predictive Ranges
4. FOURTH: Use 'analyze_liquidity_orderflow' tool to analyze liquidity zones and order flow
5. FIFTH: Use 'analyze_sentiment_macro' tool to get sentiment and macro data

Pass the user's input to each tool. Each tool will return a JSON result.

After ALL tools have been called, compile their results into a comprehensive analysis report.
Present the final output as a structured JSON containing all the analysis results.

Your final output should be a JSON object with the following structure:
{
  "step01_context": <result from context tool>,
  "step02_structure": <result from structure tool>,
  "step03_ranges": <result from ranges tool>,
  "step04_liquidity": <result from liquidity tool>,
  "step06_sentiment": <result from sentiment tool>,
  "analysis_summary": "Brief summary of key findings across all steps"
}
"""

root_agent = LlmAgent(
    model="gemini-2.5-flash-preview-05-20", # Using the same model for consistency for now
    name="orchestrator_agent",
    description="Orchestrates calls to specialized TA agents in sequence for comprehensive analysis.",
    instruction=ORCHESTRATOR_INSTRUCTION,
    tools=[
        context_analysis_tool,
        structure_analysis_tool,
        ranges_analysis_tool,
        liquidity_analysis_tool,
        sentiment_analysis_tool
    ]
)

# To test this agent with adk web:
# 1. In backend/agents/__init__.py, expose this agent:
#    from .orchestrator_agent import root_agent as orchestrator_agent
# 2. (Temporarily) In backend/__init__.py, change the main root_agent to be this orchestrator_agent:
#    from .agents import orchestrator_agent as root_agent
# 3. Run `adk web` and select the 'backend' app.
# 4. Input: "Analyze chart: BTCUSDT 1H, image_url: fake.png"
