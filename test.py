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
    arg1: str
    arg2: str
    result1: str
    result2: str
    请勿询问与面试无关内容: str

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
OUTPUT_VARIABLE = "output"

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
    Node: 输入 (input)
    """
    global_vars = get_global_vars()

    # Input type: dialog
    # 收集并验证用户输入，确保query变量完全一致

    # Input variables:
    #   - query: string
    raw_query = state.get("query", "")
    if not ComponentData.validate_input(raw_query, 'string'):
        raise ValueError(f"Invalid query type: expected string, got {type(raw_query)}")
    # 确保query一致性：不进行任何修改
    query = ComponentData.ensure_query_consistency(raw_query)
    state["query"] = query
    logger.info(f"[DataFlow] 输入节点处理query: {repr(query)}")

    return state

def llm_node(state: AgentState) -> AgentState:
    """
    Node: 大模型 (llm)
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
    system_prompt = format_prompt("""/nothink你是一个意图判断专家，根据输入{query}来判断用户的意图意图进行判断，如果意图是面试返回面试，其他意图返回闲聊，你的回复只有“面试”和“闲聊”这两种""", state, global_vars)
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

    user_prompt_template = """{query}"""
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

    # Update chat history in state
    new_messages = messages_history.copy()
    # Only add user message if not already in history
    if not new_messages or new_messages[-1].get("role") != "user":
        new_messages.append({"role": "user", "content": current_user_input})
    # Add assistant response
    new_messages.append({"role": "assistant", "content": response.content})
    state["messages"] = new_messages

    # Update state with output (各输出变量 + 统一 output 供输出节点使用)
    state["result1"] = response.content
    state["result2"] = response.content
    state["output"] = response.content  # 供输出节点默认展示

    return state

def output_node(state: AgentState) -> AgentState:
    """
    Node: 输出 (output)
    """
    global_vars = get_global_vars()

    # Output node
    output_value = state.get("output", "")
    logger.info(f"[DataFlow] 输出节点值: {repr(output_value)}")
    print(f"\nOutput: {output_value}")
    return state

def condition_node(state: AgentState) -> AgentState:
    """
    Node: 条件分支 (condition)
    """
    global_vars = get_global_vars()

    # Condition node - routing handled by conditional edges
    # 条件1: true
    return state

def output_node_2(state: AgentState) -> AgentState:
    """
    Node: 输出 (output)
    """
    global_vars = get_global_vars()

    # Output node
    output_value = state.get("请勿询问与面试无关内容", "")
    logger.info(f"[DataFlow] 输出节点值: {repr(output_value)}")
    print(f"\nOutput: {output_value}")
    return state

def llm_node_2(state: AgentState) -> AgentState:
    """
    Node: 大模型 (llm)
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
    system_prompt = format_prompt("""根据用户{query}来生成一个相关的面试问题""", state, global_vars)
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

    user_prompt_template = """{query}"""
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

    # Update chat history in state
    new_messages = messages_history.copy()
    # Only add user message if not already in history
    if not new_messages or new_messages[-1].get("role") != "user":
        new_messages.append({"role": "user", "content": current_user_input})
    # Add assistant response
    new_messages.append({"role": "assistant", "content": response.content})
    state["messages"] = new_messages

    # Update state with output (各输出变量 + 统一 output 供输出节点使用)
    state["result1"] = response.content
    state["result2"] = response.content
    state["output"] = response.content  # 供输出节点默认展示

    return state

# ========================================
# Build Graph
# ========================================

def build_graph():
    """Build and compile the LangGraph workflow."""
    workflow = StateGraph(AgentState)

    # Node: 输入 (input)
    workflow.add_node("node_1773473160968", input_node)
    # Node: 大模型 (llm)
    workflow.add_node("node_1773473166782", llm_node)
    # Node: 输出 (output)
    workflow.add_node("node_1773473176366", output_node)
    # Node: 条件分支 (condition)
    workflow.add_node("node_1773476561067", condition_node)
    # Node: 输出 (output)
    workflow.add_node("node_1773476593651", output_node_2)
    # Node: 大模型 (llm)
    workflow.add_node("node_1773476644850", llm_node_2)

    # Define edges between nodes
    workflow.set_entry_point("node_1773473160968")
    workflow.add_edge("node_1773473160968", "node_1773473166782")  # 输入 → 大模型
    workflow.add_edge("node_1773473166782", "node_1773476561067")  # 大模型 → 条件分支
    workflow.add_edge("node_1773476644850", "node_1773473176366")  # 大模型 → 输出
    def _route_node_1773476561067(state: AgentState):
        try:
            if True:
                return "node_1773476593651"
        except Exception:
            pass
        return "node_1773476644850"

    workflow.add_conditional_edges("node_1773476561067", _route_node_1773476561067)


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
        "arg1": "",
        "arg2": "",
        "result1": "",
        "result2": "",
        "output": "",
        "请勿询问与面试无关内容": "",
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