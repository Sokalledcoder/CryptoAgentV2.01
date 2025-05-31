from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import datetime

# Define the Pydantic models for the output schema
class _Meta(BaseModel):
    timestamp: str = Field(..., description="REQUIRED Placeholder for timestamp (YYYY-MM-DDTHH:MM:SSZ)")
    analyst: str = Field("orchestrator-v1", description="REQUIRED Analyst identifier")
    error: Optional[str] = Field(None, description="REQUIRED Error message if any, else null")

class FinalSignal(BaseModel):
    direction: Optional[str] = Field(None, description="Proposed trade direction (short, long, null)")
    entry: Optional[float] = Field(None, description="Proposed entry price")
    stopLoss: Optional[float] = Field(None, description="Proposed stop loss price")
    takeProfit: Optional[float] = Field(None, description="Proposed take profit price")
    winProbability: Optional[int] = Field(None, description="Heuristic win probability score (0-100)")
    timeframe: str = Field(..., description="REQUIRED Timeframe of the analysis")
    symbol: str = Field(..., description="REQUIRED Trading symbol (e.g., BTCUSDT)")
    confidence: Optional[str] = Field(None, description="Qualitative confidence tier (high, medium, low)")
    indicators: List[str] = Field([], description="List of key indicator states (e.g., Kalman, Derivatives, Sentiment)")
    patterns: List[str] = Field([], description="List of key structure and liquidity patterns")
    strategies: List[str] = Field([], description="List of applicable strategies identified")
    marketCondition: Optional[str] = Field(None, description="Overall market condition (trending, ranging, volatile)")
    entryConditions: List[str] = Field([], description="List of entry conditions from action plan")
    exitConditions: List[str] = Field([], description="List of invalidation triggers and scenario risks")
    fearAndGreedValue: Optional[int] = Field(None, description="Fear and Greed Index value")
    fearAndGreedRating: Optional[str] = Field(None, description="Fear and Greed Index rating")
    btcDominance: Optional[float] = Field(None, description="Bitcoin Dominance percentage")
    totalMarketCap: Optional[str] = Field(None, description="Total crypto market capitalization")
    notes: Optional[str] = Field(None, description="Overarching context, justifications, alternative scenarios, or residual sentiment/news details")
    meta: _Meta = Field(..., alias="_meta", description="REQUIRED Metadata about the analysis") # Renamed _meta to meta and added alias

from google.adk.agents import LlmAgent # Corrected import
import json

class FinalPackageAgent(LlmAgent): # Inherit from LlmAgent
    def __init__(self):
        super().__init__(
            model="gemini-2.5-flash-preview-05-20", # Added model
            name="FinalPackagerValidatorSummarizer",
            description="Assembles, validates, and summarizes the final technical analysis report from all previous agents.",
            output_schema=FinalSignal, # Added output_schema
            tools=[] # No external tools for this agent
        )

    async def run(self, context_from_previous_agents: Dict[str, Any]) -> str:
        # PLAN: Map inputs to FinalSignal fields, set meta, generate JSON, generate Summary,
        # construct final string WITH separator, verify schema.
        print("PLAN: Assembling final report from all agent outputs, validating schema, and generating summary.")
        print(f"Context from previous agents: {json.dumps(context_from_previous_agents, indent=2)}")

        # Simulate extracting data from all previous agents' outputs
        # In a real scenario, this would involve robust parsing and error handling
        
        # Extract data from context_from_previous_agents (simulated)
        context_output = context_from_previous_agents.get('step01_context', {})
        structure_output = context_from_previous_agents.get('step02_structure', {})
        ranges_output = context_from_previous_agents.get('step03_ranges', {})
        liquidity_output = context_from_previous_agents.get('step04_liquidity', {})
        momentum_output = context_from_previous_agents.get('step05_momentum', {})
        derivatives_output = context_from_previous_agents.get('step05b_derivatives', {})
        sentiment_output = context_from_previous_agents.get('step06_sentiment', {})
        news_output = context_from_previous_agents.get('step07_news', {})
        tradesetup_output = context_from_previous_agents.get('step08_tradesetup', {})
        confidencerisk_output = context_from_previous_agents.get('step09_confidencerisk', {})
        actionplan_output = context_from_previous_agents.get('step10_actionplan', {})

        # Populate FinalSignal fields
        final_signal_data = {
            "direction": tradesetup_output.get('direction'),
            "entry": tradesetup_output.get('entry'),
            "stopLoss": tradesetup_output.get('stop'),
            "takeProfit": tradesetup_output.get('take_profit'),
            "winProbability": confidencerisk_output.get('winProbability'),
            "timeframe": context_output.get('timeframe', '1H'), # Default for simulation
            "symbol": context_output.get('pair', 'BTCUSDT'), # Default for simulation
            "confidence": confidencerisk_output.get('confidence_tier'),
            "indicators": [],
            "patterns": [],
            "strategies": [],
            "marketCondition": "trending", # Simulated
            "entryConditions": [],
            "exitConditions": [],
            "fearAndGreedValue": sentiment_output.get('fear_greed_index', {}).get('value'),
            "fearAndGreedRating": sentiment_output.get('fear_greed_index', {}).get('rating'),
            "btcDominance": sentiment_output.get('global_market_data', {}).get('btc_dominance'),
            "totalMarketCap": sentiment_output.get('global_market_data', {}).get('total_market_cap_usd'),
            "notes": None,
            "meta": { # Renamed _meta to meta
                "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z'),
                "analyst": "orchestrator-v1",
                "error": None # Assume no error for now
            }
        }

        # Compile lists (simplifying for placeholder)
        if momentum_output and momentum_output.get('kalman_output', {}).get('state_description'):
            final_signal_data["indicators"].append(f"Kalman: {momentum_output['kalman_output']['state_description']}")
        if derivatives_output and derivatives_output.get('funding_rate_state'):
            final_signal_data["indicators"].append(f"Funding Rate: {derivatives_output['funding_rate_state']} ({derivatives_output.get('funding_rate_value', 'N/A')}%)")
        if sentiment_output and sentiment_output.get('fear_greed_index', {}).get('rating'):
            final_signal_data["indicators"].append(f"F&G Status: {sentiment_output['fear_greed_index']['rating']} ({sentiment_output['fear_greed_index']['value']})")
        if news_output and news_output.get('market_news_sentiment'):
            final_signal_data["indicators"].append(f"News Sentiment: Market {news_output['market_news_sentiment']}, Asset {news_output.get('asset_news_sentiment', 'N/A')}")

        if structure_output and structure_output.get('market_structure_trend'):
            final_signal_data["patterns"].append(f"Market Structure: {structure_output['market_structure_trend']}")
        if liquidity_output and liquidity_output.get('liquidity_zones'):
            final_signal_data["patterns"].append(f"Liquidity: {liquidity_output['liquidity_zones'][0].get('type', 'N/A')} at {liquidity_output['liquidity_zones'][0].get('price_level', 'N/A')}")

        if actionplan_output and actionplan_output.get('action_plan'):
            for step in actionplan_output['action_plan']:
                final_signal_data["entryConditions"].append(step['description'])
        if actionplan_output and actionplan_output.get('invalidation_triggers'):
            for trigger in actionplan_output['invalidation_triggers']:
                final_signal_data["exitConditions"].append(trigger['description'])
        
        # Add notes from various agents or for overall context
        notes_list = []
        if tradesetup_output.get('notes'):
            notes_list.append(f"Trade Setup Notes: {tradesetup_output['notes']}")
        if confidencerisk_output.get('notes'):
            notes_list.append(f"Confidence/Risk Notes: {confidencerisk_output['notes']}")
        if news_output.get('notes'):
            notes_list.append(f"News Notes: {news_output['notes']}")
        
        if notes_list:
            final_signal_data["notes"] = " | ".join(notes_list)

        # Create FinalSignal Pydantic model for validation
        final_signal = FinalSignal(**final_signal_data)
        json_output = json.dumps(final_signal.dict(exclude_none=True), indent=2)

        # Generate Markdown Summary
        summary_direction = final_signal.direction if final_signal.direction else "No clear direction"
        summary_symbol = final_signal.symbol
        summary_wp = final_signal.winProbability if final_signal.winProbability is not None else "N/A"
        summary_confidence = final_signal.confidence if final_signal.confidence else "N/A"
        summary_stop = final_signal.stopLoss if final_signal.stopLoss is not None else "N/A"
        
        summary_reason = "strong confluence of technical factors"
        if final_signal.direction == "long":
            summary_reason = "bullish market structure and liquidity support"
        elif final_signal.direction == "short":
            summary_reason = "bearish market structure and liquidity resistance"

        key_factors = []
        if final_signal.indicators:
            key_factors.append(f"Indicators: {', '.join(final_signal.indicators[:2])}") # Take top 2
        if final_signal.patterns:
            key_factors.append(f"Patterns: {', '.join(final_signal.patterns[:2])}") # Take top 2
        if final_signal.notes:
            key_factors.append(f"Additional Context: {final_signal.notes.split(' | ')[0]}") # Take first note

        summary_text = f"""Recommendation: {summary_direction.capitalize()} {summary_symbol} based on {summary_reason}.
Key Factors:
* {key_factors[0] if len(key_factors) > 0 else "N/A"}
* {key_factors[1] if len(key_factors) > 1 else "N/A"}
* Key Risk: {final_signal.exitConditions[0] if final_signal.exitConditions else "No specific risks identified."}. Win Probability: {summary_wp}%. Confidence: {summary_confidence}. Stop: {summary_stop}.
"""

        # REFLECTION: Confirm JSON assembled, sentiment/scenario info integrated, summary generated, separator ready.
        print("REFLECTION: FinalSignal JSON assembled and validated. Summary generated. Output string will include the mandatory separator.")

        # OUTPUT: Construct the single final output string
        return f"{json_output}\n--- SUMMARY ---\n{summary_text}"
