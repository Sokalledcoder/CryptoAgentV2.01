from pydantic import BaseModel
from typing import Optional, List

# Based on the understanding that ADK's InvocationContext
# expects Pydantic models for content and parts, especially
# for new_message in Runner.run_async.

class Part(BaseModel):
    text: Optional[str] = None
    # We are omitting executable_code and code_execution_result for simple text messages.
    # If ADK's InvocationContext strictly requires these fields even when None,
    # they can be added here as Optional[SomePydanticModel] = None.
    # For now, Pydantic's default behavior for missing optional fields (treating them as None)
    # should be sufficient if InvocationContext's Part model also defines them as Optional.

class Content(BaseModel):
    role: str
    parts: List[Part]

def create_simple_text_content(text: str, role: str = "user") -> Content:
    """
    Creates a Content object for a simple text message.
    """
    return Content(role=role, parts=[Part(text=text)])
