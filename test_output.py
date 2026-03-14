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
    query: str
    output: str

# ========================================
# Global Variables & Configuration
# ========================================

import os

# API Key Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

GLOBAL_VARS = {
    "user_info": {},
    "current_time": lambda: datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "chat_history": [],
    "message": "",
    "dialog_files_content": "",
    "dialog_image_files": [],
}

# ========================================
# Node Functions
# ========================================

def input(state: AgentState) -> AgentState:
    """
    Node: 输入 (input)
    """
    global_vars = get_global_vars()

    # Input type: dialog
    # Input variables:
    #   - query: string
    return state

def llm_node(state: AgentState) -> AgentState:
    """
    Node: 大模型 (llm)
    """
    global_vars = get_global_vars()

    # Initialize LLM: gpt-3.5-turbo
    llm = ChatOpenAI(
        model="gpt-3.5-turbo",
        temperature=0.7,
    )

    # Build prompt template
    system_prompt = format_prompt("""You are a helpful assistant.""", state, global_vars)
    user_prompt = format_prompt("""{{query}}""", state, global_vars)
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", user_prompt),
    ])

    # Create chain and invoke
    chain = prompt | llm
    response = chain.invoke(state)

    # Update state with output
    state["output"] = response.content

    return state

def code_node(state: AgentState) -> AgentState:
    """
    Node: 代码 (code)
    """
    global_vars = get_global_vars()

    # Extract inputs from state
    output = state.get("output", "")

    # Execute custom code
    try:
        result = state['output'].upper()
        state['output'] = result
    except Exception as e:
        print(f"Error in 代码: {e}")
        raise

    # Update state with outputs
    # state["output"] = ... (set in custom code)

    return state

def output(state: AgentState) -> AgentState:
    """
    Node: 输出 (output)
    """
    global_vars = get_global_vars()

    # Output node
    output_value = state.get("output", "")
    print(f"\nOutput: {output_value}")
    return state

# ========================================
# Build Graph
# ========================================

def build_graph():
    """Build and compile the LangGraph workflow."""
    workflow = StateGraph(AgentState)

    # Node: 输入 (input)
    workflow.add_node("input", input)
    # Node: 大模型 (llm)
    workflow.add_node("llm_node", llm_node)
    # Node: 代码 (code)
    workflow.add_node("code_node", code_node)
    # Node: 输出 (output)
    workflow.add_node("output", output)

    # Define edges between nodes
    workflow.set_entry_point("input")
    workflow.add_edge("input", "llm_node")  # 输入 → 大模型
    workflow.add_edge("llm_node", "code_node")  # 大模型 → 代码
    workflow.add_edge("code_node", "output")  # 代码 → 输出
    workflow.add_edge("output", END)

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
        "query": "Hello, how can I help you today?",
        "output": "",
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