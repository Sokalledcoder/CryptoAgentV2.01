from google.adk.agents import LlmAgent
from google.adk.tools.agent_tool import AgentTool # Corrected import path
from backend.agents.context_agent import ContextAgent # Import the ContextAgent class
from backend.agents.structure_agent import StructureAgent # Import the StructureAgent class
from backend.agents.ranges_agent import RangesAgent # Import the RangesAgent class
from backend.agents.liquidity_agent import LiquidityAgent # Import the LiquidityAgent class
from backend.agents.sentiment_agent import SentimentAgent # Import the SentimentAgent class
from backend.agents.momentum_agent import MomentumAgent # Import the new MomentumAgent class
from backend.agents.derivatives_agent import DerivativesAgent # Import the new DerivativesAgent class
from backend.agents.news_agent import NewsAgent # Import the new NewsAgent class
from backend.agents.tradesetup_agent import TradeSetupAgent # Import the new TradeSetupAgent class
from backend.agents.confidencerisk_agent import ConfidenceRiskAgent # Import the new ConfidenceRiskAgent class
from backend.agents.actionplan_agent import ActionPlanAgent # Import the new ActionPlanAgent class
from backend.agents.finalpackage_agent import FinalPackageAgent # Import the new FinalPackageAgent class

# Wrap the specialized agents as tools
context_analysis_tool = AgentTool(
    agent=ContextAgent()
)

finalpackage_assembly_tool = AgentTool(
    agent=FinalPackageAgent()
)

actionplan_analysis_tool = AgentTool(
    agent=ActionPlanAgent()
)

confidencerisk_analysis_tool = AgentTool(
    agent=ConfidenceRiskAgent()
)

tradesetup_analysis_tool = AgentTool(
    agent=TradeSetupAgent()
)

news_analysis_tool = AgentTool(
    agent=NewsAgent()
)

structure_analysis_tool = AgentTool(
    agent=StructureAgent()
)

ranges_analysis_tool = AgentTool(
    agent=RangesAgent()
)

liquidity_analysis_tool = AgentTool(
    agent=LiquidityAgent()
)

momentum_analysis_tool = AgentTool(
    agent=MomentumAgent()
)

derivatives_analysis_tool = AgentTool(
    agent=DerivativesAgent()
)

sentiment_analysis_tool = AgentTool(
    agent=SentimentAgent()
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
5. FIFTH: Use 'analyze_momentum_volume' tool to analyze momentum and volume indicators
6. SIXTH: Use 'analyze_derivatives_data' tool to analyze derivatives indicators
7. SEVENTH: Use 'analyze_news_sentiment' tool to research news and analyze sentiment
8. EIGHTH: Use 'synthesize_trade_setup' tool to propose a trade setup
9. NINTH: Use 'assess_confidence_risk' tool to assess confidence and risk for the trade setup
10. TENTH: Use 'define_action_plan' tool to define action plan steps and invalidation triggers
11. ELEVENTH: Use 'assemble_final_package' tool to assemble the final analysis report and summary
12. TWELFTH: Use 'analyze_sentiment_macro' tool to get sentiment and macro data

Pass the user's input to each tool. Each tool will return a JSON result.

After ALL tools have been called, compile their results into a comprehensive analysis report.
Present the final output as a structured JSON containing all the analysis results.

Your final output should be a JSON object with the following structure:
{
  "step01_context": <result from context tool>,
  "step02_structure": <result from structure tool>,
  "step03_ranges": <result from ranges tool>,
  "step04_liquidity": <result from liquidity tool>,
  "step05_momentum": <result from momentum tool>,
  "step05b_derivatives": <result from derivatives tool>,
  "step07_news": <result from news tool>,
  "step08_tradesetup": <result from tradesetup tool>,
  "step09_confidencerisk": <result from confidencerisk tool>,
  "step10_actionplan": <result from actionplan tool>,
  "step11_finalpackage": <result from finalpackage tool>,
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
        momentum_analysis_tool,
        derivatives_analysis_tool,
        news_analysis_tool,
        tradesetup_analysis_tool,
        confidencerisk_analysis_tool,
        actionplan_analysis_tool,
        finalpackage_assembly_tool, # Added finalpackage tool
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
