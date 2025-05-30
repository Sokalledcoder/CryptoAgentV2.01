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
