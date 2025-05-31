# backend/tools/mcp_wrappers.py
import anyio
import json
from typing import List # Corrected import for List

async def _run_mcp(cmd_parts: List[str], input_data: str) -> str:
    """
    Runs an MCP command-line tool, sends input_data to its STDIN,
    and returns its STDOUT as a string.
    Captures and prints STDERR.
    """
    # cmd_parts will be like ["node", "path/to/script.js"]
    # input_data will be the JSON string representing the MCP call
    # (e.g., '{"tool_name": "get-price", "arguments": {"coins": "bitcoin"}}')
    print(f"MCP Wrapper: Executing {' '.join(cmd_parts)} with input: {input_data[:200]}...") # Log input
    try:
        proc = await anyio.create_subprocess(
            cmd_parts,
            stdin=anyio.streams.text.TextSendStream,
            stdout=anyio.streams.text.TextReceiveStream,
            stderr=anyio.streams.text.TextReceiveStream 
        )
        
        async with proc.stdin:
            await proc.stdin.send(input_data + "\n")
        
        # Wait for STDOUT
        reply_lines = []
        async for line in proc.stdout:
            reply_lines.append(line.strip())
        
        # Wait for STDERR
        stderr_lines = []
        async for line in proc.stderr:
            stderr_lines.append(line.strip())

        # Process already closes after streams are done, no explicit proc.aclose() needed here
        # as it's handled by the async with proc.stdin context manager for stdin,
        # and iteration over stdout/stderr handles their closure.

        if stderr_lines:
            print(f"MCP Wrapper STDERR for {' '.join(cmd_parts)}:\n{' '.join(stderr_lines)}")
            # If there's stderr and no stdout, consider it an error
            if not reply_lines:
                return json.dumps({"error": "MCP process error", "details": "\n".join(stderr_lines)})

        reply = "".join(reply_lines)
        if not reply:
            # Handle case where stdout is empty but stderr might have info
            if stderr_lines: # This case is now covered above
                return json.dumps({"error": "MCP process produced no stdout, but had stderr", "details": "\n".join(stderr_lines)})
            return json.dumps({"error": "MCP process produced no output"})
        
        print(f"MCP Wrapper STDOUT for {' '.join(cmd_parts)}: {reply[:200]}...") # Log output
        return reply
        
    except Exception as e:
        print(f"Error running MCP command {' '.join(cmd_parts)}: {e}")
        return json.dumps({"error": f"Exception during MCP call: {str(e)}"})

# Specific FunctionTools will be added below this

from google.adk.tools import FunctionTool # Using FunctionTool from google.adk.tools
from pydantic import BaseModel, Field as PydanticField # Alias Field to avoid conflict if any
from typing import Optional # For optional fields in Pydantic models if needed

# Define input schema for LLM guidance, though run_async will take specific params
class CoinGeckoPriceToolParams(BaseModel):
    coins: str = PydanticField(description="Comma-separated list of coin IDs (e.g., \"bitcoin,ethereum\")")
    currencies: str = PydanticField(default="usd", description="Comma-separated list of currencies (e.g., \"usd,eur\")")

class CoinGeckoPriceTool(FunctionTool):
    name = "fetch_coingecko_price"
    description = "Fetches current cryptocurrency prices from CoinGecko. Provide coin IDs and target currencies."
    # The input schema for the LLM is implicitly defined by the type hints of run_async
    # and can be further specified if needed, but ADK uses the method signature.

    async def run_async(self, coins: str, currencies: str = "usd") -> str:
        """
        Wraps the CoinGecko MCP's 'get-price' tool.
        Args:
            coins: Comma-separated list of coin IDs (e.g., "bitcoin", "ethereum").
            currencies: Comma-separated list of currencies (e.g., "usd", "eur").
        Returns:
            A JSON string response from the CoinGecko MCP.
        """
        tool_name_to_call = "get-price" # The actual tool name within CoinGecko MCP
        mcp_arguments = {"coins": coins, "currencies": currencies}
        
        # Construct the JSON input string for the MCP STDIN
        # This assumes your Node.js MCP script expects a JSON object with "tool_name" and "arguments"
        mcp_input_json_string = json.dumps({
            "tool_name": tool_name_to_call,
            "arguments": mcp_arguments
        })
        
        cmd_parts = ["node", "f:/DEKSTOP MARCH25 SC/CLINE MCP 1/coingecko-mcp/dist/stdio.js"]
        
        print(f"CoinGeckoPriceTool: Calling _run_mcp with cmd='{' '.join(cmd_parts)}', input='{mcp_input_json_string}'")
        
        result_str = await _run_mcp(cmd_parts, mcp_input_json_string)
        
        # The result_str is expected to be a JSON string from the MCP.
        # No further parsing here; the LLM will receive this string.
        return result_str

# Add other MCP tool wrappers here (e.g., for Fear & Greed, Perplexity)

# --- Fear & Greed MCP Tool Wrappers ---

FEAR_AND_GREED_MCP_SCRIPT_PATH = "f:/DEKSTOP MARCH25 SC/CLINE MCP 1/fearandgreed-mcp/dist/index.js"

class FearAndGreed_GetCurrentTool(FunctionTool):
    name = "fetch_fearandgreed_current"
    description = "Gets the current Fear and Greed Index value."
    # Input: dummy parameter as per F&G MCP spec for no-parameter tools
    async def run_async(self, random_string: str = "trigger") -> str:
        mcp_input = json.dumps({
            "tool_name": "mcp_fearandgreed_get_current",
            "arguments": {"random_string": random_string} # MCP tool expects a dummy arg
        })
        cmd_parts = ["node", FEAR_AND_GREED_MCP_SCRIPT_PATH]
        return await _run_mcp(cmd_parts, mcp_input)

class FearAndGreed_InterpretValueTool(FunctionTool):
    name = "interpret_fearandgreed_value"
    description = "Interprets a Fear and Greed Index value (0-100)."
    async def run_async(self, value: int) -> str:
        mcp_input = json.dumps({
            "tool_name": "mcp_fearandgreed_interpret_value",
            "arguments": {"value": value}
        })
        cmd_parts = ["node", FEAR_AND_GREED_MCP_SCRIPT_PATH]
        return await _run_mcp(cmd_parts, mcp_input)

class FearAndGreed_CompareHistoricalTool(FunctionTool):
    name = "compare_fearandgreed_historical"
    description = "Compares the current Fear and Greed Index with historical data for a number of days (1-365, default 30)."
    async def run_async(self, days: int = 30) -> str:
        mcp_input = json.dumps({
            "tool_name": "mcp_fearandgreed_compare_with_historical",
            "arguments": {"days": days}
        })
        cmd_parts = ["node", FEAR_AND_GREED_MCP_SCRIPT_PATH]
        return await _run_mcp(cmd_parts, mcp_input)

# --- CoinGecko MCP Tool Wrapper (for global market data) ---

COINGECKO_MCP_SCRIPT_PATH = "f:/DEKSTOP MARCH25 SC/CLINE MCP 1/coingecko-mcp/dist/stdio.js" # Already defined above, but good for clarity here

class CoinGecko_GlobalMarketDataTool(FunctionTool):
    name = "fetch_coingecko_global_market_data"
    description = "Gets global cryptocurrency market data including BTC dominance and total market cap. Optionally include DeFi data."
    async def run_async(self, include_defi: bool = False) -> str:
        mcp_input = json.dumps({
            "tool_name": "global-market-data", # Actual tool name in CoinGecko MCP
            "arguments": {"include_defi": include_defi}
        })
        cmd_parts = ["node", COINGECKO_MCP_SCRIPT_PATH]
        return await _run_mcp(cmd_parts, mcp_input)

# Add Perplexity tool wrappers next if needed

import os # For PERPLEXITY_API_KEY

# --- Perplexity MCP Tool Wrapper ---

PERPLEXITY_MCP_SCRIPT_PATH = "f:/DEKSTOP MARCH25 SC/CLINE MCP 1/perplexity-mcp/build/index.js"

class PerplexityMCPTool(FunctionTool):
    name = "call_perplexity_mcp"
    description = (
        "Calls a specified tool within the Perplexity MCP server. "
        "Provide the 'tool_to_call' (e.g., 'search', 'chat_perplexity', 'get_documentation', 'find_apis', 'check_deprecated_code') "
        "and 'tool_args' as a dictionary for that tool."
    )

    async def run_async(self, tool_to_call: str, tool_args: dict) -> str:
        """
        Wraps calls to the Perplexity MCP.
        Args:
            tool_to_call: The name of the tool within Perplexity MCP to execute.
            tool_args: A dictionary of arguments for the specified Perplexity tool.
        Returns:
            A JSON string response from the Perplexity MCP.
        """
        mcp_input = json.dumps({
            "tool_name": tool_to_call,
            "arguments": tool_args
        })
        
        cmd_parts = ["node", PERPLEXITY_MCP_SCRIPT_PATH]
        
        # Prepare environment for Perplexity MCP
        mcp_env = {}
        perplexity_api_key = os.environ.get("PERPLEXITY_API_KEY")
        perplexity_model_env = os.environ.get("PERPLEXITY_MODEL")

        if perplexity_api_key:
            mcp_env["PERPLEXITY_API_KEY"] = perplexity_api_key
        else:
            # This tool wrapper itself cannot stop the call, but _run_mcp will print warnings
            # if the MCP script fails due to missing API key.
            print("PerplexityMCPTool: WARN - PERPLEXITY_API_KEY environment variable not set.")
        
        if perplexity_model_env:
            mcp_env["PERPLEXITY_MODEL"] = perplexity_model_env

        # The _run_mcp function needs to be adapted or a new one created if env needs to be passed to create_subprocess
        # For now, let's assume _run_mcp doesn't handle env, and we'd need to modify it or use a more direct anyio call here.
        # Revisiting _run_mcp to accept env:

        # For this to work, _run_mcp needs to accept an optional env dictionary.
        # Let's assume _run_mcp is modified or we use a more direct call.
        # For now, I will proceed as if _run_mcp can handle it, and we can refine _run_mcp later if needed.
        # The current _run_mcp does not take an env argument.
        # This will require modifying _run_mcp.

        # Let's construct the call assuming _run_mcp is enhanced or we make a direct call.
        # For simplicity in this step, I'll just print a note about the env.
        # The actual passing of env to the subprocess happens within _run_mcp.
        # The _run_mcp in the previous step does not have an `env` parameter.
        # This is a limitation.

        # Correct approach: Modify _run_mcp to accept 'env' or make a specific version.
        # Given the current _run_mcp, it CANNOT pass environment variables.
        # This means the Perplexity MCP script must be able to pick up PERPLEXITY_API_KEY from the environment
        # it inherits from the main Python process, or the _run_mcp must be updated.

        # The user's guide (Pattern 1) uses `anyio.create_subprocess` directly.
        # Let's adapt that for this tool, as it needs custom env.

        print(f"PerplexityMCPTool: Calling Perplexity MCP tool='{tool_to_call}' with args='{tool_args}'")
        
        try:
            proc = await anyio.create_subprocess(
                cmd_parts,
                stdin=anyio.streams.text.TextSendStream,
                stdout=anyio.streams.text.TextReceiveStream,
                stderr=anyio.streams.text.TextReceiveStream,
                env=mcp_env # Pass the environment here
            )
            
            async with proc.stdin:
                await proc.stdin.send(mcp_input + "\n")
            
            reply_lines = []
            async for line in proc.stdout:
                reply_lines.append(line.strip())
            
            stderr_lines = []
            async for line in proc.stderr:
                stderr_lines.append(line.strip())

            if stderr_lines:
                print(f"PerplexityMCPTool STDERR: {' '.join(stderr_lines)}")
                if not reply_lines:
                    return json.dumps({"error": "Perplexity MCP process error", "details": "\n".join(stderr_lines)})
            
            reply = "".join(reply_lines)
            if not reply:
                if stderr_lines:
                     return json.dumps({"error": "Perplexity MCP process produced no stdout, but had stderr", "details": "\n".join(stderr_lines)})
                return json.dumps({"error": "Perplexity MCP process produced no output"})
            
            print(f"PerplexityMCPTool STDOUT: {reply[:200]}...")
            return reply
            
        except Exception as e:
            print(f"Error in PerplexityMCPTool for tool {tool_to_call}: {e}")
            return json.dumps({"error": f"Exception during Perplexity MCP call: {str(e)}"})
