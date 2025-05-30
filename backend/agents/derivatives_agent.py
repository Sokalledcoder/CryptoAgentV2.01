from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

# Define the Pydantic models for the output schema
class OISpecificSignals(BaseModel):
    trapped_traders: Optional[str] = Field(None, description="Potential trapped longs or shorts")
    stop_hunt_risk: Optional[str] = Field(None, description="Potential long or short stop hunt risk")
    failed_auction: Optional[bool] = Field(None, description="Flag for failed auction signal")

class LiquidationEvent(BaseModel):
    type: Optional[str] = Field(None, description="Type of liquidation (long or short)")
    level: Optional[float] = Field(None, description="Approximate price level of liquidation")
    size: Optional[str] = Field(None, description="Size of liquidation (small, medium, large, significant)")
    timestamp_description: Optional[str] = Field(None, description="Description of when the liquidation occurred")

class CVDAnalysis(BaseModel):
    trend: Optional[str] = Field(None, description="Trend of Cumulative Volume Delta (rising, falling, flat)")
    interpretation: Optional[str] = Field(None, description="Interpretation of CVD trend relative to price")

class Agent5b_Derivatives_Output(BaseModel):
    open_interest_value: Optional[float] = Field(None, description="Estimated Open Interest value if clear, else null")
    open_interest_trend_raw: Optional[str] = Field(None, description="Raw trend of Open Interest (rising, falling, flat, unclear)")
    oi_price_interpretation: Optional[str] = Field(None, description="Interpretation of Open Interest relative to price")
    oi_specific_signals: Optional[OISpecificSignals] = Field(None, description="Specific Open Interest signals")
    recent_liquidations: List[LiquidationEvent] = Field([], description="List of recent liquidation events")
    funding_rate_value: Optional[float] = Field(None, description="Estimated Funding Rate value if clear, else null")
    funding_rate_state: Optional[str] = Field(None, description="Funding Rate state based on RAG thresholds")
    funding_rate_trend: Optional[str] = Field(None, description="Trend of Funding Rate (rising, falling, flat, volatile)")
    cvd_value: Optional[float] = Field(None, description="Estimated Cumulative Volume Delta value if clear, else null")
    cvd_analysis: Optional[CVDAnalysis] = Field(None, description="Cumulative Volume Delta analysis")
    overall_interpretation: Optional[str] = Field(None, description="Overall interpretation of derivatives data")
    divergence_flag_oi: Optional[bool] = Field(None, description="Flag for divergence between Price and Open Interest")
    divergence_flag_cvd: Optional[bool] = Field(None, description="Flag for divergence between Price and Cumulative Volume Delta")
    notes: Optional[str] = Field(None, description="Additional notes or observations")

from google.adk.agent import Agent
from google.adk.agent_tool import AgentTool
from google.adk.side_effects import ToolCode
import json

# Placeholder for a simulated FileSearchTool
class FileSearchTool:
    def __init__(self, vector_store_id: str):
        self.vector_store_id = vector_store_id

    def search(self, query: str) -> str:
        if "Funding Rate thresholds" in query:
            return "Funding Rate Thresholds (from Trading Reference Checklist): Very Bullish (>0.02%), Bullish (0.005% to 0.02%), Neutral (-0.005% to 0.005%), Bearish (-0.02% to -0.005%), Very Bearish (<-0.02%)."
        elif "Open Interest relative to Price" in query:
            return "Open Interest (OI) relative to Price: Rising OI with rising price = healthy uptrend. Falling OI with rising price = potential short squeeze/weak uptrend. Rising OI with falling price = healthy downtrend. Falling OI with falling price = potential long squeeze/weak downtrend."
        elif "Cumulative Volume Delta relative to Price" in query:
            return "Cumulative Volume Delta (CVD) relative to Price: Rising CVD with rising price = strong buying pressure. Falling CVD with falling price = strong selling pressure. Divergence (e.g., rising price but falling CVD) indicates potential weakness."
        elif "Trapped Traders/Stop Hunts" in query:
            return "Trapped Traders/Stop Hunts: Trapped longs occur when price breaks support after an uptrend, trapping buyers. Trapped shorts occur when price breaks resistance after a downtrend, trapping sellers. Stop hunts are rapid price movements to trigger stop losses, often followed by reversal."
        else:
            return "No specific documentation found for the query."

class DerivativesAgent(Agent):
    def __init__(self):
        super().__init__(
            name="DerivativesAnalyzer",
            description="Analyzes Open Interest, Liquidations, Funding Rate, and Cumulative Volume Delta from chart subplots using RAG context.",
            output_model=Agent5b_Derivatives_Output,
            tools=[
                AgentTool(
                    name="FileSearchTool",
                    description="Tool for searching documentation in a vector store.",
                    tool_code=ToolCode.from_callable(FileSearchTool(vector_store_id="vs_derivatives_rag").search),
                    parameters={
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "The search query for the documentation."}
                        },
                        "required": ["query"]
                    }
                )
            ]
        )

    async def run(self, chart_image_url: str, context_from_previous_agents: Dict[str, Any]) -> Agent5b_Derivatives_Output:
        # PLAN: Query RAG for checklist rules including exact FR thresholds; locate OI, FR, Liq, CVD subplots;
        # visually analyze trends/states/values within each subplot; correlate OI/CVD trends with the Price panel trend;
        # apply RAG rules strictly, especially for FR state; check divergences/specific signals; synthesize; reflect; output JSON.
        print("PLAN: Querying RAG for derivatives interpretation rules, then visually analyzing chart subplots for OI, Liq, FR, CVD. Correlating with price action and applying strict RAG rules, especially for Funding Rate thresholds. Preparing structured JSON output.")

        # EXECUTE RAG & ANALYSIS:
        file_search_tool = FileSearchTool(vector_store_id="vs_derivatives_rag")

        rag_rules = file_search_tool.search("Provide the interpretation rules for Open Interest relative to Price, exact Funding Rate thresholds and their corresponding states (e.g., >0.04% = Very Bearish), Cumulative Volume Delta relative to Price, and Trapped Traders/Stop Hunts from the Trading Reference Checklist document.")
        print(f"RAG Output - Derivatives Rules: {rag_rules}")

        # Placeholder for visual analysis of the chart_image_url and its subplots
        print(f"Visual analysis of chart_image_url: {chart_image_url} and its subplots would occur here.")
        print(f"Context from previous agents: {json.dumps(context_from_previous_agents, indent=2)}")

        # REFLECTION: Briefly summarize key applicable RAG rules.
        # State findings for OI (value?, trend, OI+Price interpretation), Liqs, FR (value?, state strictly based on RAG thresholds, trend),
        # CVD (value?, trend, CVD+Price interpretation), and any specific OI signals. Note divergences. State overall interpretation.
        print("REFLECTION: Based on RAG, Funding Rate thresholds are critical for sentiment. OI and CVD trends must be correlated with price for accurate interpretation. Liquidations indicate market exhaustion or stop hunts.")
        print("Visual analysis (simulated): Assuming a slightly positive funding rate, rising OI with rising price, and CVD confirming buying pressure.")

        # OUTPUT: Generate the final JSON based on reflection, conforming strictly to Agent5b_Derivatives_Output schema.
        # Apply funding rate state thresholds exactly as defined in the RAG checklist.
        # Set numerical fields to `null` if not clearly legible.
        # Note interpretation difficulties if any.
        
        # Simulate applying FR thresholds based on a dummy value
        simulated_fr_value = 0.015 # Example: 0.015%
        funding_rate_state = "unclear"
        if simulated_fr_value > 0.02:
            funding_rate_state = "very_bullish"
        elif 0.005 <= simulated_fr_value <= 0.02:
            funding_rate_state = "bullish"
        elif -0.005 <= simulated_fr_value < 0.005:
            funding_rate_state = "neutral"
        elif -0.02 <= simulated_fr_value < -0.005:
            funding_rate_state = "bearish"
        elif simulated_fr_value < -0.02:
            funding_rate_state = "very_bearish"

        return Agent5b_Derivatives_Output(
            open_interest_value=None,
            open_interest_trend_raw="rising",
            oi_price_interpretation="healthy_uptrend",
            oi_specific_signals=OISpecificSignals(
                trapped_traders=None,
                stop_hunt_risk=None,
                failed_auction=False
            ),
            recent_liquidations=[
                LiquidationEvent(type="short", level=None, size="small", timestamp_description="recent")
            ],
            funding_rate_value=simulated_fr_value,
            funding_rate_state=funding_rate_state,
            funding_rate_trend="flat",
            cvd_value=None,
            cvd_analysis=CVDAnalysis(
                trend="rising",
                interpretation="Healthy bullish momentum, CVD confirming buying pressure (simulated visual correlation)"
            ),
            overall_interpretation="Derivatives data suggests a healthy bullish trend with positive funding and confirming volume, though no significant trapped traders or stop hunts observed.",
            divergence_flag_oi=False,
            divergence_flag_cvd=False,
            notes=f"Funding rate {simulated_fr_value}% classified as {funding_rate_state} per checklist rule (simulated)."
        )
