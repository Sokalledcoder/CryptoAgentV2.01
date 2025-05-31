from google.adk.agents import LlmAgent
from google.adk.tools.function_tool import FunctionTool
from pydantic import BaseModel, Field
from typing import Optional, List, Literal

# 1. Define Pydantic Models for Output Schema (Agent4_Liquidity_Output)
class FVG(BaseModel):
    top: float
    bottom: float
    type: Literal["bearish", "bullish"]
    strength_pct: float = Field(..., ge=0, le=1) # Percentage between 0 and 1

class OrderBlock(BaseModel): # Assuming a structure, can be refined
    top: float
    bottom: float
    type: Literal["bearish", "bullish"]

class BreakoutSignal(BaseModel):
    type: Literal["CHoCH_up", "CHoCH_down", "BOS_up", "BOS_down"]
    price_level: float

class Agent4_Liquidity_Output(BaseModel):
    fvgs: List[FVG] = Field(default_factory=list)
    order_blocks: List[OrderBlock] = Field(default_factory=list)
    breakout_signals: List[BreakoutSignal] = Field(default_factory=list)
    notes: Optional[str] = None

AGENT_INSTRUCTION_LIQUIDITY = """
# 📈 Crypto TA Agent 4: Liquidity & Order-Flow Analyzer (RAG + CoT Enhanced - Refined)

## 🔒 SYSTEM-LEVEL DIRECTIVES
1.  **Role & Objective:** Expert liquidity/order-flow analyst. Identify FVGs, OBs, Breakout Signals visually, using RAG for interpretation context. Output structured JSON.
2.  **Input:** Chart image URL + context from Agents 1-3.
3.  **Tool Usage:** Access to `file_search_tool`. **MUST use it** for context on "FVG Order Blocks [BigBeluga]" and "AlgoAlpha - Smart Money Breakout".
4.  **Reasoning Steps:** You MUST use the following reasoning steps:
    *   **PLAN:** State plan (query docs for FVG/OB and AlgoAlpha context, then visually analyze chart for these elements using doc context, reflect, output JSON).
    *   **EXECUTE RAG & ANALYSIS:** Invoke `file_search_tool` for both topics AND THEN perform the visual analysis of the chart.
    *   **REFLECTION:** Summarize key interpretation points from docs. State the results of the visual analysis (identified FVGs, OBs, Breakout Signals with their details).
    *   **OUTPUT:** Generate the final JSON based on the comprehensive reflection.
5.  **Output Constraint:** Output ONLY the single, strictly valid JSON object conforming to `Agent4_Liquidity_Output` schema. Lists are REQUIRED (`[]` if none). Do NOT include PLAN/REFLECT/EXECUTE lines in the final JSON output.

---

## 🔁 Workflow Task (RAG + CoT Enhanced - Refined)

**Analyze Liquidity & Order-Flow (Output Structured Data):**
1.  **PLAN:** Plan to query file_search_tool for interpretation guides on FVG Order Blocks (BigBeluga) and AlgoAlpha BOS/CHoCH signals. Subsequently, plan to visually identify FVG zones, distinct Order Blocks, and Breakout Signals on the chart, using the RAG context. Finally, reflect on all findings and generate the structured JSON.
2.  **EXECUTE RAG & ANALYSIS:**
    *   Invoke `file_search_tool`: Ask "How to interpret FVG Order Blocks BigBeluga indicator zones and strength percentage?".
    *   Invoke `file_search_tool`: Ask "How to identify AlgoAlpha Smart Money Breakout BOS and CHoCH signals?".
    *   *After* reviewing the tool outputs, perform visual analysis of the chart: Identify FVG zones (top, bottom, type, strength%), distinct OBs (top, bottom, type), and Breakout Signals (type, price_level).
3.  **REFLECTION:** Summarize key interpretations from docs for FVG/OBs and AlgoAlpha signals. List the specific FVG zones, Order Block zones, and Breakout Signals identified visually with their details.
4.  **OUTPUT:** Generate the `Agent4_Liquidity_Output` JSON based on Reflection. Populate the `fvgs`, `order_blocks`, and `breakout_signals` lists. Add brief `notes` if needed.

---

## 📦 Output Schema (Agent4_Liquidity_Output - Verbose Example) - Defined as Pydantic Model

Your response MUST be ONLY the following JSON structure (after PLAN/REFLECT steps). Lists are required.

STOP: Generate ONLY the required JSON object after completing the PLAN/REFLECT steps. Ensure lists are present.
"""

class LiquidityAgent(LlmAgent):
    def __init__(self):
        super().__init__(
            model="gemini-2.5-flash-preview-05-20", # Assuming vision capabilities
            name="analyze_liquidity_orderflow",
            description="Analyzes liquidity zones, FVGs, Order Blocks, and Smart Money Breakout signals using RAG context.",
            instruction=AGENT_INSTRUCTION_LIQUIDITY,
            output_schema=Agent4_Liquidity_Output
        )

        search_tool = FunctionTool(func=self._simulated_file_search)
        search_tool.name = "file_search_tool"
        search_tool.description = "Simulates a RAG/FileSearch tool for querying knowledge base about FVG Order Blocks, AlgoAlpha Smart Money Breakout signals, etc."
        search_tool.input_schema = {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The search query for the knowledge base."}
            },
            "required": ["query"]
        }
        self.tools: List[FunctionTool] = [search_tool]

    async def _simulated_file_search(self, query: str) -> dict:
        """
        Simulates a RAG/FileSearch tool for querying knowledge base.
        """
        print(f"[LiquidityAgent Tool SIMULATION] _simulated_file_search called with query: {query}")
        
        query_lower = query.lower()
        if "fvg" in query_lower or "order blocks" in query_lower or "bigbeluga" in query_lower:
            return {
                "results": [
                    {
                        "content": "FVG (Fair Value Gap) Order Blocks by BigBeluga identify imbalance zones where price moved quickly, leaving gaps. Strength percentage indicates the reliability of the zone. Bearish FVGs act as resistance, bullish FVGs as support. Higher strength percentages (>70%) indicate stronger zones.",
                        "source": "FVG_Order_Blocks_BigBeluga.md"
                    }
                ]
            }
        elif "algolpha" in query_lower or "smart money" in query_lower or "breakout" in query_lower:
            return {
                "results": [
                    {
                        "content": "AlgoAlpha Smart Money Breakout signals include BOS (Break of Structure) and CHoCH (Change of Character). BOS indicates continuation of trend, CHoCH indicates potential reversal. These signals are marked at specific price levels where institutional activity is detected.",
                        "source": "AlgoAlpha_Smart_Money_Breakout.md"
                    }
                ]
            }
        else:
            return {
                "results": [
                    {
                        "content": "General liquidity analysis involves identifying order flow imbalances, institutional activity zones, and breakout patterns.",
                        "source": "Liquidity_Analysis.md"
                    }
                ]
            }
