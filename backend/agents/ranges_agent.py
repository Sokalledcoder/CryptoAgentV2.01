from google.adk.agents import LlmAgent
from google.adk.tools.function_tool import FunctionTool
from pydantic import BaseModel, Field
from typing import Optional, List, Literal

# 1. Define Pydantic Models for Output Schema (Agent3_Ranges_Output_V7)
class LevelDetail(BaseModel):
    level: Literal["R2", "R1", "MID", "S1", "S2"]
    price: Optional[float] = None
    approx: bool

class Agent3_Ranges_Output(BaseModel):
    levels: List[LevelDetail] = Field(default_factory=list)
    numeric_interaction_state: Optional[Literal[
        "outside_R2", "inside_R1_R2", "inside_R1_MID", 
        "inside_MID_S1", "inside_S1_S2", "outside_S2"
    ]] = None
    visual_touching_level: Optional[Literal["R2", "R1", "MID", "S1", "S2"]] = None
    notes: Optional[str] = None

AGENT_INSTRUCTION_RANGES = """
# 📈 Agent 3 – LuxAlgo Predictive Ranges
### v11 • "Top-Left OCR ➜ Numeric + Visual Separation + Assertions"

## 🔒 SYSTEM-LEVEL DIRECTIVES
1. **Role & Goals**
   1. Extract R2, R1, MID, S1, S2 values **from the TOP-LEFT status line** (`LuxAlgo... close <R2>...`). Use `null` if unreadable.
   2. Populate `levels` with these numbers, **adding `"approx": true`**.
   3. **Perform Numeric Sanity Check:** If `R2 > R1 > MID > S1 > S2` order violated (ignoring nulls), nullify all prices, set `approx: false`, nullify `numeric_interaction_state`, add note.
   4. Compute **`numeric_interaction_state`** (if prices valid & sanity OK) using strict numeric comparison logic. **MUST run Post-Comparison Assertion.**
   5. Independently decide **`visual_touching_level`** (candle **body** overlap check). Default to `null`.
   6. Output JSON conforming **exactly** to `Agent3_Ranges_Output_V7`. **NO extra keys/mid_slope.**

2. **Fail-Fast Rules**
   * Before emitting, verify schema keys, allowed state literals.
   * If violation detected → respond **only** with `{"error":"SCHEMA_VIOLATION"}`

3. **Numeric Interaction Logic (MUST follow order - Apply if prices valid & sanity OK)**
    *(Same python pseudo-code block as v10 for the 6 states: outside_R2 to outside_S2)*
    ```python
    # pseudo-code – you must replicate this comparison in-reflection if applicable
    if current_price is None or current_price <= 0 or any(v is None for v in (R2,R1,MID,S1,S2)):
        numeric_interaction_state = null # Handles invalid price or missing levels
    elif current_price >= R2:
        numeric_interaction_state = "outside_R2"
    elif current_price >= R1:           # < R2 implied
        numeric_interaction_state = "inside_R1_R2"
    elif current_price >= MID:          # < R1
        numeric_interaction_state = "inside_R1_MID"
    elif current_price >= S1:           # < MID
        numeric_interaction_state = "inside_MID_S1"
    elif current_price >= S2:           # < S1
        numeric_interaction_state = "inside_S1_S2"
    else: # current_price < S2
        numeric_interaction_state = "outside_S2"
    ```

4. **Post-Comparison Assertion (MANDATORY)**  # <<<< NEW SECTION
   *After you decide `numeric_interaction_state` (from step 3), run this assert table;
   if the chosen state's condition is **not** satisfied based on the extracted levels and price_now, you **must**
   set `numeric_interaction_state` to `null` and add
   `"Numeric-state assertion failed"` to `notes`.*

   | expected state        | condition that **must** be True (using extracted R2_val, R1_val etc.) |
   |-----------------------|-----------------------------------------------------------------------|
   | `outside_R2`            | `current_price >= R2_val`                                             |
   | `inside_R1_R2`          | `R1_val <= current_price < R2_val`                                    |
   | `inside_R1_MID`         | `MID_val <= current_price < R1_val`                                   |
   | `inside_MID_S1`         | `S1_val <= current_price < MID_val`                                   |
   | `inside_S1_S2`          | `S2_val <= current_price < S1_val`                                    |
   | `outside_S2`            | `current_price < S2_val`                                              |

   *If any level used in the assertion condition is `null` ➜ automatically fail the assertion.*

5. **Visual Touching Level Logic**
   * Visually inspect the **latest candle body**.
   * If body clearly overlaps R1 line -> `visual_touching_level = "R1"`.
   * Else if body clearly overlaps MID line -> `visual_touching_level = "MID"`.
   * Else if body clearly overlaps S1 line -> `visual_touching_level = "S1"`.
   * (Check R2/S2 if needed) -> `"R2"` or `"S2"`.
   * Else (no clear body overlap, not even by one pixel) -> `visual_touching_level = None`. # <<<< Touch Nudge

---

## 🔁 WORKFLOW (COT – you MUST think, but do not reveal PLAN/EXECUTE/REFLECT)

1. **PLAN**
   * Query RAG. Locate top-left text → OCR levels. **Sanity-order check**. Retrieve & validate `price_now`. Run numeric comparison. **Run assertion check.** Determine visual touching level. Prepare JSON & run fail-fast check.
2. **EXECUTE**
   * Perform RAG, OCR, sanity check, price validation, numeric comparison (conditional), **assertion check**, visual touch check. Record results internally.
3. **REFLECT** (internal, unseen)
   * Record OCR values & sanity outcome. Record `price_now` validity.
   * **Detail numeric comparisons.** State initial numeric state choice. **State outcome of MANDATORY assertion check.** Determine final `numeric_interaction_state` (potentially nullified by assertion).
   * State final `visual_touching_level`.
   * Prepare JSON, double-check against schema & fail-fast rules.
4. **OUTPUT**
   Emit **only** the JSON object (or `SCHEMA_VIOLATION`).

---

## 📦 OUTPUT SCHEMA (Agent3_Ranges_Output_V7 - Reminder) - Defined as Pydantic Model

STOP – Output only JSON (or SCHEMA_VIOLATION).
Perform ALL checks: Sanity Order, Numeric Comparison, Assertion, Visual Touch.
"""

class RangesAgent(LlmAgent):
    def __init__(self):
        super().__init__(
            model="gemini-2.5-flash-preview-05-20", # Assuming vision capabilities
            name="analyze_predictive_ranges",
            description="Analyzes LuxAlgo Predictive Ranges levels, price interaction states, and visual touching levels.",
            instruction=AGENT_INSTRUCTION_RANGES,
            output_schema=Agent3_Ranges_Output
        )

        search_tool = FunctionTool(func=self._simulated_file_search)
        search_tool.name = "file_search_tool"
        search_tool.description = "Simulates a RAG/FileSearch tool for querying knowledge base about LuxAlgo Predictive Ranges."
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
        Simulates a RAG/FileSearch tool for querying knowledge base about LuxAlgo Predictive Ranges.
        """
        print(f"[RangesAgent Tool SIMULATION] _simulated_file_search called with query: {query}")
        
        query_lower = query.lower()
        if "luxalgo" in query_lower or "predictive" in query_lower or "ranges" in query_lower:
            return {
                "results": [
                    {
                        "content": "LuxAlgo Predictive Ranges displays R2, R1, MID, S1, S2 levels in the top-left status line. These levels act as dynamic support and resistance zones. The indicator shows current price interaction with these levels.",
                        "source": "LuxAlgo_Predictive_Ranges.md"
                    }
                ]
            }
        else:
            return {
                "results": [
                    {
                        "content": "General range analysis involves identifying key support and resistance levels and price interaction with these zones.",
                        "source": "Range_Analysis.md"
                    }
                ]
            }
