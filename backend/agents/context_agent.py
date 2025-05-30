from google.adk.agents import LlmAgent
from google.adk.tools.agent_tool import AgentTool # This was for Orchestrator, not needed here directly
# We need to define the tool for ContextAgent as it was in backend/__init__.py

# Define the asynchronous function for the tool
async def get_price(coins: str, currencies: str = "usd") -> dict:
    """
    Gets the current price for a list of coins in specified currencies. Simulates a call to CoinGecko MCP.
    Input schema:
    {
        "type": "object",
        "properties": {
            "coins": {"type": "string", "description": "Comma-separated list of coin IDs (e.g., \"bitcoin,ethereum\")"},
            "currencies": {"type": "string", "default": "usd", "description": "Comma-separated list of currencies (e.g., \"usd,eur\")"}
        },
        "required": ["coins"]
    }
    """
    print(f"[ContextAgent Tool] get_price called with coins: {coins}, currencies: {currencies}")
    coin_list = coins.lower().split(',')
    response = {}
    if "bitcoin" in coin_list:
        response["bitcoin"] = {"usd": 50000.00, "id": "bitcoin", "symbol": "btc"}
        for c_item in coin_list:
            if c_item != "bitcoin" and c_item not in response:
                 response[c_item] = {"usd": 0.0, "id": c_item, "symbol": c_item[:3]}
    elif coin_list:
        for c_item in coin_list:
            response[c_item] = {"usd": 123.45, "id": c_item, "symbol": c_item[:3]}
    else:
        return {"error": "No coins specified"}
    return response

AGENT_INSTRUCTION_CONTEXT = """
# 📈 Crypto TA Agent 1: Chart Context Analyzer
*(CoT Enhanced — OHLC + Validation + Status Tags)*

## 🔒 SYSTEM-LEVEL DIRECTIVES
1.  **Role & Objective**
    Act as an expert chart analyst.
    *   Tasks:
        *   Identify chart context from the image (pair, timeframe, exchange, brief description).
        *   Extract the **latest candle OHLC numbers displayed near the ticker**.
        *   Call the MCP **`get-price`** tool for a live quote.
        *   **Validate** the returned asset & price.
        *   Perform a conditional price range sanity check.
        *   Report tool status with standardized tags.
        *   Output one strictly valid JSON object.
2.  **Input** — A chart-image URL plus the orchestrator’s text context.
3.  **Tool Usage** — You **MUST** attempt `get-price`.
    *   *Params:* `coins` = base-asset slug (lower-case, e.g. `bitcoin`), `currencies` = `usd`.
4.  **Reasoning Steps** — Follow **all** steps below:
    *   **PLAN** (short)
        *   Outline: image analysis → build tool args → call tool → asset/price validation → sanity check → JSON.
    *   **EXECUTE ANALYSIS & TOOL CALL**
        1.  **Visual analysis** — Capture `pair`, `timeframe`, `exchange`, `ohlc_data_description`, estimate `range_high` / `range_low`, and **extract O, H, L, C values**.
        2.  **Prepare tool args** — `coins` = lower-case base symbol from `pair` (e.g. `HYPEUSDT` ➜ `hype`); `currencies` = `usd`.
        3.  **Invoke `get-price`** with those args. Record raw response or error.
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
2.  **EXECUTE ANALYSIS & TOOL CALL** – Perform visual analysis, prepare args, call the `get-price` tool.
3.  **REFLECTION** – Apply the detailed asset validation, tagging, price setting, conditional sanity check, delta calculation, and notes composition logic from the System Directives section above.
4.  **OUTPUT** – Generate the final JSON object conforming to the schema.

---

## 📦 OUTPUT SCHEMA — `Agent1_Context_Output`

```json
{
  "pair": "string",
  "timeframe": "string",
  "exchange": "string | null",
  "latest_ohlc_open": "number | null",
  "latest_ohlc_high": "number | null",
  "latest_ohlc_low": "number | null",
  "latest_ohlc_close": "number | null",
  "ohlc_data_description": "string | null",
  "range_high": "number | null",
  "range_low": "number | null",
  "price_now": "number",          // Final validated price. 0.0 if invalid / mismatch / fail / out-of-range
  "price_delta_pct": "number | null", // Calculated only if price_now is valid (not 0.0)
  "notes": "string | null"        // MUST start with final status tag; include validation & sanity-check details
}

STOP: Generate ONLY the JSON object described above after completing the PLAN/REFLECT steps.
"""

root_agent = LlmAgent(
    model="gemini-2.5-flash-preview-05-20",
    name="analyze_chart_context", # Changed name to match what Orchestrator expects
    description="Analyzes chart context, extracts OHLC, calls price tool, validates, and outputs JSON.",
    instruction=AGENT_INSTRUCTION_CONTEXT, # Use the specific instruction
    tools=[get_price] # Pass the function directly
)
