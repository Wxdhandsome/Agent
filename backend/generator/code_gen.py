import sys
import os
import logging
from typing import Dict, Any, List

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from nodes import NodeType
from config.chat_openai_config import CHAT_OPENAI_BASE_URL, CHAT_OPENAI_API_KEY


class DataValidationError(Exception):
    """数据验证错误异常"""
    pass


class CodeGenerator:
    def __init__(self):
        pass

    def generate(self, graph_data: Dict[str, Any], workflow_config: Dict[str, Any] = None) -> str:
        state_fields = graph_data.get("state", {}).get("fields", {})
        nodes = graph_data.get("nodes", [])
        edges = graph_data.get("edges", [])
        workflow_config = workflow_config or {}

        code_lines = []
        code_lines.append("# ========================================")
        code_lines.append("# LangFlow Generated Code")
        code_lines.append("# ========================================")
        code_lines.append("")
        code_lines.append("# Import necessary libraries")
        code_lines.append("from typing import TypedDict, Dict, Any, Optional, List")
        code_lines.append("from langgraph.graph import StateGraph, END")
        code_lines.append("from langchain_openai import ChatOpenAI")
        code_lines.append("from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder")
        code_lines.append("from langchain_core.messages import HumanMessage, AIMessage, SystemMessage")
        code_lines.append("import datetime")
        code_lines.append("import json")
        code_lines.append("import logging")
        code_lines.append("")

        state_code, state_field_names = self._generate_state(state_fields, nodes)
        code_lines.extend(state_code)
        code_lines.append("")

        code_lines.append("# ========================================")
        code_lines.append("# Global Variables & Configuration")
        code_lines.append("# ========================================")
        code_lines.append("")
        code_lines.append("GLOBAL_VARS = {")
        code_lines.append('    "user_info": {},')
        code_lines.append('    "current_time": lambda: datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),')
        code_lines.append('    "chat_history": [],')
        code_lines.append('    "message": "",')
        code_lines.append('    "dialog_files_content": "",')
        code_lines.append('    "dialog_image_files": [],')
        code_lines.append("}")
        code_lines.append("")
        code_lines.append("# Setup logging")
        code_lines.append("logging.basicConfig(")
        code_lines.append("    level=logging.INFO,")
        code_lines.append('    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"')
        code_lines.append(")")
        code_lines.append("logger = logging.getLogger(__name__)")
        code_lines.append("")

        has_opening_message = bool(workflow_config and workflow_config.get("openingMessage"))
        if workflow_config:
            code_lines.append("# Workflow Configuration")
            if has_opening_message:
                opening_msg = workflow_config.get("openingMessage", "").replace("\\", "\\\\").replace('"""', '\\"\\"\\"')
                code_lines.append(f'OPENING_MESSAGE = """{opening_msg}"""')
            code_lines.append(f'RUN_MODE = "{workflow_config.get("runMode", "single")}"')
            code_lines.append(f'INTERACTION_TYPE = "{workflow_config.get("interactionType", "input")}"')
            code_lines.append(f'ENABLE_DIALOG_INPUT = {workflow_config.get("enableDialogInput", True)}')
            code_lines.append(f'ENABLE_FORM_INPUT = {workflow_config.get("enableFormInput", False)}')
            code_lines.append(f'ENABLE_FILE_UPLOAD = {workflow_config.get("enableFileUpload", False)}')
            if workflow_config.get("enableFileUpload"):
                code_lines.append(f'FILE_SIZE_LIMIT = {workflow_config.get("fileSizeLimit", 15000)}')
                code_lines.append(f'FILE_TYPES = "{workflow_config.get("fileTypes", "all")}"')
            code_lines.append(f'OUTPUT_VARIABLE = "{workflow_config.get("outputVariable", "output")}"')
            if workflow_config.get("presetQuestions"):
                code_lines.append(f'PRESET_QUESTIONS = {workflow_config.get("presetQuestions", [])}')
        code_lines.append("")

        node_id_to_name = self._build_node_id_to_name(nodes)

        code_lines.append("# ========================================")
        code_lines.append("# Data Validation & Component Communication")
        code_lines.append("# ========================================")
        code_lines.append("")
        code_lines.append("class ComponentData:")
        code_lines.append('    """组件数据验证和通信接口类。"""')
        code_lines.append("    @staticmethod")
        code_lines.append("    def validate_input(data: Any, expected_type: str = 'str') -> bool:")
        code_lines.append('        """验证输入数据的类型和格式。"""')
        code_lines.append("        try:")
        code_lines.append("            if expected_type == 'str':")
        code_lines.append("                return isinstance(data, str)")
        code_lines.append("            elif expected_type == 'number':")
        code_lines.append("                return isinstance(data, (int, float))")
        code_lines.append("            elif expected_type == 'boolean':")
        code_lines.append("                return isinstance(data, bool)")
        code_lines.append("            elif expected_type == 'object':")
        code_lines.append("                return isinstance(data, dict)")
        code_lines.append("            elif expected_type == 'array':")
        code_lines.append("                return isinstance(data, list)")
        code_lines.append("            return True")
        code_lines.append("        except Exception:")
        code_lines.append("            return False")
        code_lines.append("")
        code_lines.append("    @staticmethod")
        code_lines.append("    def ensure_query_consistency(user_input: str) -> str:")
        code_lines.append('        """确保query变量与用户输入完全一致，不进行任何修改。"""')
        code_lines.append('        logger.debug(f"[DataFlow] 接收用户输入: {repr(user_input)}")')
        code_lines.append("        return user_input")
        code_lines.append("")

        code_lines.append("# ========================================")
        code_lines.append("# Node Functions")
        code_lines.append("# ========================================")
        code_lines.append("")

        for node in nodes:
            node_type = node.get("type")
            if node_type not in ["start", "end"]:
                nid = node.get("id")
                func_name = node_id_to_name.get(nid, nid)
                node_code = self._generate_node(node, func_name)
                code_lines.extend(node_code)
                code_lines.append("")

        code_lines.append("# ========================================")
        code_lines.append("# Build Graph")
        code_lines.append("# ========================================")
        code_lines.append("")
        code_lines.append("def build_graph():")
        code_lines.append('    """Build and compile the LangGraph workflow."""')
        code_lines.append("    workflow = StateGraph(AgentState)")
        code_lines.append("")
        
        for node in nodes:
            node_type = node.get("type")
            if node_type not in ["start", "end"]:
                node_id = node["id"]
                node_label = node.get("label", node_id)
                func_name = node_id_to_name.get(node_id, node_id)
                code_lines.append(f'    # Node: {node_label} ({node_type})')
                code_lines.append(f'    workflow.add_node("{node_id}", {func_name})')
        code_lines.append("")

        code_lines.append("    # Define edges between nodes")
        condition_node_ids = {n["id"] for n in nodes if n.get("type") == "condition"}
        normal_edges = [e for e in edges if e.get("from") not in condition_node_ids]
        condition_edges = [e for e in edges if e.get("from") in condition_node_ids]

        has_entry_point = False
        for edge in normal_edges:
            edge_code = self._generate_edge(edge, nodes)
            if edge_code:
                code_lines.append(f"    {edge_code}")
                if "set_entry_point" in edge_code:
                    has_entry_point = True

        for cond_node_id in condition_node_ids:
            out_edges = [e for e in condition_edges if e.get("from") == cond_node_id]
            cond_node_data = next((n for n in nodes if n["id"] == cond_node_id), None)
            if cond_node_data and out_edges:
                cond_lines = self._generate_conditional_edges(cond_node_id, cond_node_data, out_edges, nodes)
                code_lines.extend(cond_lines)
        
        code_lines.append("")
        if not has_entry_point:
            first_non_start_end_node = None
            for node in nodes:
                node_type = node.get("type")
                if node_type not in ["start", "end"]:
                    first_non_start_end_node = node
                    break
            if first_non_start_end_node:
                code_lines.append("    # Auto-set entry point (no start node connected)")
                code_lines.append(f'    workflow.set_entry_point("{first_non_start_end_node["id"]}")')

        code_lines.append("")
        code_lines.append("    # Compile and return the graph")
        code_lines.append("    return workflow.compile()")
        code_lines.append("")

        code_lines.append("# ========================================")
        code_lines.append("# Helper Functions")
        code_lines.append("# ========================================")
        code_lines.append("")
        code_lines.append("def format_prompt(template: str, state: AgentState, global_vars: Dict[str, Any]) -> str:")
        code_lines.append('    """')
        code_lines.append("    Format a prompt template with state and global variables.")
        code_lines.append('    Supports {{variable}} syntax for variable substitution.')
        code_lines.append('    Special handling for query variable to ensure consistency.')
        code_lines.append('    """')
        code_lines.append('    logger.info(f"[DataFlow] 开始格式化提示词，模板长度: {len(template)}")')
        code_lines.append("    result = template")
        code_lines.append("    # Substitute state variables")
        code_lines.append("    for key, value in state.items():")
        code_lines.append('        if key == "query":')
        code_lines.append('            # 对query变量特殊处理：确保完全一致，不进行任何转换')
        code_lines.append('            logger.debug(f"[DataFlow] 替换query变量: {repr(value)}")')
        code_lines.append('            result = result.replace(f"{{{{{key}}}}}", str(value) if value is not None else "")')
        code_lines.append('        else:')
        code_lines.append('            result = result.replace(f"{{{{{key}}}}}", str(value) if value is not None else "")')
        code_lines.append("    # Substitute global variables")
        code_lines.append("    for key, value in global_vars.items():")
        code_lines.append("        if callable(value):")
        code_lines.append("            resolved_value = value()")
        code_lines.append("        else:")
        code_lines.append("            resolved_value = value")
        code_lines.append('        result = result.replace(f"{{{{{key}}}}}", str(resolved_value) if resolved_value is not None else "")')
        code_lines.append('    logger.debug(f"[DataFlow] 提示词格式化完成，结果: {repr(result[:100])}...")')
        code_lines.append("    return result")
        code_lines.append("")

        code_lines.append("def get_global_vars() -> Dict[str, Any]:")
        code_lines.append('    """Get a copy of global variables with evaluated functions."""')
        code_lines.append("    result = {}")
        code_lines.append("    for key, value in GLOBAL_VARS.items():")
        code_lines.append("        if callable(value):")
        code_lines.append("            result[key] = value()")
        code_lines.append("        else:")
        code_lines.append("            result[key] = value")
        code_lines.append("    return result")
        code_lines.append("")

        code_lines.append("# ========================================")
        code_lines.append("# Run the Workflow")
        code_lines.append("# ========================================")
        code_lines.append("")
        code_lines.append("def run_interactive_mode():")
        code_lines.append('    """运行交互式对话模式。"""')
        code_lines.append("    app = build_graph()")
        code_lines.append("    current_state: AgentState = {")
        code_lines.append('        "messages": [],')
        for field in state_field_names:
            if field != "messages":
                code_lines.append(f'        "{field}": "",')
        code_lines.append("    }")
        code_lines.append("")
        code_lines.append('    print("\\n=== 交互式对话模式 ===")')
        code_lines.append('    print("输入 \'quit\' 或 \'exit\' 退出程序")')
        code_lines.append('    print("-" * 50)')
        code_lines.append("")
        code_lines.append("    while True:")
        code_lines.append("        try:")
        code_lines.append('            user_input = input("\\n用户: ")')
        code_lines.append('            if user_input.lower() in ["quit", "exit", "q"]:')
        code_lines.append('                print("\\n再见!")')
        code_lines.append("                break")
        code_lines.append('            if not user_input.strip():')
        code_lines.append('                print("请输入有效内容!")')
        code_lines.append("                continue")
        code_lines.append("")
        code_lines.append('            logger.info(f"[Interactive] 用户输入: {repr(user_input)}")')
        code_lines.append("")
        code_lines.append('            current_state["query"] = user_input')
        code_lines.append("            logger.info(f'[Interactive] 当前状态 query: {repr(current_state[\"query\"])}')")
        code_lines.append("")
        code_lines.append('            print("\\n正在处理...")')
        code_lines.append("            current_state = app.invoke(current_state)")
        code_lines.append("")
        code_lines.append("        except KeyboardInterrupt:")
        code_lines.append('            print("\\n\\n程序已被用户中断")')
        code_lines.append("            break")
        code_lines.append("        except Exception as e:")
        code_lines.append('            logger.error(f"运行错误: {e}")')
        code_lines.append('            print(f"\\n错误: {e}")')
        code_lines.append("            continue")
        code_lines.append("")
        code_lines.append('if __name__ == "__main__":')
        code_lines.append('    print("=" * 50)')
        code_lines.append('    print("LangFlow Workflow")')
        code_lines.append('    print("=" * 50)')
        code_lines.append("")
        
        if has_opening_message:
            code_lines.append("    # Display opening message if configured")
            code_lines.append("    print(\"\\nOpening Message:\")")
            code_lines.append('    print("-" * 30)')
            code_lines.append("    print(OPENING_MESSAGE)")
            code_lines.append('    print("-" * 30)')
            code_lines.append("")
        
        code_lines.append("    # ========================================")
        code_lines.append("    # 直接启动交互式对话模式")
        code_lines.append("    # ========================================")
        code_lines.append("    run_interactive_mode()")

        return "\n".join(code_lines)

    def _generate_state(self, fields: Dict[str, str], nodes: List[Dict]) -> tuple:
        """返回 (代码行列表, 状态字段名列表)。"""
        lines = []
        lines.append("# ========================================")
        lines.append("# State Definition")
        lines.append("# ========================================")
        lines.append("")
        lines.append("class AgentState(TypedDict):")
        lines.append('    """State definition for the LangGraph workflow."""')
        
        all_fields = dict(fields)
        
        for node in nodes:
            node_type = node.get("type")
            config = node.get("config", {})
            if node_type == "llm" or node_type == "code":
                for inp in config.get("inputs", []):
                    if inp.get("name"):
                        all_fields[inp["name"]] = inp.get("type", "str")
                for out in config.get("outputs", []):
                    if out.get("name"):
                        all_fields[out["name"]] = out.get("type", "str")
            if node_type == "output":
                out_var = config.get("outputVariable", "output")
                if out_var and out_var not in all_fields:
                    all_fields[out_var] = "str"
        
        lines.append("    messages: List[Dict[str, str]]")
        lines.append("    query: str")
        lines.append("    output: str")
        
        if not all_fields:
            all_fields = {"messages": "List[Dict[str, str]]", "query": "str", "output": "str"}
        else:
            all_fields["messages"] = "List[Dict[str, str]]"
            if "query" not in all_fields:
                all_fields["query"] = "str"
            if "output" not in all_fields:
                all_fields["output"] = "str"
            for field_name, field_type in all_fields.items():
                if field_name not in ["messages", "query", "output"]:
                    py_type = self._map_type_to_python(field_type)
                    lines.append(f"    {field_name}: {py_type}")
        
        return lines, list(all_fields.keys())

    def _map_type_to_python(self, type_str: str) -> str:
        type_mapping = {
            "string": "str",
            "number": "float",
            "boolean": "bool",
            "object": "Dict[str, Any]",
            "array": "List[Any]",
        }
        return type_mapping.get(type_str, "str")

    def _build_node_id_to_name(self, nodes: List[Dict[str, Any]]) -> Dict[str, str]:
        """为每个节点生成可读的、唯一的 Python 函数名（如 input_node, llm_node, output_node_2）。"""
        seen: Dict[str, int] = {}
        out: Dict[str, str] = {}
        for node in nodes:
            t = node.get("type", "node")
            if t in ("start", "end"):
                continue
            base = t if t in ("input", "condition", "llm", "output", "code", "knowledge") else "node"
            if base not in seen:
                seen[base] = 0
            seen[base] += 1
            name = f"{base}_node" if seen[base] == 1 else f"{base}_node_{seen[base]}"
            out[node["id"]] = name
        return out

    def _generate_node(self, node: Dict[str, Any], func_name: str) -> List[str]:
        node_id = node["id"]
        node_label = node.get("label", node_id)
        node_type = node.get("type", NodeType.LLM)
        config = node.get("config", {})

        lines = []
        lines.append(f"def {func_name}(state: AgentState) -> AgentState:")
        lines.append(f'    """')
        lines.append(f"    Node: {node_label} ({node_type})")
        lines.append(f'    """')
        lines.append("    global_vars = get_global_vars()")
        lines.append("")

        if node_type == "llm":
            lines = self._generate_llm_node(lines, config, node_label)
        elif node_type == "code":
            lines = self._generate_code_node(lines, config, node_label)
        elif node_type == "knowledge":
            lines = self._generate_knowledge_node(lines, config, node_label)
        elif node_type == "condition":
            lines = self._generate_condition_node(lines, config, node_label)
        elif node_type == "input":
            lines = self._generate_input_node(lines, config, node_label)
        elif node_type == "output":
            lines = self._generate_output_node(lines, config, node_label)
        else:
            lines.append("    # Unknown node type")
            lines.append("    return state")

        return lines

    def _generate_llm_node(self, lines: List[str], config: Dict, node_label: str) -> List[str]:
        model = "Qwen3-32B-FP8"
        temperature = config.get("temperature", 0.7)
        system_prompt = config.get("systemPrompt", "")
        user_prompt = config.get("userPrompt", "")
        outputs = config.get("outputs", [])
        enable_stream = config.get("enableStream", False)
        show_in_chat = config.get("showInChat", True)

        base_url_escaped = CHAT_OPENAI_BASE_URL.replace("\\", "\\\\").replace('"', '\\"')
        api_key_escaped = CHAT_OPENAI_API_KEY.replace("\\", "\\\\").replace('"', '\\"')
        lines.append(f"    # Initialize LLM: {model}")
        lines.append(f"    llm = ChatOpenAI(")
        lines.append(f'        base_url="{base_url_escaped}",')
        lines.append(f'        api_key="{api_key_escaped}",')
        lines.append(f'        model="{model}",')
        lines.append(f"        temperature={temperature},")
        if enable_stream:
            lines.append("        streaming=True,")
        lines.append("    )")
        lines.append("")

        lines.append("    # Build messages from chat history")
        lines.append("    chat_messages = []")
        if system_prompt:
            lines.append(f'    system_prompt = format_prompt("""{system_prompt}""", state, global_vars)')
            lines.append("    chat_messages.append(SystemMessage(content=system_prompt))")
        lines.append("")
        lines.append("    # Add previous messages from state")
        lines.append('    messages_history = state.get("messages", [])')
        lines.append('    for msg in messages_history:')
        lines.append('        if msg["role"] == "user":')
        lines.append('            chat_messages.append(HumanMessage(content=msg["content"]))')
        lines.append('        elif msg["role"] == "assistant":')
        lines.append('            chat_messages.append(AIMessage(content=msg["content"]))')
        lines.append("")
        lines.append("    # Get current user input - 确保query变量完全一致")
        lines.append('    raw_query = state.get("query", "")')
        lines.append('    logger.info(f"[DataFlow] LLM节点接收到query: {repr(raw_query)}")')
        lines.append("    # 验证query数据类型")
        lines.append("    if not ComponentData.validate_input(raw_query, 'str'):")
        lines.append('        raise ValueError(f"Invalid query type: expected str, got {type(raw_query)}")')
        lines.append("    # 确保query一致性：直接使用，不进行任何修改")
        lines.append("    query = ComponentData.ensure_query_consistency(raw_query)")
        lines.append("")
        if user_prompt:
            lines.append(f'    user_prompt_template = """{user_prompt}"""')
            lines.append('    logger.info(f"[DataFlow] 使用用户提示词模板: {repr(user_prompt_template)}")')
            lines.append("    # 确保query被嵌入到用户提示词中")
            lines.append("    user_prompt_formatted = format_prompt(user_prompt_template, state, global_vars)")
            lines.append('    logger.info(f"[DataFlow] 格式化后的用户提示词: {repr(user_prompt_formatted)}")')
            lines.append("    current_user_input = user_prompt_formatted")
        else:
            lines.append("    current_user_input = query")
            lines.append('    logger.info(f"[DataFlow] 直接使用query作为用户输入: {repr(current_user_input)}")')
        lines.append("")
        lines.append("    # Only add current user input if not already in history (or if history is empty)")
        lines.append('    if not messages_history or messages_history[-1].get("role") != "user":')
        lines.append("        chat_messages.append(HumanMessage(content=current_user_input))")
        lines.append("")
        lines.append("    # Invoke LLM")
        lines.append("    response = llm.invoke(chat_messages)")

        lines.append("")
        lines.append(f"    show_in_chat = {show_in_chat}")
        lines.append("    logger.info(f\"[DataFlow] showInChat 配置: {show_in_chat}\")")
        lines.append("    # Update chat history in state")
        lines.append('    new_messages = messages_history.copy()')
        lines.append('    # Only add user message if not already in history and showInChat is True')
        lines.append('    if show_in_chat and (not new_messages or new_messages[-1].get("role") != "user"):')
        lines.append('        new_messages.append({"role": "user", "content": current_user_input})')
        lines.append('    # Add assistant response only if showInChat is True')
        lines.append('    if show_in_chat:')
        lines.append('        new_messages.append({"role": "assistant", "content": response.content})')
        lines.append('    state["messages"] = new_messages')
        lines.append("")
        lines.append("    # Update state with output (各输出变量 + 统一 output 供输出节点使用)")
        if outputs:
            for out in outputs:
                out_name = out.get("name", "output")
                lines.append(f'    state["{out_name}"] = response.content')
            lines.append('    state["output"] = response.content  # 供输出节点默认展示')
        else:
            lines.append('    state["output"] = response.content')
        lines.append("")
        lines.append("    return state")
        return lines

    def _generate_code_node(self, lines: List[str], config: Dict, node_label: str) -> List[str]:
        code = config.get("code", "")
        inputs = config.get("inputs", [])
        outputs = config.get("outputs", [])

        if inputs:
            lines.append("    # Extract and validate inputs from state")
            for inp in inputs:
                inp_name = inp.get("name")
                inp_type = inp.get("type", "string")
                if inp_name:
                    lines.append(f'    {inp_name} = state.get("{inp_name}", "")')
                    lines.append(f"    if not ComponentData.validate_input({inp_name}, '{inp_type}'):")
                    lines.append(f'        raise ValueError(f"Invalid {inp_name} type: expected {inp_type}, got {{type({inp_name})}}")')
                    lines.append(f'    logger.debug(f"[DataFlow] 代码节点接收到{inp_name}: {{repr({inp_name})}}")')
        lines.append("")

        lines.append("    # Execute custom code")
        lines.append("    try:")
        code_lines = code.split("\n")
        for line in code_lines:
            lines.append(f"        {line}")
        lines.append("    except Exception as e:")
        lines.append(f'        logger.error(f"Error in {node_label}: {{e}}")')
        lines.append("        raise")
        lines.append("")

        if outputs:
            lines.append("    # Update state with outputs")
            for out in outputs:
                out_name = out.get("name")
                if out_name:
                    lines.append(f'    # state["{out_name}"] = ... (set in custom code)')
        lines.append("")
        lines.append("    return state")
        return lines

    def _generate_knowledge_node(self, lines: List[str], config: Dict, node_label: str) -> List[str]:
        knowledge_base = config.get("knowledgeBase", "")
        top_k = config.get("topK", 5)

        lines.append("    # Knowledge retrieval placeholder")
        lines.append("    # You need to implement this with your vector store")
        lines.append("    # Example using FAISS:")
        lines.append("    # from langchain_community.vectorstores import FAISS")
        lines.append("    # from langchain_openai import OpenAIEmbeddings")
        lines.append("    # embeddings = OpenAIEmbeddings()")
        lines.append(f'    # vector_store = FAISS.load_local("{knowledge_base}", embeddings)')
        lines.append(f'    # docs = vector_store.similarity_search(state.get("query", ""), k={top_k})')
        lines.append('    # state["context"] = "\\n".join([d.page_content for d in docs])')
        lines.append("")
        lines.append("    # For now, just pass through")
        lines.append("    return state")
        return lines

    def _generate_condition_node(self, lines: List[str], config: Dict, node_label: str) -> List[str]:
        conditions = config.get("conditions", [])
        lines.append("    # Condition node - routing handled by conditional edges")
        for idx, cond in enumerate(conditions):
            cond_label = cond.get("label", f"Condition {idx + 1}")
            cond_expr = cond.get("expression", "True")
            lines.append(f"    # {cond_label}: {cond_expr}")
        lines.append("    return state")
        return lines

    def _generate_input_node(self, lines: List[str], config: Dict, node_label: str) -> List[str]:
        input_type = config.get("inputType", "dialog")
        variables = config.get("variables", [])

        lines.append(f"    # Input type: {input_type}")
        lines.append("    # 收集并验证用户输入，确保query变量完全一致")
        lines.append("")
        
        if variables:
            lines.append("    # Input variables:")
            for var in variables:
                var_name = var.get("name")
                var_type = var.get("type", "string")
                lines.append(f"    #   - {var_name}: {var_type}")
                if var_name:
                    lines.append(f'    raw_{var_name} = state.get("{var_name}", "")')
                    lines.append(f"    if not ComponentData.validate_input(raw_{var_name}, '{var_type}'):")
                    lines.append(f'        raise ValueError(f"Invalid {var_name} type: expected {var_type}, got {{type(raw_{var_name})}}")')
                    lines.append(f'    # 确保{var_name}一致性：不进行任何修改')
                    lines.append(f'    {var_name} = ComponentData.ensure_query_consistency(raw_{var_name})')
                    lines.append(f'    state["{var_name}"] = {var_name}')
                    lines.append(f'    logger.info(f"[DataFlow] 输入节点处理{var_name}: {{repr({var_name})}}")')
        else:
            lines.append("    # 默认：处理'query'变量")
            lines.append('    raw_query = state.get("query", "")')
            lines.append('    if not ComponentData.validate_input(raw_query, "str"):')
            lines.append('        raise ValueError(f"Invalid query type: expected str, got {type(raw_query)}")')
            lines.append("    # 确保query一致性：完全保留原始输入")
            lines.append("    query = ComponentData.ensure_query_consistency(raw_query)")
            lines.append('    state["query"] = query')
            lines.append('    logger.info(f"[DataFlow] 输入节点处理query: {repr(query)}")')
        
        lines.append("")
        lines.append("    return state")
        return lines

    def _generate_output_node(self, lines: List[str], config: Dict, node_label: str) -> List[str]:
        output_var = (config.get("outputVariable") or "").strip() or "output"
        lines.append("    # Output node")
        lines.append(f'    output_value = state.get("{output_var}", "")')
        lines.append('    logger.info(f"[DataFlow] 输出节点值: {repr(output_value)}")')
        lines.append('    print(f"\\nOutput: {output_value}")')
        lines.append("    return state")
        return lines

    def _condition_expr_from_config(self, cond: Dict[str, Any]) -> str:
        """从条件配置生成 Python 表达式（用于路由判断）。"""
        raw = cond.get("expression") or ""
        if raw:
            s = str(raw).strip().lower()
            if s == "true":
                return "True"
            if s == "false":
                return "False"
            return cond.get("expression", "True")
        field = cond.get("field", "")
        operator = cond.get("operator", "==")
        value = cond.get("value", "")
        if not field:
            return "True"
        safe_field = field.replace('"', '\\"')
        try:
            float(value)
            value_repr = value
        except (ValueError, TypeError):
            value_repr = repr(str(value))
        if operator == "contains":
            return f'str({value_repr}) in str(state.get("{safe_field}", ""))'
        if operator in ("==", "!="):
            return f'str(state.get("{safe_field}", "")) {operator} str({value_repr})'
        # 数值比较
        if operator in (">", "<", ">=", "<="):
            return f'(state.get("{safe_field}", "") or 0) {operator} ({value_repr})'
        return "True"

    def _generate_conditional_edges(
        self,
        cond_node_id: str,
        cond_node_data: Dict[str, Any],
        out_edges: List[Dict[str, Any]],
        all_nodes: List[Dict[str, Any]],
    ) -> List[str]:
        """为条件节点生成 add_conditional_edges 与路由函数。"""
        lines: List[str] = []
        config = cond_node_data.get("config", {})
        conditions = config.get("conditions", [])

        # sourceHandle -> target node id
        handle_to_target: Dict[str, str] = {}
        for e in out_edges:
            handle = e.get("sourceHandle") or "condition_0"
            to_id = e.get("to", "")
            if to_id:
                handle_to_target[handle] = to_id

        target_if = handle_to_target.get("condition_0")
        target_else = handle_to_target.get("condition_else")
        if not target_else and len(handle_to_target) == 1:
            target_else = list(handle_to_target.values())[0]
        if not target_if and not target_else:
            return lines
        if not target_else:
            target_else = "__end__"
        if not target_if:
            target_if = target_else

        def _ret(v: str) -> str:
            if v == "END" or v == "__end__":
                return "return END"
            return f'return "{v}"'

        func_name = f"_route_{cond_node_id}"
        lines.append(f"    def {func_name}(state: AgentState):")
        lines.append("        try:")
        if conditions:
            expr = self._condition_expr_from_config(conditions[0])
            lines.append(f"            if {expr}:")
            lines.append(f"                {_ret(target_if)}")
        else:
            lines.append(f"            {_ret(target_if)}")
        lines.append("        except Exception:")
        lines.append("            pass")
        lines.append(f"        {_ret(target_else)}")
        lines.append("")
        lines.append(f'    workflow.add_conditional_edges("{cond_node_id}", {func_name})')
        return lines

    def _generate_edge(self, edge: Dict[str, Any], all_nodes: List[Dict[str, Any]]) -> str:
        from_node = edge["from"]
        to_node = edge["to"]
        from_node_data = next((n for n in all_nodes if n["id"] == from_node), None)
        if from_node_data and from_node_data.get("type") == "condition":
            return ""  # 条件边由 _generate_conditional_edges 处理
        if from_node_data and from_node_data.get("type") == "start":
            return f'workflow.set_entry_point("{to_node}")'

        if from_node == "START":
            return f'workflow.set_entry_point("{to_node}")'
        elif to_node == "END":
            return f'workflow.add_edge("{from_node}", END)'
        else:
            to_node_data = next((n for n in all_nodes if n["id"] == to_node), None)
            to_label = to_node_data.get("label", to_node) if to_node_data else to_node
            from_label = from_node_data.get("label", from_node) if from_node_data else from_node
            return f'workflow.add_edge("{from_node}", "{to_node}")  # {from_label} → {to_label}'
