from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

# Define the Pydantic models for the output schema
class ConfirmationFactor(BaseModel):
    factor_type: str = Field(..., description="Type of factor (structure, liquidity, range, momentum, derivatives, sentiment, news, macro, other)")
    description: str = Field(..., description="Description of the confirmation factor")
    strength: Optional[str] = Field(None, description="Strength of the factor (high, medium, low)")

class Scenario(BaseModel):
    type: str = Field(..., description="Type of scenario (alternative_bullish, alternative_bearish, invalidation_point, risk_factor)")
    description: str = Field(..., description="Description of the scenario or risk")
    implication: Optional[str] = Field(None, description="Implication of the scenario")

class Agent8_TradeSetup_Output(BaseModel):
    direction: Optional[str] = Field(None, description="Proposed trade direction (short, long, null)")
    entry: Optional[float] = Field(None, description="Proposed entry price")
    stop: Optional[float] = Field(None, description="Proposed stop loss price")
    take_profit: Optional[float] = Field(None, description="Proposed take profit price")
    confirmations: List[ConfirmationFactor] = Field([], description="List of confirmation factors")
    scenarios: List[Scenario] = Field([], description="List of alternative scenarios or risks")
    notes: Optional[str] = Field(None, description="Additional notes or observations")


from google.adk.agents import LlmAgent # Corrected import
from typing import Dict, Any

class TradeSetupAgent(LlmAgent): # Inherit from LlmAgent
    def __init__(self):
        super().__init__(
            model="gemini-2.5-flash-preview-05-20", # Added model
            name="TradeSetupSynthesizer",
            description="Synthesizes trade setups based on analysis from previous agents.",
            output_schema=Agent8_TradeSetup_Output # Added output_schema
        )

    async def run(self, context_from_previous_agents: Dict[str, Any]) -> Agent8_TradeSetup_Output:
        # PLAN: Review context including Agent 5b derivatives, apply weighting logic to identify confluence
        # for long/short or determine no setup, define levels, list prioritized confirmations including derivatives,
        # list scenarios/risks.
        print("PLAN: Reviewing context from Agents 1-7, including derivatives. Applying weighted synthesis to identify trade setup confluence. Defining levels, confirmations, and risks.")
        print(f"Context from previous agents: {json.dumps(context_from_previous_agents, indent=2)}")

        # Simulate weighted synthesis based on hypothetical strong bullish signals
        # In a real scenario, this would involve complex logic parsing the JSON outputs
        # from all preceding agents and applying the weighting rules.

        # Example of extracting hypothetical data from previous agents' outputs
        # (These keys would need to match the actual output schemas of the agents)
        # context_agent_output = context_from_previous_agents.get("step01_context", {})
        # structure_agent_output = context_from_previous_agents.get("step02_structure", {})
        # liquidity_agent_output = context_from_previous_agents.get("step04_liquidity", {})
        # momentum_agent_output = context_from_previous_agents.get("step05_momentum", {})
        # derivatives_agent_output = context_from_previous_agents.get("step05b_derivatives", {})
        # sentiment_agent_output = context_from_previous_agents.get("step06_sentiment", {})
        # news_agent_output = context_from_previous_agents.get("step07_news", {})

        # For demonstration, assume a strong bullish confluence
        proposed_direction = "long"
        proposed_entry = 70000.0
        proposed_stop = 69000.0
        proposed_take_profit = 72000.0

        confirmations = [
            ConfirmationFactor(factor_type="structure", description="Bullish market structure confirmed by higher lows and higher highs.", strength="high"),
            ConfirmationFactor(factor_type="liquidity", description="Price reacted strongly from a key demand zone/order block.", strength="high"),
            ConfirmationFactor(factor_type="momentum", description="Kalman and MOAK indicators show strong bullish momentum.", strength="medium"),
            ConfirmationFactor(factor_type="derivatives", description="Funding rate is positive and OI is rising with price, indicating healthy long interest.", strength="high"),
            ConfirmationFactor(factor_type="sentiment", description="Overall market sentiment is positive, supporting bullish moves.", strength="low"),
            ConfirmationFactor(factor_type="news", description="Recent asset-specific news is positive, supporting growth.", strength="low")
        ]

        scenarios = [
            Scenario(type="risk_factor", description="Invalidation if price breaks below 69000, indicating a shift in market structure.", implication="Potential for further downside to 68500."),
            Scenario(type="alternative_bearish", description="If bullish momentum fails, a retest of 69500 is possible before further downside.", implication="Could lead to a short setup if 69500 breaks.")
        ]

        notes = "Proposed long setup based on strong confluence from primary (structure, liquidity) and confirming (momentum, derivatives) factors. Secondary factors (sentiment, news) also align."

        # REFLECTION: State the proposed setup
        print(f"REFLECTION: Proposed {proposed_direction} setup based primarily on bullish structure and liquidity demand. Confirmed by strong momentum and positive derivatives signals (funding rate, OI).")

        # OUTPUT: Generate the Agent8_TradeSetup_Output JSON
        return Agent8_TradeSetup_Output(
            direction=proposed_direction,
            entry=proposed_entry,
            stop=proposed_stop,
            take_profit=proposed_take_profit,
            confirmations=confirmations,
            scenarios=scenarios,
            notes=notes
        )
