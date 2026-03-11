# ========================================
# LangFlow Generated Code
# ========================================

# Import necessary libraries
from typing import TypedDict, Dict, Any, Optional, List
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
import datetime
import json

# ========================================
# State Definition
# ========================================

class AgentState(TypedDict):
    """State definition for the LangGraph workflow."""
    arg1: str
    arg2: str
    result1: str
    result2: str

# ========================================
# Global Variables & Configuration
# ========================================

GLOBAL_VARS = {
    "user_info": {},
    "current_time": lambda: datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "chat_history": [],
    "message": "",
    "dialog_files_content": "",
    "dialog_image_files": [],
}

# Workflow Configuration
RUN_MODE = "single"
INTERACTION_TYPE = "input"
ENABLE_DIALOG_INPUT = True
ENABLE_FORM_INPUT = False
ENABLE_FILE_UPLOAD = False
OUTPUT_VARIABLE = "output"

# ========================================
# Node Functions
# ========================================

def condition_node(state: AgentState) -> AgentState:
    """
    Node: 条件分支 (condition)
    """
    global_vars = get_global_vars()

    # Condition node - routing handled by conditional edges
    # 使用大模型: state.get('use_llm', True)
    return state

def llm_node(state: AgentState) -> AgentState:
    """
    Node: 大模型 (llm)
    """
    global_vars = get_global_vars()

    # Initialize LLM: vllm2/Qwen3-32B-FP8
    llm = ChatOpenAI(
        model="vllm2/Qwen3-32B-FP8",
        temperature=0.7,
    )

    # Build prompt template
    # Fallback: simple prompt
    response = llm.invoke(state.get("query", ""))

    # Update state with output
    state["result1"] = response.content
    state["result2"] = response.content

    return state

def code_node(state: AgentState) -> AgentState:
    """
    Node: 代码 (code)
    """
    global_vars = get_global_vars()

    # Extract inputs from state
    arg1 = state.get("arg1", "")
    arg2 = state.get("arg2", "")

    # Execute custom code
    try:
        def main(arg1: str, arg2: str) -> dict:
            # 在此编写自定义逻辑，例如数据处理、API调用等
            return {"result1": arg1, "result2": arg2}
    except Exception as e:
        print(f"Error in 代码: {e}")
        raise

    # Update state with outputs
    # state["result1"] = ... (set in custom code)
    # state["result2"] = ... (set in custom code)

    return state

def output_node(state: AgentState) -> AgentState:
    """
    Node: 输出 (output)
    """
    global_vars = get_global_vars()

    # Output node
    output_value = state.get("result1", "")
    print(f"\nOutput: {output_value}")
    return state

# ========================================
# Build Graph
# ========================================

def build_graph():
    """Build and compile the LangGraph workflow."""
    workflow = StateGraph(AgentState)

    # Node: 条件分支 (condition)
    workflow.add_node("condition_node", condition_node)
    # Node: 大模型 (llm)
    workflow.add_node("llm_node", llm_node)
    # Node: 代码 (code)
    workflow.add_node("code_node", code_node)
    # Node: 输出 (output)
    workflow.add_node("output_node", output_node)

    # Define edges between nodes
    workflow.set_entry_point("condition_node")
    workflow.add_edge("condition_node", "llm_node")  # 条件分支 → 使用大模型
    workflow.add_edge("condition_node", "code_node")  # 条件分支 → 使用大模型
    workflow.add_edge("llm_node", "output_node")  # 大模型 → 输出
    workflow.add_edge("code_node", "output_node")  # 代码 → 输出
    workflow.add_edge("output_node", END)

    # Compile and return the graph
    return workflow.compile()

# ========================================
# Helper Functions
# ========================================

def format_prompt(template: str, state: AgentState, global_vars: Dict[str, Any]) -> str:
    """
    Format a prompt template with state and global variables.
    Supports {{variable}} syntax for variable substitution.
    """
    result = template
    # Substitute state variables
    for key, value in state.items():
        result = result.replace(f"{{{{{key}}}}}", str(value) if value is not None else "")
    # Substitute global variables
    for key, value in global_vars.items():
        if callable(value):
            resolved_value = value()
        else:
            resolved_value = value
        result = result.replace(f"{{{{{key}}}}}", str(resolved_value) if resolved_value is not None else "")
    return result

def get_global_vars() -> Dict[str, Any]:
    """Get a copy of global variables with evaluated functions."""
    result = {}
    for key, value in GLOBAL_VARS.items():
        if callable(value):
            result[key] = value()
        else:
            result[key] = value
    return result

# ========================================
# Run the Workflow
# ========================================

if __name__ == "__main__":
    print("=" * 50)
    print("LangFlow Workflow")
    print("=" * 50)

    # Display opening message if configured
    if 'OPENING_MESSAGE' in locals() and OPENING_MESSAGE:
        print("\nOpening Message:")
        print("-" * 30)
        print(OPENING_MESSAGE)
        print("-" * 30)

    # Build the graph
    app = build_graph()

    # Example usage
    print("\nExample Usage:")
    initial_state: AgentState = {
        "arg1": "",
        "arg2": "",
        "result1": "",
        "result2": "",
    }

    print("\nRunning workflow...")
    result = app.invoke(initial_state)

    print("\nWorkflow Result:")
    print("-" * 30)
    if 'OUTPUT_VARIABLE' in locals():
        print(result.get(OUTPUT_VARIABLE, result))
    else:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    print("-" * 30)

    print("\nDone!")