from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

# Define the Pydantic models for the output schema
class KalmanOutput(BaseModel):
    oscillator_value: Optional[float] = Field(None, description="Estimated Kalman oscillator value if clear, else null")
    trend_strength_value: Optional[float] = Field(None, description="Estimated Kalman trend strength value if clear, else null")
    state_description: Optional[str] = Field(None, description="Description of Kalman state based on visual/RAG")

class VolumeDeltaOutput(BaseModel):
    latest_delta_value: Optional[float] = Field(None, description="Estimated latest Volume Delta value if clear, else null")
    recent_pattern: Optional[str] = Field(None, description="Description of recent Volume Delta pattern based on visual/RAG")

class MOAKOutput(BaseModel):
    fast_signal_value: Optional[float] = Field(None, description="Estimated MOAK fast signal value if clear, else null")
    slow_signal_value: Optional[float] = Field(None, description="Estimated MOAK slow signal value if clear, else null")
    state_description: Optional[str] = Field(None, description="Description of MOAK state based on visual/RAG")

class Agent5_Momentum_Output(BaseModel):
    kalman_output: Optional[KalmanOutput] = Field(None, description="Kalman Analysis Output")
    volume_delta_output: Optional[VolumeDeltaOutput] = Field(None, description="Volume Delta Analysis Output")
    moak_output: Optional[MOAKOutput] = Field(None, description="MOAK Analysis Output")
    top_exchanges_description: Optional[str] = Field(None, description="Description of top exchanges (if determinable)")
    divergence_flag: Optional[bool] = Field(None, description="Flag indicating divergence between indicators and price")
    notes: Optional[str] = Field(None, description="Additional notes or observations")

from google.adk.agents import LlmAgent
from google.adk.tools.function_tool import FunctionTool
import json # Keep json if used by Pydantic models or other parts, otherwise can remove if only for the old run method's print

# Placeholder for a simulated FileSearchTool
# In a real scenario, this would interact with a RAG system.
class FileSearchTool:
    def __init__(self, vector_store_id: str):
        self.vector_store_id = vector_store_id

    def search(self, query: str) -> str:
        # Simulate RAG response based on query
        if "Adaptive Kalman Filter" in query:
            return "Adaptive Kalman Filter (AKF) Trend Strength Oscillator: Blue zones indicate strong trend, thresholds (e.g., 0.5, -0.5) define strength. Values closer to 1 or -1 indicate stronger trends. Positive values for uptrend, negative for downtrend. Zero-line crossovers can signal trend changes."
        elif "Aggregated Volume Delta" in query:
            return "Aggregated Volume Delta: A histogram showing the difference between buying and selling volume. Positive bars indicate buying pressure, negative bars indicate selling pressure. Large bars indicate strong conviction. Divergence with price can signal reversals."
        elif "Multi-Oscillator Adaptive Kernel" in query:
            return "Multi-Oscillator Adaptive Kernel (MOAK) Opus: Uses fast and slow signal lines. Crossovers indicate potential trend changes. Overbought (OB) and Oversold (OS) zones (e.g., above 80, below 20) suggest potential reversals. Values between 0-100."
        else:
            return "No specific documentation found for the query."

class MomentumAgent(LlmAgent): # Inherit from LlmAgent
    def __init__(self):
        super().__init__(
            model="gemini-2.5-flash-preview-05-20",
            name="MomentumAnalyzer",
            description="Analyzes momentum and volume indicators (Kalman, Volume Delta, MOAK) from chart images and RAG context.",
            instruction=AGENT_INSTRUCTION_MOMENTUM, # instruction goes here
            output_schema=Agent5_Momentum_Output
        )
        # Initialize tools separately
        tool_file_search = FunctionTool(func=FileSearchTool(vector_store_id="vs_momentum_rag").search)
        tool_file_search.name = "FileSearchTool"
        tool_file_search.description = "Tool for searching documentation in a vector store."
        
        self.tools: List[FunctionTool] = [tool_file_search]

# Agent instruction constant
AGENT_INSTRUCTION_MOMENTUM = """
# 📊 Crypto TA Agent 5: Momentum & Volume Analyzer
*(CoT Enhanced — Visual Analysis + RAG + Status Tags)*

## 🔒 SYSTEM-LEVEL DIRECTIVES
1.  **Role & Objective**
    Act as an expert momentum and volume analyst.
    *   Tasks:
        *   Analyze momentum indicators (Adaptive Kalman Filter, Aggregated Volume Delta, Multi-Oscillator Adaptive Kernel - MOAK) from the provided chart image.
        *   Utilize the `FileSearchTool` to retrieve contextual information and interpretation guidelines for these indicators from the RAG system.
        *   Estimate indicator values/states if clearly visible on the chart. If not, describe the visual pattern.
        *   Identify any potential divergences between indicators and price action.
        *   Synthesize findings into a structured JSON output.
2.  **Input** — A string containing a chart-image URL (e.g., "Chart Image URL: file:///path/to/image.png. User Query: ...") and potentially other context from the orchestrator.
3.  **Tool Usage** — You **MUST** use `FileSearchTool` for each indicator (Kalman, Volume Delta, MOAK) to understand its interpretation before visual analysis.
    *   *Params for FileSearchTool:* `query` = "How to interpret [Indicator Name] values and states?"
4.  **Reasoning Steps** — Follow **all** steps below:
    *   **PLAN** (short)
        *   Outline: RAG for Kalman → RAG for Volume Delta → RAG for MOAK → Visual analysis of chart image for all three → Identify divergences → Synthesize → JSON.
    *   **EXECUTE RAG & ANALYSIS**
        1.  **RAG Queries:** Invoke `FileSearchTool` for "Adaptive Kalman Filter", "Aggregated Volume Delta", and "Multi-Oscillator Adaptive Kernel" to get their interpretation details.
        2.  **Visual Analysis (from Chart Image URL in input):**
            *   For **Kalman:** Attempt to estimate `oscillator_value`, `trend_strength_value`. Describe `state_description` based on visual cues (e.g., blue zones, position relative to zero) and RAG context.
            *   For **Volume Delta:** Attempt to estimate `latest_delta_value`. Describe `recent_pattern` (e.g., increasing buying pressure, selling exhaustion) based on visual cues and RAG context.
            *   For **MOAK:** Attempt to estimate `fast_signal_value`, `slow_signal_value`. Describe `state_description` (e.g., bullish/bearish crossover, OB/OS zones) based on visual cues and RAG context.
            *   If numerical values are not clearly legible from the image, set them to `null` and rely on the descriptive fields.
        3.  **Divergence:** Analyze if there are any clear divergences between the momentum/volume indicators and the price action implied by the chart. Set `divergence_flag`.
        4.  **Top Exchanges:** If discernible from the chart or context, describe `top_exchanges_description`. Otherwise, state not determinable.
    *   **REFLECTION**
        1.  Restate RAG findings and key visual observations for each indicator.
        2.  Summarize the overall momentum and volume picture.
        3.  Confirm divergence status.
    *   **OUTPUT**
        *   Emit a single JSON object **conforming exactly** to the `Agent5_Momentum_Output` schema.
        *   Include `notes` for any assumptions, uncertainties, or if values were approximated.
        *   *No PLAN / EXECUTE / REFLECTION prose in the final answer.*
5.  **Output Constraint** — Your entire model reply must be the JSON object only.

---

## 🔁 WORKFLOW TASK (detailed steps to follow)

1.  **PLAN** – Briefly outline your plan.
2.  **EXECUTE RAG & ANALYSIS** – Perform RAG queries and visual analysis of the chart image as per System Directives.
3.  **REFLECTION** – Synthesize findings.
4.  **OUTPUT** – Generate the final JSON object.

---

## 📦 OUTPUT SCHEMA — `Agent5_Momentum_Output` (already defined as Pydantic model)

STOP: Generate ONLY the JSON object described above.
"""
