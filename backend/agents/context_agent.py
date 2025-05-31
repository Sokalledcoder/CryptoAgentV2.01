from google.adk.agents import LlmAgent
from google.adk.tools.function_tool import FunctionTool
from pydantic import BaseModel, Field
from typing import Optional, Union, List # Added List for self.tools

# 1. Define the Pydantic Output Model
class Agent1_Context_Output(BaseModel):
    pair: str
    timeframe: str
    exchange: Optional[str] = None
    latest_ohlc_open: Optional[float] = Field(default=None, description="Latest Open price from chart")
    latest_ohlc_high: Optional[float] = Field(default=None, description="Latest High price from chart")
    latest_ohlc_low: Optional[float] = Field(default=None, description="Latest Low price from chart")
    latest_ohlc_close: Optional[float] = Field(default=None, description="Latest Close price from chart")
    ohlc_data_description: Optional[str] = Field(default=None, description="Description of the OHLC data source or context")
    range_high: Optional[float] = Field(default=None, description="Estimated high of the current visual range")
    range_low: Optional[float] = Field(default=None, description="Estimated low of the current visual range")
    price_now: float = Field(description="Final validated price. 0.0 if invalid / mismatch / fail / out-of-range")
    price_delta_pct: Optional[float] = Field(default=None, description="Calculated only if price_now is valid (not 0.0)")
    notes: Optional[str] = Field(default=None, description="MUST start with final status tag; include validation & sanity-check details")

AGENT_INSTRUCTION_CONTEXT = """
# 📈 Crypto TA Agent 1: Chart Context Analyzer
*(CoT Enhanced — OHLC + Validation + Status Tags)*

## 🔒 SYSTEM-LEVEL DIRECTIVES
1.  **Role & Objective**
    Act as an expert chart analyst.
    *   Tasks:
        *   Identify chart context from the image (pair, timeframe, exchange, brief description).
        *   Extract the **latest candle OHLC numbers displayed near the ticker**.
        *   Call the MCP **`fetch_current_price`** tool for a live quote.
        *   **Validate** the returned asset & price.
        *   Perform a conditional price range sanity check.
        *   Report tool status with standardized tags.
        *   Output one strictly valid JSON object.
2.  **Input** — A chart-image URL plus the orchestrator’s text context.
3.  **Tool Usage** — You **MUST** attempt `fetch_current_price`.
    *   *Params:* `coins` = base-asset slug (lower-case, e.g. `bitcoin`), `currencies` = `usd`.
4.  **Reasoning Steps** — Follow **all** steps below:
    *   **PLAN** (short)
        *   Outline: image analysis → build tool args → call tool → asset/price validation → sanity check → JSON.
    *   **EXECUTE ANALYSIS & TOOL CALL**
        1.  **Visual analysis** — Capture `pair`, `timeframe`, `exchange`, `ohlc_data_description`, estimate `range_high` / `range_low`, and **extract O, H, L, C values**.
        2.  **Prepare tool args** — `coins` = lower-case base symbol from `pair` (e.g. `HYPEUSDT` ➜ `hype`); `currencies` = `usd`.
        3.  **Invoke `fetch_current_price`** with those args. Record raw response or error.
    *   **REFLECTION**
        1.  Restate visual findings & tool result.
        2.  **Asset-slug validation** — Compare the tool’s returned `id`/`symbol` to the requested slug.
        3.  **Determine Status Tag** (always choose one):
            *   `[TOOL_SUCCESS]` — tool succeeded **and** asset matched.
            *   `[TOOL_MISMATCH]` — tool succeeded **but** asset mismatched.
            *   `[TOOL_FAIL]` — tool errored or returned 0.
        4.  **Set `price_now` (Initial)** —
            *   If tag =`[TOOL_SUCCESS]`, tentatively accept the returned price.
            *   Otherwise set `price_now` = `0.0`.
        5.  **Sanity check (Price Range - Conditional)** — Run **only if tag =`[TOOL_SUCCESS]`** (i.e., only if asset matched and tool returned a non-zero price):
            *   Compare the tentatively accepted `price_now` against visual `range_low` and `range_high`.
            *   If `price_now < range_low` or `price_now > range_high`, mark **out-of-range** ➜ **Invalidate the price**:
                *   Set `price_now = 0.0`.
                *   Change the Status Tag to `[TOOL_MISMATCH]` (reason: out-of-range).
        6.  **Compute `price_delta_pct`**
            *   Calculate (e.g., vs latest close or range midpoint) **only if `price_now` ≠ 0.0** (i.e., only if tool succeeded, asset matched, AND price was within range); else set `null`.
        7.  **Compose `notes`** —
            *   **Start with the final status tag** (`[TOOL_SUCCESS]`, `[TOOL_MISMATCH]`, `[TOOL_FAIL]`).
            *   Then: brief reason (e.g., asset matched / asset mismatched / tool error / price out-of-range) and sanity-check outcome (e.g., consistent / failed-out-of-range / skipped).
    *   **OUTPUT**
        *   Emit a single JSON object **conforming exactly** to the schema below.
        *   *No PLAN / EXECUTE / REFLECTION prose in the final answer.*
5.  **Output Constraint** — Your entire model reply must be the JSON object only.

---

## 🔁 WORKFLOW TASK (detailed steps to follow)

1.  **PLAN** – Briefly outline your plan (≈ 1 sentence).
2.  **EXECUTE ANALYSIS & TOOL CALL** – Perform visual analysis, prepare args, call the `fetch_current_price` tool.
3.  **REFLECTION** – Apply the detailed asset validation, tagging, price setting, conditional sanity check, delta calculation, and notes composition logic from the System Directives section above.
4.  **OUTPUT** – Generate the final JSON object conforming to the schema.

---

## 📦 OUTPUT SCHEMA — `Agent1_Context_Output` (already defined as Pydantic model)

STOP: Generate ONLY the JSON object described above after completing the PLAN/REFLECT steps.
"""

class ContextAgent(LlmAgent):
    def __init__(self):
        super().__init__(
            model="gemini-2.5-flash-preview-05-20", # Assuming this model has vision capabilities
            name="analyze_chart_context",
            description="Analyzes chart context from an image, extracts OHLC, calls a price tool, validates, and outputs a JSON string.", # Modified description
            instruction=AGENT_INSTRUCTION_CONTEXT
            # output_schema=Agent1_Context_Output # Removed output_schema to avoid application/json mime type issue
        )
        
        # Define the tool using FunctionTool
        price_tool = FunctionTool(func=self._simulated_mcp_get_price)
        price_tool.name = "fetch_current_price" # Changed tool name
        price_tool.description = "Gets the current price for a list of coins in specified currencies. Simulates a call to CoinGecko MCP."
        # Input schema for the tool (for LLM guidance, actual validation by Pydantic in the method if needed)
        price_tool.input_schema = {
            "type": "object",
            "properties": {
                "coins": {"type": "string", "description": "Comma-separated list of coin IDs (e.g., \"bitcoin,ethereum\")"},
                "currencies": {"type": "string", "default": "usd", "description": "Comma-separated list of currencies (e.g., \"usd,eur\")"}
            },
            "required": ["coins"]
        }
        self.tools: List[FunctionTool] = [price_tool]

    async def _simulated_mcp_get_price(self, coins: str, currencies: str = "usd") -> dict:
        """
        Simulates a call to CoinGecko MCP to get the current price for a list of coins.
        """
        print(f"[ContextAgent Tool SIMULATION] _simulated_mcp_get_price called with coins: {coins}, currencies: {currencies}")
        coin_list = coins.lower().split(',')
        response = {}
        
        # Basic simulation logic
        if not coin_list or not coins.strip():
            return {"error": "No coins specified or empty coin string."}

        if "bitcoin" in coin_list:
            response["bitcoin"] = {"usd": 50000.00, "id": "bitcoin", "symbol": "btc", "name": "Bitcoin"}
            # Simulate other coins if requested alongside bitcoin
            for c_item in coin_list:
                if c_item != "bitcoin" and c_item not in response:
                    response[c_item] = {"usd": 100.00 + len(c_item) * 10, "id": c_item, "symbol": c_item[:3].upper(), "name": c_item.capitalize()} # Dummy data
        else:
            for c_item in coin_list:
                response[c_item] = {"usd": 100.00 + len(c_item) * 10, "id": c_item, "symbol": c_item[:3].upper(), "name": c_item.capitalize()} # Dummy data
        
        # Ensure each coin in the response has the currency key
        final_response = {}
        for coin_id, data in response.items():
            final_response[coin_id] = {cur: data.get(cur, 0.0) for cur in currencies.split(',')}
            final_response[coin_id]['id'] = data.get('id', coin_id)
            final_response[coin_id]['symbol'] = data.get('symbol', coin_id[:3].upper())
            final_response[coin_id]['name'] = data.get('name', coin_id.capitalize())
            # Ensure the primary currency (first in list, or usd) has the main price
            main_currency = currencies.split(',')[0]
            if main_currency not in final_response[coin_id] and 'usd' in data: # fallback for simulation
                 final_response[coin_id][main_currency] = data['usd']


        if not final_response: # Should not happen if coin_list was not empty
             return {"error": f"Could not simulate price for {coins}"}
             
        return final_response

# To make this agent discoverable or usable by an orchestrator, 
# you might instantiate it or register it elsewhere,
# for example, in backend/agents/__init__.py or directly in the orchestrator.
# For now, defining the class is the main step.
