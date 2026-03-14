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
import logging

# ========================================
# State Definition
# ========================================

class AgentState(TypedDict):
    """State definition for the LangGraph workflow."""
    messages: List[Dict[str, str]]
    query: str
    output: str
    intent_result: str
    final_output: str

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

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Workflow Configuration
RUN_MODE = "single"
INTERACTION_TYPE = "input"
ENABLE_DIALOG_INPUT = True
ENABLE_FORM_INPUT = False
ENABLE_FILE_UPLOAD = False
OUTPUT_VARIABLE = "final_output"

# ========================================
# Data Validation & Component Communication
# ========================================

class ComponentData:
    """组件数据验证和通信接口类。"""
    @staticmethod
    def validate_input(data: Any, expected_type: str = 'str') -> bool:
        """验证输入数据的类型和格式。"""
        try:
            if expected_type == 'str':
                return isinstance(data, str)
            elif expected_type == 'number':
                return isinstance(data, (int, float))
            elif expected_type == 'boolean':
                return isinstance(data, bool)
            elif expected_type == 'object':
                return isinstance(data, dict)
            elif expected_type == 'array':
                return isinstance(data, list)
            return True
        except Exception:
            return False

    @staticmethod
    def ensure_query_consistency(user_input: str) -> str:
        """确保query变量与用户输入完全一致，不进行任何修改。"""
        logger.debug(f"[DataFlow] 接收用户输入: {repr(user_input)}")
        return user_input

# ========================================
# Node Functions
# ========================================

def input_node(state: AgentState) -> AgentState:
    """
    Node: 用户输入 (input)
    """
    global_vars = get_global_vars()

    # Input type: dialog
    # 收集并验证用户输入，确保query变量完全一致

    # 默认：处理'query'变量
    raw_query = state.get("query", "")
    if not ComponentData.validate_input(raw_query, "str"):
        raise ValueError(f"Invalid query type: expected str, got {type(raw_query)}")
    # 确保query一致性：完全保留原始输入
    query = ComponentData.ensure_query_consistency(raw_query)
    state["query"] = query
    logger.info(f"[DataFlow] 输入节点处理query: {repr(query)}")

    return state

def llm_node(state: AgentState) -> AgentState:
    """
    Node: 意图判断(不显示) (llm)
    """
    global_vars = get_global_vars()

    # Initialize LLM: Qwen3-32B-FP8
    llm = ChatOpenAI(
        base_url="http://1.194.201.134:50178/v1",
        api_key="kJ94sWuDogW49zapnePumpVRQgFcz2O1jb3S7C35ZoHp8HRnVdz1CryyyZftsEmFHFKS4egaoY1Jyvvi",
        model="Qwen3-32B-FP8",
        temperature=0.1,
    )

    # Build messages from chat history
    chat_messages = []
    system_prompt = format_prompt("""你是意图判断专家。只返回'面试'或'闲聊'两个字，不要有其他内容。""", state, global_vars)
    chat_messages.append(SystemMessage(content=system_prompt))

    # Add previous messages from state
    messages_history = state.get("messages", [])
    for msg in messages_history:
        if msg["role"] == "user":
            chat_messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            chat_messages.append(AIMessage(content=msg["content"]))

    # Get current user input - 确保query变量完全一致
    raw_query = state.get("query", "")
    logger.info(f"[DataFlow] LLM节点接收到query: {repr(raw_query)}")
    # 验证query数据类型
    if not ComponentData.validate_input(raw_query, 'str'):
        raise ValueError(f"Invalid query type: expected str, got {type(raw_query)}")
    # 确保query一致性：直接使用，不进行任何修改
    query = ComponentData.ensure_query_consistency(raw_query)

    user_prompt_template = """{{query}}"""
    logger.info(f"[DataFlow] 使用用户提示词模板: {repr(user_prompt_template)}")
    # 确保query被嵌入到用户提示词中
    user_prompt_formatted = format_prompt(user_prompt_template, state, global_vars)
    logger.info(f"[DataFlow] 格式化后的用户提示词: {repr(user_prompt_formatted)}")
    current_user_input = user_prompt_formatted

    # Only add current user input if not already in history (or if history is empty)
    if not messages_history or messages_history[-1].get("role") != "user":
        chat_messages.append(HumanMessage(content=current_user_input))

    # Invoke LLM
    response = llm.invoke(chat_messages)

    show_in_chat = False
    logger.info(f"[DataFlow] showInChat 配置: {show_in_chat}")
    # Update chat history in state
    new_messages = messages_history.copy()
    # Only add user message if not already in history and showInChat is True
    if show_in_chat and (not new_messages or new_messages[-1].get("role") != "user"):
        new_messages.append({"role": "user", "content": current_user_input})
    # Add assistant response only if showInChat is True
    if show_in_chat:
        new_messages.append({"role": "assistant", "content": response.content})
    state["messages"] = new_messages

    # Update state with output (各输出变量 + 统一 output 供输出节点使用)
    state["intent_result"] = response.content
    state["output"] = response.content  # 供输出节点默认展示

    return state

def condition_node(state: AgentState) -> AgentState:
    """
    Node: 条件分支 (condition)
    """
    global_vars = get_global_vars()

    # Condition node - routing handled by conditional edges
    # 面试模式: True
    return state

def llm_node_2(state: AgentState) -> AgentState:
    """
    Node: 面试问题(显示) (llm)
    """
    global_vars = get_global_vars()

    # Initialize LLM: Qwen3-32B-FP8
    llm = ChatOpenAI(
        base_url="http://1.194.201.134:50178/v1",
        api_key="kJ94sWuDogW49zapnePumpVRQgFcz2O1jb3S7C35ZoHp8HRnVdz1CryyyZftsEmFHFKS4egaoY1Jyvvi",
        model="Qwen3-32B-FP8",
        temperature=0.7,
    )

    # Build messages from chat history
    chat_messages = []
    system_prompt = format_prompt("""你是专业的面试官。请根据用户的输入生成一个相关的面试问题。""", state, global_vars)
    chat_messages.append(SystemMessage(content=system_prompt))

    # Add previous messages from state
    messages_history = state.get("messages", [])
    for msg in messages_history:
        if msg["role"] == "user":
            chat_messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            chat_messages.append(AIMessage(content=msg["content"]))

    # Get current user input - 确保query变量完全一致
    raw_query = state.get("query", "")
    logger.info(f"[DataFlow] LLM节点接收到query: {repr(raw_query)}")
    # 验证query数据类型
    if not ComponentData.validate_input(raw_query, 'str'):
        raise ValueError(f"Invalid query type: expected str, got {type(raw_query)}")
    # 确保query一致性：直接使用，不进行任何修改
    query = ComponentData.ensure_query_consistency(raw_query)

    user_prompt_template = """用户输入: {{query}}"""
    logger.info(f"[DataFlow] 使用用户提示词模板: {repr(user_prompt_template)}")
    # 确保query被嵌入到用户提示词中
    user_prompt_formatted = format_prompt(user_prompt_template, state, global_vars)
    logger.info(f"[DataFlow] 格式化后的用户提示词: {repr(user_prompt_formatted)}")
    current_user_input = user_prompt_formatted

    # Only add current user input if not already in history (or if history is empty)
    if not messages_history or messages_history[-1].get("role") != "user":
        chat_messages.append(HumanMessage(content=current_user_input))

    # Invoke LLM
    response = llm.invoke(chat_messages)

    show_in_chat = True
    logger.info(f"[DataFlow] showInChat 配置: {show_in_chat}")
    # Update chat history in state
    new_messages = messages_history.copy()
    # Only add user message if not already in history and showInChat is True
    if show_in_chat and (not new_messages or new_messages[-1].get("role") != "user"):
        new_messages.append({"role": "user", "content": current_user_input})
    # Add assistant response only if showInChat is True
    if show_in_chat:
        new_messages.append({"role": "assistant", "content": response.content})
    state["messages"] = new_messages

    # Update state with output (各输出变量 + 统一 output 供输出节点使用)
    state["final_output"] = response.content
    state["output"] = response.content  # 供输出节点默认展示

    return state

def llm_node_3(state: AgentState) -> AgentState:
    """
    Node: 闲聊模式(显示) (llm)
    """
    global_vars = get_global_vars()

    # Initialize LLM: Qwen3-32B-FP8
    llm = ChatOpenAI(
        base_url="http://1.194.201.134:50178/v1",
        api_key="kJ94sWuDogW49zapnePumpVRQgFcz2O1jb3S7C35ZoHp8HRnVdz1CryyyZftsEmFHFKS4egaoY1Jyvvi",
        model="Qwen3-32B-FP8",
        temperature=0.7,
    )

    # Build messages from chat history
    chat_messages = []
    system_prompt = format_prompt("""你是友好的聊天助手。请与用户愉快地聊天。""", state, global_vars)
    chat_messages.append(SystemMessage(content=system_prompt))

    # Add previous messages from state
    messages_history = state.get("messages", [])
    for msg in messages_history:
        if msg["role"] == "user":
            chat_messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            chat_messages.append(AIMessage(content=msg["content"]))

    # Get current user input - 确保query变量完全一致
    raw_query = state.get("query", "")
    logger.info(f"[DataFlow] LLM节点接收到query: {repr(raw_query)}")
    # 验证query数据类型
    if not ComponentData.validate_input(raw_query, 'str'):
        raise ValueError(f"Invalid query type: expected str, got {type(raw_query)}")
    # 确保query一致性：直接使用，不进行任何修改
    query = ComponentData.ensure_query_consistency(raw_query)

    user_prompt_template = """{{query}}"""
    logger.info(f"[DataFlow] 使用用户提示词模板: {repr(user_prompt_template)}")
    # 确保query被嵌入到用户提示词中
    user_prompt_formatted = format_prompt(user_prompt_template, state, global_vars)
    logger.info(f"[DataFlow] 格式化后的用户提示词: {repr(user_prompt_formatted)}")
    current_user_input = user_prompt_formatted

    # Only add current user input if not already in history (or if history is empty)
    if not messages_history or messages_history[-1].get("role") != "user":
        chat_messages.append(HumanMessage(content=current_user_input))

    # Invoke LLM
    response = llm.invoke(chat_messages)

    show_in_chat = True
    logger.info(f"[DataFlow] showInChat 配置: {show_in_chat}")
    # Update chat history in state
    new_messages = messages_history.copy()
    # Only add user message if not already in history and showInChat is True
    if show_in_chat and (not new_messages or new_messages[-1].get("role") != "user"):
        new_messages.append({"role": "user", "content": current_user_input})
    # Add assistant response only if showInChat is True
    if show_in_chat:
        new_messages.append({"role": "assistant", "content": response.content})
    state["messages"] = new_messages

    # Update state with output (各输出变量 + 统一 output 供输出节点使用)
    state["final_output"] = response.content
    state["output"] = response.content  # 供输出节点默认展示

    return state

def output_node(state: AgentState) -> AgentState:
    """
    Node: 最终输出 (output)
    """
    global_vars = get_global_vars()

    # Output node
    output_value = state.get("final_output", "")
    logger.info(f"[DataFlow] 输出节点值: {repr(output_value)}")
    print(f"\nOutput: {output_value}")
    return state

# ========================================
# Build Graph
# ========================================

def build_graph():
    """Build and compile the LangGraph workflow."""
    workflow = StateGraph(AgentState)

    # Node: 用户输入 (input)
    workflow.add_node("input_node", input_node)
    # Node: 意图判断(不显示) (llm)
    workflow.add_node("intent_llm", llm_node)
    # Node: 条件分支 (condition)
    workflow.add_node("condition_node", condition_node)
    # Node: 面试问题(显示) (llm)
    workflow.add_node("interview_llm", llm_node_2)
    # Node: 闲聊模式(显示) (llm)
    workflow.add_node("chat_llm", llm_node_3)
    # Node: 最终输出 (output)
    workflow.add_node("output_node", output_node)

    # Define edges between nodes
    workflow.add_edge("input_node", "intent_llm")  # 用户输入 → 意图判断(不显示)
    workflow.add_edge("intent_llm", "condition_node")  # 意图判断(不显示) → 条件分支
    workflow.add_edge("interview_llm", "output_node")  # 面试问题(显示) → 最终输出
    workflow.add_edge("chat_llm", "output_node")  # 闲聊模式(显示) → 最终输出
    def _route_condition_node(state: AgentState):
        try:
            if str('面试') in str(state.get("intent_result", "")):
                return "interview_llm"
        except Exception:
            pass
        return "chat_llm"

    workflow.add_conditional_edges("condition_node", _route_condition_node)

    # Auto-set entry point (no start node connected)
    workflow.set_entry_point("input_node")

    # Compile and return the graph
    return workflow.compile()

# ========================================
# Helper Functions
# ========================================

def format_prompt(template: str, state: AgentState, global_vars: Dict[str, Any]) -> str:
    """
    Format a prompt template with state and global variables.
    Supports {{variable}} syntax for variable substitution.
    Special handling for query variable to ensure consistency.
    """
    logger.info(f"[DataFlow] 开始格式化提示词，模板长度: {len(template)}")
    result = template
    # Substitute state variables
    for key, value in state.items():
        if key == "query":
            # 对query变量特殊处理：确保完全一致，不进行任何转换
            logger.debug(f"[DataFlow] 替换query变量: {repr(value)}")
            result = result.replace(f"{{{{{key}}}}}", str(value) if value is not None else "")
        else:
            result = result.replace(f"{{{{{key}}}}}", str(value) if value is not None else "")
    # Substitute global variables
    for key, value in global_vars.items():
        if callable(value):
            resolved_value = value()
        else:
            resolved_value = value
        result = result.replace(f"{{{{{key}}}}}", str(resolved_value) if resolved_value is not None else "")
    logger.debug(f"[DataFlow] 提示词格式化完成，结果: {repr(result[:100])}...")
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

def run_interactive_mode():
    """运行交互式对话模式。"""
    app = build_graph()
    current_state: AgentState = {
        "messages": [],
        "query": "",
        "intent_result": "",
        "final_output": "",
        "output": "",
    }

    print("\n=== 交互式对话模式 ===")
    print("输入 'quit' 或 'exit' 退出程序")
    print("-" * 50)

    while True:
        try:
            user_input = input("\n用户: ")
            if user_input.lower() in ["quit", "exit", "q"]:
                print("\n再见!")
                break
            if not user_input.strip():
                print("请输入有效内容!")
                continue

            logger.info(f"[Interactive] 用户输入: {repr(user_input)}")

            current_state["query"] = user_input
            logger.info(f'[Interactive] 当前状态 query: {repr(current_state["query"])}')

            print("\n正在处理...")
            current_state = app.invoke(current_state)

        except KeyboardInterrupt:
            print("\n\n程序已被用户中断")
            break
        except Exception as e:
            logger.error(f"运行错误: {e}")
            print(f"\n错误: {e}")
            continue

if __name__ == "__main__":
    print("=" * 50)
    print("LangFlow Workflow")
    print("=" * 50)

    # ========================================
    # 直接启动交互式对话模式
    # ========================================
    run_interactive_mode()