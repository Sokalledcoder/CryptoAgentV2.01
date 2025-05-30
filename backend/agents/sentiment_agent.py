from google.adk.agents import LlmAgent
from google.adk.tools.agent_tool import AgentTool # Corrected import path for AgentTool
from google.adk.side_effects import ToolCode # Import ToolCode for MCP calls
from typing import Dict, Any

# Define the Pydantic model for the output schema (assuming it's defined elsewhere or will be defined here)
from pydantic import BaseModel, Field
from typing import Optional

class Agent6_Sentiment_Output(BaseModel):
    fear_greed_value: Optional[int] = Field(None, description="Fear and Greed Index value")
    fear_greed_rating: Optional[str] = Field(None, description="Fear and Greed Index rating")
    historical_comparison_notes: Optional[str] = Field(None, description="Notes on historical comparison of Fear and Greed Index")
    btc_dominance: Optional[float] = Field(None, description="Bitcoin Dominance percentage")
    total_market_cap: Optional[str] = Field(None, description="Total crypto market capitalization")
    notes: Optional[str] = Field(None, description="Additional notes or observations")

class SentimentAgent(LlmAgent):
    def __init__(self):
        super().__init__(
            model="gemini-2.5-flash-preview-05-20",
            name="analyze_sentiment_macro",
            description="Analyzes market sentiment using Fear & Greed Index and global market data via MCP tools.",
            instruction="""
# 📈 Crypto TA Agent 6: Sentiment & Macro Analyzer (MCP + CoT Enabled)

## 🔒 SYSTEM-LEVEL DIRECTIVES
1.  **Role & Objective:** Analyst focused on gathering crypto market sentiment (F&G) and global data (BTC Dom, MktCap) using MCP tools. Output structured JSON.
2.  **Input:** Context from previous steps.
3.  **Tool Usage:** Access to Fear & Greed MCP tools (`mcp_fearandgreed_*`) and CoinGecko MCP tool (`global-market-data`). **MUST use these tools.**
4.  **Reasoning Steps:** You MUST use the following reasoning steps:
    *   **PLAN:** State plan (call F&G tools, call Global Data tool, reflect, output JSON).
    *   **TOOL CALLS:** Invoke `mcp_fearandgreed_get_current`, `mcp_fearandgreed_interpret_value`, `mcp_fearandgreed_compare_with_historical`, and `global-market-data`.
    *   **REFLECTION:** Briefly summarize the retrieved F&G value/rating/comparison and the BTC Dom/Market Cap values.
    *   **OUTPUT:** Generate the final JSON.
5.  **Output Constraint:** Output ONLY the single, strictly valid JSON object conforming to `Agent6_Sentiment_Output` schema. Do NOT include PLAN/REFLECT lines in the final JSON output.

---

## 🔁 Workflow Task (MCP + CoT Enabled)

**Analyze Sentiment & Macro Context:**
1.  **PLAN:** Plan to call the three Fear & Greed tools for current value, rating, and historical context. Then call the global-market-data tool for BTC dominance and total market cap. Reflect on the gathered data. Generate final JSON.
2.  **TOOL CALL (1/4):** Invoke `mcp_fearandgreed_get_current`.
3.  **TOOL CALL (2/4):** Invoke `mcp_fearandgreed_interpret_value` (using value from previous call).
4.  **TOOL CALL (3/4):** Invoke `mcp_fearandgreed_compare_with_historical`.
5.  **TOOL CALL (4/4):** Invoke `global_market_data`.
6.  **REFLECTION:** Note the F&G value, rating, and historical comparison notes from tool results. Note the BTC dominance % and total market cap string from the global data tool result.
7.  **OUTPUT:** Generate the `Agent6_Sentiment_Output` JSON, populating fields from the tool results obtained during Reflection. Add brief summary `notes`.

---

## 📦 Output Schema (Agent6_Sentiment_Output)

Your response MUST be ONLY the following JSON structure (after PLAN/REFLECT steps):

```json
{
  "fear_greed_value": "integer | null",
  "fear_greed_rating": "string | null",
  "historical_comparison_notes": "string | null",
  "btc_dominance": "number | null", // Expecting float
  "total_market_cap": "string | null", // Expecting formatted string like '$X.XT'
  "notes": "string | null"
}

STOP: Generate ONLY the JSON object described above after completing the PLAN/REFLECT steps using the specified MCP tools.
""",
            output_model=Agent6_Sentiment_Output,
            tools=[
                AgentTool(
                    name="mcp_fearandgreed_get_current",
                    description="Gets the current Fear and Greed Index value.",
                    tool_code=ToolCode.from_callable(self._call_mcp_fearandgreed_get_current),
                    parameters={"type": "object", "properties": {"random_string": {"type": "string"}}}
                ),
                AgentTool(
                    name="mcp_fearandgreed_interpret_value",
                    description="Interprets a Fear and Greed Index value.",
                    tool_code=ToolCode.from_callable(self._call_mcp_fearandgreed_interpret_value),
                    parameters={"type": "object", "properties": {"value": {"type": "number"}}, "required": ["value"]}
                ),
                AgentTool(
                    name="mcp_fearandgreed_compare_with_historical",
                    description="Compares current Fear and Greed Index with historical data.",
                    tool_code=ToolCode.from_callable(self._call_mcp_fearandgreed_compare_with_historical),
                    parameters={"type": "object", "properties": {"days": {"type": "number"}}}
                ),
                AgentTool(
                    name="global_market_data",
                    description="Gets global cryptocurrency market data including BTC dominance and total market cap.",
                    tool_code=ToolCode.from_callable(self._call_global_market_data),
                    parameters={"type": "object", "properties": {"include_defi": {"type": "boolean"}}}
                )
            ]
        )

    async def _call_mcp_fearandgreed_get_current(self, random_string: str = "dummy") -> Dict[str, Any]:
        return await self.call_tool(
            server_name="fearandgreed-mcp",
            tool_name="mcp_fearandgreed_get_current",
            arguments={"random_string": random_string}
        )

    async def _call_mcp_fearandgreed_interpret_value(self, value: int) -> Dict[str, Any]:
        return await self.call_tool(
            server_name="fearandgreed-mcp",
            tool_name="mcp_fearandgreed_interpret_value",
            arguments={"value": value}
        )

    async def _call_mcp_fearandgreed_compare_with_historical(self, days: int = 30) -> Dict[str, Any]:
        return await self.call_tool(
            server_name="fearandgreed-mcp",
            tool_name="mcp_fearandgreed_compare_with_historical",
            arguments={"days": days}
        )

    async def _call_global_market_data(self, include_defi: bool = False) -> Dict[str, Any]:
        return await self.call_tool(
            server_name="coingecko-mcp",
            tool_name="global-market-data",
            arguments={"include_defi": include_defi}
        )

    async def run(self, context_from_previous_steps: Dict[str, Any]) -> Agent6_Sentiment_Output:
        print("PLAN: Calling Fear & Greed Index and CoinGecko global market data tools. Reflecting on results and generating structured JSON output.")

        # TOOL CALLS
        fg_current_result = await self._call_mcp_fearandgreed_get_current()
        fg_value = fg_current_result.get('value')

        fg_interpret_result = await self._call_mcp_fearandgreed_interpret_value(value=fg_value)
        fg_historical_result = await self._call_mcp_fearandgreed_compare_with_historical()
        global_market_result = await self._call_global_market_data()

        # REFLECTION
        fear_greed_value = fg_value
        fear_greed_rating = fg_interpret_result.get('classification')
        historical_comparison_notes = fg_historical_result.get('notes')

        btc_dominance = global_market_result.get('data', {}).get('market_cap_percentage', {}).get('btc')
        total_market_cap_usd = global_market_result.get('data', {}).get('total_market_cap', {}).get('usd')
        total_market_cap_str = f"${total_market_cap_usd:,.2f}" if total_market_cap_usd else None

        notes = "Sentiment and macro data retrieved from Fear & Greed Index and CoinGecko MCP servers."

        # OUTPUT
        return Agent6_Sentiment_Output(
            fear_greed_value=fear_greed_value,
            fear_greed_rating=fear_greed_rating,
            historical_comparison_notes=historical_comparison_notes,
            btc_dominance=btc_dominance,
            total_market_cap=total_market_cap_str,
            notes=notes
        )

root_agent = SentimentAgent()
