Okay, based *only* on the information provided in the source materials you've shared, here is a detailed guide for the Monday Range Trading Strategy using the Key Levels SpacemanBTC IDWM indicator.

---

## A Detailed Guide to the Monday Range Trading Strategy using the Key Levels SpacemanBTC IDWM Indicator

### 1. Introduction and Strategy Overview

This guide outlines a specific trading strategy focused on using the price range established during Monday's trading session as a key reference point. The goal is to predict potential price movements and establish a directional bias for subsequent intraday trades throughout the rest of the week (typically Tuesday onwards).

The strategy relies heavily on a specific TradingView indicator, "Key Levels SpacemanBTC IDWM" (V13.1 is mentioned in the source context), which automates the identification and plotting of the crucial Monday price levels. The core concept involves observing how price interacts with these automatically plotted levels, specifically looking for a "deviation" outside the range followed by a "reclaim" back inside it.

### 2. Required Tool: Key Levels SpacemanBTC IDWM Indicator

*   **Indicator:** The "Key Levels SpacemanBTC IDWM" TradingView indicator is essential for this strategy.
*   **Core Function for this Strategy:** Its primary role here is to automatically identify and plot Monday's High and Monday's Low price levels accurately using historical data. This saves manual effort and provides clear, non-repainting visual boundaries.
*   **Other Capabilities:** While the indicator can plot numerous other levels (Daily, Weekly, Monthly Highs/Lows/Opens, Session Ranges, etc.), this specific strategy *initially* requires only the Monday High and Low levels to be active.

### 3. Core Concept: Deviation and Reclaim of Monday's Range

*   **Monday's Range:** Defined by the highest high and lowest low price points reached during Monday's trading session. These levels are automatically plotted by the indicator.
*   **Significance of Levels:** Monday's High and Low are considered significant because they may represent "potential liquidity pools" where stop-loss orders cluster.
*   **Anticipated Pattern:** The strategy anticipates a common weekly pattern where the week's high or low (often established on Tuesday or Wednesday) involves an initial move *beyond* the boundaries of Monday's Range (a "sweep" or "deviation").
*   **The Trigger:** The core idea is to visually track price as it:
    1.  **Deviates:** Moves clearly outside the indicator's plotted Monday High or Monday Low line.
    2.  **Reclaims:** Moves back inside the area between the indicator's plotted Monday High and Low lines.
*   **Bias Signal:** This deviation followed by a reclaim relative to the indicator's plotted levels is the primary trigger for establishing a directional bias (Bullish or Bearish) for the week's intraday trades.

### 4. Step-by-Step Strategy Implementation

Here is the detailed process for implementing the basic strategy using the indicator:

**Step 1: Setup the Indicator**
*   **Add Indicator:** Add the "Key Levels SpacemanBTC IDWM" (V13.1 or similar) indicator to your TradingView chart.
*   **Configure Settings:** Open the indicator's settings.
    *   **Enable Monday Range:** Ensure the "Monday Range" group is enabled, specifically the "Range" checkbox (this plots Monday High and Low).
    *   **Disable Others (Recommended):** Initially, disable other levels (Daily, Weekly, Monthly, Sessions, etc.) using the indicator's input toggles to keep the chart clean and focus solely on the Monday Range.
    *   **Customize (Optional):** Adjust colors, line style, text size, and line extension distance (using the 'Distance' input) for optimal visual clarity.

**Step 2: Identify Monday's Range**
*   **Wait for Session Completion:** Allow Monday's trading session to complete fully.
*   **Automatic Plotting:** The indicator will then automatically calculate and plot the horizontal lines for Monday's High and Monday's Low based on that day's price action.

**Step 3: Wait for Deviation (Usually Tue/Wed)**
*   **Observe Price:** Actively watch price action relative to the indicator's plotted Monday High and Low lines, typically on Tuesday or Wednesday.
*   **Identify Deviation:** Wait for price to clearly trade *outside* these lines – either above the plotted Monday High or below the plotted Monday Low.

**Step 4: Wait for Reclaim**
*   **Observe Price (After Deviation):** Once price has deviated outside the range, continue watching.
*   **Identify Reclaim:** Wait for price to move *back inside* the area between the indicator's plotted Monday High and Low lines.
*   **Confirmation Signal (Basic):** Use the hourly (H1) timeframe. The reclaim is confirmed when an hourly candle *closes* back inside the range:
    *   If price deviated below Monday Low, wait for an H1 candle to **close above** the plotted Monday Low line.
    *   If price deviated above Monday High, wait for an H1 candle to **close below** the plotted Monday High line.

**Step 5: Determine Bias & Enter Trade**
*   The reclaim event (H1 close inside) establishes the directional bias.
*   **Bullish Scenario:**
    *   *Conditions:* Price deviated below the indicator's Monday Low line, AND an hourly candle closes back above the Monday Low line.
    *   *Bias:* Bullish.
    *   *Entry:* Enter a LONG trade. The basic method suggests entering at the close of the confirming hourly candle.
*   **Bearish Scenario:**
    *   *Conditions:* Price deviated above the indicator's Monday High line, AND an hourly candle closes back below the Monday High line.
    *   *Bias:* Bearish.
    *   *Entry:* Enter a SHORT trade. The basic method suggests entering at the close of the confirming hourly candle.

**Step 6: Set Stop Loss**
*   Placement is determined by the deviation extreme relative to the indicator's reclaimed level.
*   Place the stop loss "just beyond the extreme point (wick) of the price deviation".
    *   *For Long Trades:* Place stop loss just below the lowest wick reached during the deviation below the Monday Low.
    *   *For Short Trades:* Place stop loss just above the highest wick reached during the deviation above the Monday High.

**Step 7: Set Target**
*   The primary target is defined by the opposite boundary of the Monday range, as plotted by the indicator.
*   "The primary target is the opposite indicator line representing Monday's range."
    *   *For Long Trades:* Target the indicator's Monday High line.
    *   *For Short Trades:* Target the indicator's Monday Low line.

**Step 8: Refinement (Optional)**
*   This step is optional and aims to find a more precise entry, potentially improving the risk-reward (R:R) ratio, especially after large deviations.
*   **Process:**
    *   *After* H1 reclaim confirms the bias (Step 5).
    *   Switch to a lower timeframe (e.g., M5, M15).
    *   Look for confirming price action patterns *near the reclaimed Monday level* (plotted by the indicator) or other structure *in the direction of your bias*.
*   **Examples of Confirming Price Action:**
    *   A retest of the reclaimed Monday level line.
    *   Entry off an Order Block formed during the reclaim.
    *   Entry on a Fair Value Gap (FVG) formed during the reclaim.
    *   Entry after a lower-timeframe liquidity sweep (Swing Failure Pattern - SFP) and Market Structure Shift (MSS) that aligns with the H1 bias.

### 5. Underlying Principles Leveraged

*   **Significance of Historical Levels:** Past range boundaries (like Monday's H/L) can act as future reference points.
*   **Liquidity Pools:** Highs and lows (especially Monday's) are potential areas where stop-loss orders accumulate. Price may be drawn to "sweep" this liquidity.
*   **Weekly Pattern Tendency:** The week's high or low often forms after an initial move beyond Monday's range, frequently on Tuesday or Wednesday.
*   **Deviation & Reversion:** Price deviating outside a range and then reclaiming it can signal a failed breakout or liquidity grab, suggesting a potential move towards the opposite side of the range.

### 6. Benefits of This Strategy (as described in sources)

*   Provides a relatively mechanical way to determine intraday bias based on price interaction with automatically plotted levels.
*   Offers clear entry, stop-loss, and target levels derived directly from the indicator's plotted Monday levels and the observed price action.
*   Leverages the indicator's automation for plotting accurate, non-repainting levels, saving manual effort.
*   Provides visual clarity through the indicator's plotting and customization options.
*   Potential applicability across different markets due to the indicator's wide asset compatibility (testing recommended).

### 7. Important Considerations

*   **Indicator is a Tool:** The indicator plots levels; the strategy interprets price action around them. The indicator itself does not provide buy/sell signals.
*   **Strategy Can Fail:** Market conditions change. Levels plotted by the indicator (including Monday's H/L) can be ignored or broken, especially in strong trends. The deviation might continue, or price might reverse before hitting the target.
*   **Chart Clarity:** Enabling too many of the indicator's other levels can make executing this specific strategy visually confusing. Start simple by only enabling the Monday Range.
*   **Testing Required:** Backtesting and forward testing are essential to validate how price typically interacts with the indicator's Monday levels on your specific chosen assets and timeframes.

### 8. Generalizability

*   While this guide focuses on the Monday Range, the sources note that the core deviation/reclaim concept can potentially be applied to other historical levels plotted by the "Key Levels SpacemanBTC IDWM" indicator (e.g., Daily, Weekly, Monthly Previous H/L) to establish bias on different time scales.

---

**Disclaimer:** Trading involves significant risk. This guide is based solely on the provided source materials and does not constitute financial advice. Always conduct your own research, backtesting, and risk management before implementing any trading strategy.