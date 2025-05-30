# Perplexity MCP Server Tools

Here is a list of the 4 tools available in the Perplexity MCP server (also known as MCP-researcher Server):

1.  **Search**: Performs general search queries to get comprehensive information on any topic.
2.  **Get Documentation**: Retrieves documentation and usage examples for specific technologies, libraries, or APIs.
3.  **Find APIs**: Discovers and evaluates APIs that could be integrated into a project.
4.  **Check Deprecated Code**: Analyzes code for deprecated features or patterns, providing migration guidance.

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
