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

  

  

  

  

  

  

  

  

  

# Fear and Greed Index MCP Server Tools

  

Here is a list of the 6 tools available in the Fear and Greed Index MCP server:

  

- `mcp_fearandgreed_get_current`: Get the current Fear and Greed Index value.

- `mcp_fearandgreed_get_historical`: Get historical Fear and Greed Index data.

- `mcp_fearandgreed_get_by_timestamp`: Get the Fear and Greed Index for a specific timestamp.

- `mcp_fearandgreed_get_chart_url`: Generate a URL for a Fear and Greed Index chart.

- `mcp_fearandgreed_interpret_value`: Get an interpretation of a Fear and Greed Index value.

- `mcp_fearandgreed_compare_with_historical`: Compare the current index with the historical average.

  

## How to use the tools in a prompt

  

To effectively use these tools, it is necessary to include the tool name in your prompt. This tells me *which* specific tool from the Fear and Greed MCP server you want me to use.

  

**Example:**

  

Instead of just asking:

  

> What is the current Fear and Greed index?

  

Ask:

  

> Use the `mcp_fearandgreed_get_current` tool to get the current Fear and Greed index.

  

**Concise Example:**

  

> `mcp_fearandgreed_get_current`

  

By including the tool name, you provide a clear and unambiguous instruction, ensuring I can correctly utilize the Fear and Greed MCP server's capabilities to fulfill your request.

  

  

  

  

  

  

  

  

# Perplexity MCP Server Tools

  

Here is a list of the 4 tools available in the Perplexity MCP server (also known as MCP-researcher Server):

  

1. **Search**: Performs general search queries to get comprehensive information on any topic.

2. **Get Documentation**: Retrieves documentation and usage examples for specific technologies, libraries, or APIs.

3. **Find APIs**: Discovers and evaluates APIs that could be integrated into a project.

4. **Check Deprecated Code**: Analyzes code for deprecated features or patterns, providing migration guidance.

  

*(Note: The README also mentions a `chat_perplexity` tool, but it's not listed under the main "Tools" section in the README provided. The system prompt lists 5 tools including `chat_perplexity`. For consistency with the README structure used for the other servers, only the 4 explicitly listed tools are included here. The `chat_perplexity` tool is available for use.)*

  

## How to use the tools in a prompt

  

To effectively use these tools, it is necessary to include the tool name in your prompt. This tells me *which* specific tool from the Perplexity MCP server you want me to use.

  

**Example:**

  

Instead of just asking:

  

> Find APIs for payment processing.

  

Ask:

  

> Use the `Find APIs` tool to find APIs for payment processing.

  

**Concise Example:**

  

> `Find APIs` for payment processing

  

By including the tool name, you provide a clear and unambiguous instruction, ensuring I can correctly utilize the Perplexity MCP server's capabilities to fulfill your request.