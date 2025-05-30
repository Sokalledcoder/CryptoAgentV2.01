from pydantic import BaseModel, Field
from typing import Optional, List, Any, Dict

# AG-UI Event Data Models
# Based on the document "Refining Server-Sent Events for AG-UI Protocol Compliance"

class ToolCallStartData(BaseModel):
    type: str = Field(default="TOOL_CALL_START", frozen=True)
    tool_call_id: str = Field(..., alias="toolCallId")
    tool_name: str = Field(..., alias="toolName")
    tool_args: Dict[str, Any] | str = Field(..., alias="toolArgs")
    timestamp: str

class ToolCallEndData(BaseModel):
    type: str = Field(default="TOOL_CALL_END", frozen=True)
    tool_call_id: str = Field(..., alias="toolCallId")
    tool_name: str = Field(..., alias="toolName")
    result: Optional[Any] = None
    is_error: bool = Field(default=False, alias="isError")
    error_details: Optional[Dict[str, Any] | str] = Field(default=None, alias="errorDetails")
    timestamp: str

class TextMessageContentData(BaseModel):
    type: str = Field(default="TEXT_MESSAGE_CONTENT", frozen=True)
    message_id: str = Field(..., alias="messageId")
    delta: str
    timestamp: str
    # Optional role, if needed, though often implied by context or a START event
    # role: Optional[str] = None 

# For simplicity, combining START and END for text messages if not streaming tokens yet
class TextMessageStartData(BaseModel):
    type: str = Field(default="TEXT_MESSAGE_START", frozen=True)
    message_id: str = Field(..., alias="messageId")
    role: str # e.g., "assistant", "user"
    timestamp: str

class TextMessageEndData(BaseModel):
    type: str = Field(default="TEXT_MESSAGE_END", frozen=True)
    message_id: str = Field(..., alias="messageId")
    timestamp: str

class RunLifecycleData(BaseModel):
    # For RUN_STARTED and RUN_FINISHED
    type: str # "RUN_STARTED" or "RUN_FINISHED"
    run_id: str = Field(..., alias="runId")
    status: Optional[str] = None # e.g., "completed", "failed" for RUN_FINISHED
    context: Optional[Dict[str, Any]] = None # For RUN_STARTED
    final_data: Optional[Dict[str, Any] | str] = Field(default=None, alias="finalData") # For RUN_FINISHED
    timestamp: str

class ErrorEventData(BaseModel):
    type: str = Field(default="ERROR_EVENT", frozen=True)
    message: str
    details: Optional[Dict[str, Any] | str] = None
    run_id: Optional[str] = Field(default=None, alias="runId")
    error_id: Optional[str] = Field(default=None, alias="errorId")
    timestamp: str
