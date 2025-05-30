# CoinGecko MCP Server Tools

Here is a list of the 18 tools available in the CoinGecko MCP server:

**Price Tools:**
- `get-price`
- `convert-currency`

**Search Tools:**
- `search`
- `get-trending`

**Market Tools:**
- `get-market-data`
- `get-specific-coins`
- `get-supported-currencies`

**Historical Data Tools:**
- `get-historical-data`
- `get-price-range`

**Comparison Tools:**
- `compare-coins`
- `rank-by-metric`

**Market Analysis Tools:**
- `market-analysis`
- `volume-analysis`
- `global-market-data`

**Token Information Tools:**
- `token-details`
- `token-holders`
- `asset-platforms`
- `exchange-rates`

## How to use the tools in a prompt

To effectively use these tools, it is necessary to include the tool name in your prompt. This tells me *which* specific tool from the CoinGecko MCP server you want me to use.

**Example:**

Instead of just asking:

> What is the price of Bitcoin?

Ask:

> Use the `get-price` tool to get the price of Bitcoin.

**Concise Example:**

> `get-price` for Bitcoin

By including the tool name, you provide a clear and unambiguous instruction, ensuring I can correctly utilize the CoinGecko MCP server's capabilities to fulfill your request.
