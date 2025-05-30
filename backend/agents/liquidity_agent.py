from google.adk.agents import LlmAgent

# Define tools needed for this agent
async def file_search_tool(query: str) -> dict:
    """
    Simulates a RAG/FileSearch tool for querying knowledge base about FVG Order Blocks, 
    AlgoAlpha Smart Money Breakout signals, etc.
    """
    print(f"[LiquidityAgent Tool] file_search_tool called with query: {query}")
    
    # Simulate responses based on common queries
    if "fvg" in query.lower() or "order blocks" in query.lower() or "bigbeluga" in query.lower():
        return {
            "results": [
                {
                    "content": "FVG (Fair Value Gap) Order Blocks by BigBeluga identify imbalance zones where price moved quickly, leaving gaps. Strength percentage indicates the reliability of the zone. Bearish FVGs act as resistance, bullish FVGs as support. Higher strength percentages (>70%) indicate stronger zones.",
                    "source": "FVG_Order_Blocks_BigBeluga.md"
                }
            ]
        }
    elif "algolpha" in query.lower() or "smart money" in query.lower() or "breakout" in query.lower():
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

## 📦 Output Schema (Agent4_Liquidity_Output - Verbose Example)

Your response MUST be ONLY the following JSON structure (after PLAN/REFLECT steps). Lists are required.

```json
{
  "fvgs": [
    {
      "top": 353.2,
      "bottom": 349.8,
      "type": "bearish",
      "strength_pct": 0.78
    },
     {
      "top": 341.4,
      "bottom": 338.1,
      "type": "bullish",
      "strength_pct": 0.62
    }
  ],
  "order_blocks": [],
  "breakout_signals": [
    {
      "type": "CHoCH_up",
      "price_level": 336.8
    },
    {
      "type": "BOS_down",
      "price_level": 336.8
    }
  ],
  "notes": "Price consolidating within bearish FVG, above bullish FVG."
}

STOP: Generate ONLY the required JSON object after completing the PLAN/REFLECT steps. Ensure lists are present.
"""

root_agent = LlmAgent(
    model="gemini-2.5-flash-preview-05-20",
    name="analyze_liquidity_orderflow",
    description="Analyzes liquidity zones, FVGs, Order Blocks, and Smart Money Breakout signals using RAG context.",
    instruction=AGENT_INSTRUCTION_LIQUIDITY,
    tools=[file_search_tool]
)
