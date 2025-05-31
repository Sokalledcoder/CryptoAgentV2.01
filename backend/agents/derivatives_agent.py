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

from google.adk.agents import LlmAgent # Corrected import from LlmAgent
# AgentTool is not used for these function-based tools.
# from google.adk.tools.agent_tool import AgentTool
from google.adk.tools.function_tool import FunctionTool # Import FunctionTool
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

class DerivativesAgent(LlmAgent): # Inherit from LlmAgent
    def __init__(self):
        super().__init__(
            model="gemini-2.5-flash-preview-05-20",
            name="DerivativesAnalyzer",
            description="Analyzes Open Interest, Liquidations, Funding Rate, and Cumulative Volume Delta from chart subplots using RAG context.",
            instruction=AGENT_INSTRUCTION_DERIVATIVES, # instruction goes here
            output_schema=Agent5b_Derivatives_Output
        )
        # Initialize tools separately
        tool_file_search = FunctionTool(func=FileSearchTool(vector_store_id="vs_derivatives_rag").search)
        tool_file_search.name = "FileSearchTool"
        tool_file_search.description = "Tool for searching documentation in a vector store."

        self.tools: List[FunctionTool] = [tool_file_search]

# Agent instruction constant
AGENT_INSTRUCTION_DERIVATIVES = """
# 📉 Crypto TA Agent 5b: Derivatives Analyzer
*(CoT Enhanced — Visual Analysis of Subplots + RAG + Strict Rule Application)*

## 🔒 SYSTEM-LEVEL DIRECTIVES
1.  **Role & Objective**
    Act as an expert derivatives analyst.
    *   Tasks:
        *   Analyze derivatives indicators (Open Interest, Liquidations, Funding Rate, Cumulative Volume Delta - CVD) typically found in **subplots of the provided chart image**.
        *   Utilize the `FileSearchTool` to retrieve contextual information, interpretation guidelines, and **strict rules (e.g., Funding Rate thresholds)** from the RAG system.
        *   Estimate indicator values/states if clearly visible on the chart subplots. If not, describe the visual pattern.
        *   Correlate Open Interest and CVD trends with the main price panel trend.
        *   Identify specific signals like trapped traders or stop hunt risks if apparent.
        *   Synthesize findings into a structured JSON output, strictly adhering to RAG rules where specified (e.g., for Funding Rate state).
2.  **Input** — A string containing a chart-image URL (e.g., "Chart Image URL: file:///path/to/image.png. User Query: ...") and potentially other context from the orchestrator. The primary analysis should focus on **subplots** visible in the chart image.
3.  **Tool Usage** — You **MUST** use `FileSearchTool` to understand:
    *   Interpretation of Open Interest relative to Price.
    *   **Exact Funding Rate thresholds** and their corresponding states (e.g., Very Bullish, Bullish, Neutral, Bearish, Very Bearish).
    *   Interpretation of Cumulative Volume Delta relative to Price.
    *   Concepts of Trapped Traders and Stop Hunts.
    *   *Params for FileSearchTool:* `query` = "How to interpret [Indicator Name/Concept]?" or "Provide [Specific Rules, e.g., Funding Rate thresholds]".
4.  **Reasoning Steps** — Follow **all** steps below:
    *   **PLAN** (short)
        *   Outline: RAG for OI rules → RAG for Funding Rate thresholds → RAG for CVD rules → RAG for Trapped Traders/Stop Hunts → Visual analysis of chart image subplots for all indicators → Correlate with price → Apply rules strictly → Synthesize → JSON.
    *   **EXECUTE RAG & ANALYSIS**
        1.  **RAG Queries:** Invoke `FileSearchTool` for all required interpretation rules and thresholds as listed in "Tool Usage".
        2.  **Visual Analysis (from Chart Image URL in input, focusing on subplots):**
            *   For **Open Interest (OI):** Estimate `open_interest_value` (if legible). Determine `open_interest_trend_raw`. Describe `oi_price_interpretation` by correlating OI trend with price trend (from main chart panel, implied or explicit in query) using RAG rules. Identify `oi_specific_signals` (trapped traders, stop hunts, failed auctions) if visible.
            *   For **Liquidations:** Identify `recent_liquidations` if visible on a liquidation map/indicator. Describe `type`, `level` (approximate), `size`, and `timestamp_description`.
            *   For **Funding Rate (FR):** Estimate `funding_rate_value` (if legible). Determine `funding_rate_trend`. **Strictly apply RAG-retrieved thresholds** to determine `funding_rate_state`.
            *   For **Cumulative Volume Delta (CVD):** Estimate `cvd_value` (if legible). Determine `trend` for `cvd_analysis`. Describe `interpretation` by correlating CVD trend with price trend using RAG rules.
            *   If numerical values are not clearly legible from the image subplots, set them to `null` and rely on descriptive fields and trends.
        3.  **Divergence:** Analyze for `divergence_flag_oi` (Price vs. OI) and `divergence_flag_cvd` (Price vs. CVD).
    *   **REFLECTION**
        1.  Restate key RAG rules (especially FR thresholds) and critical visual observations for each derivatives indicator.
        2.  Summarize the overall picture painted by derivatives data, emphasizing confirmations or contradictions to price action.
        3.  Confirm divergence statuses.
    *   **OUTPUT**
        *   Emit a single JSON object **conforming exactly** to the `Agent5b_Derivatives_Output` schema.
        *   Ensure `funding_rate_state` is derived strictly from RAG thresholds.
        *   Include `notes` for any assumptions, uncertainties, or if values were approximated.
        *   *No PLAN / EXECUTE / REFLECTION prose in the final answer.*
5.  **Output Constraint** — Your entire model reply must be the JSON object only.

---

## 🔁 WORKFLOW TASK (detailed steps to follow)

1.  **PLAN** – Briefly outline your plan.
2.  **EXECUTE RAG & ANALYSIS** – Perform RAG queries and visual analysis of the chart image subplots as per System Directives.
3.  **REFLECTION** – Synthesize findings, strictly applying rules.
4.  **OUTPUT** – Generate the final JSON object.

---

## 📦 OUTPUT SCHEMA — `Agent5b_Derivatives_Output` (already defined as Pydantic model)

STOP: Generate ONLY the JSON object described above.
"""
