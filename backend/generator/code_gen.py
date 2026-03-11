from typing import Dict, Any, List
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from nodes import NodeType


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
        code_lines.append("")

        state_code = self._generate_state(state_fields, nodes)
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

        if workflow_config:
            code_lines.append("")
            code_lines.append("# Workflow Configuration")
            if workflow_config.get("openingMessage"):
                opening_msg = workflow_config.get("openingMessage", "").replace('"""', '\\"\\"\\"')
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

        code_lines.append("# ========================================")
        code_lines.append("# Node Functions")
        code_lines.append("# ========================================")
        code_lines.append("")

        for node in nodes:
            node_type = node.get("type")
            if node_type not in ["start", "end"]:
                node_code = self._generate_node(node)
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
                code_lines.append(f'    # Node: {node_label} ({node_type})')
                code_lines.append(f'    workflow.add_node("{node_id}", {node_id})')
        code_lines.append("")

        code_lines.append("    # Define edges between nodes")
        for edge in edges:
            edge_code = self._generate_edge(edge, nodes)
            code_lines.append(f"    {edge_code}")

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
        code_lines.append('    """')
        code_lines.append("    result = template")
        code_lines.append("    # Substitute state variables")
        code_lines.append("    for key, value in state.items():")
        code_lines.append('        result = result.replace(f"{{{{{key}}}}}", str(value) if value is not None else "")')
        code_lines.append("    # Substitute global variables")
        code_lines.append("    for key, value in global_vars.items():")
        code_lines.append("        if callable(value):")
        code_lines.append("            resolved_value = value()")
        code_lines.append("        else:")
        code_lines.append("            resolved_value = value")
        code_lines.append('        result = result.replace(f"{{{{{key}}}}}", str(resolved_value) if resolved_value is not None else "")')
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
        code_lines.append("if __name__ == \"__main__\":")
        code_lines.append('    print("=" * 50)')
        code_lines.append('    print("LangFlow Workflow")')
        code_lines.append('    print("=" * 50)')
        code_lines.append("")
        
        code_lines.append("    # Display opening message if configured")
        code_lines.append("    if 'OPENING_MESSAGE' in locals() and OPENING_MESSAGE:")
        code_lines.append('        print("\\nOpening Message:")')
        code_lines.append('        print("-" * 30)')
        code_lines.append("        print(OPENING_MESSAGE)")
        code_lines.append('        print("-" * 30)')
        code_lines.append("")
        
        code_lines.append("    # Build the graph")
        code_lines.append("    app = build_graph()")
        code_lines.append("")
        
        code_lines.append("    # Example usage")
        code_lines.append("    print(\"\\nExample Usage:\")")
        code_lines.append('    initial_state: AgentState = {')
        
        for field in state_fields.keys():
            if field == "query":
                code_lines.append('        "query": "Hello, how can I help you today?",')
            else:
                code_lines.append(f'        "{field}": "",')
        code_lines.append("    }")
        code_lines.append("")
        code_lines.append("    print(\"\\nRunning workflow...\")")
        code_lines.append("    result = app.invoke(initial_state)")
        code_lines.append("")
        code_lines.append('    print("\\nWorkflow Result:")')
        code_lines.append('    print("-" * 30)')
        code_lines.append("    if 'OUTPUT_VARIABLE' in locals():")
        code_lines.append("        print(result.get(OUTPUT_VARIABLE, result))")
        code_lines.append("    else:")
        code_lines.append("        print(json.dumps(result, indent=2, ensure_ascii=False))")
        code_lines.append('    print("-" * 30)')
        code_lines.append("")
        code_lines.append('    print("\\nDone!")')

        return "\n".join(code_lines)

    def _generate_state(self, fields: Dict[str, str], nodes: List[Dict]) -> List[str]:
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
        
        if not all_fields:
            lines.append("    query: str")
            lines.append("    output: str")
        else:
            for field_name, field_type in all_fields.items():
                py_type = self._map_type_to_python(field_type)
                lines.append(f"    {field_name}: {py_type}")
        
        return lines

    def _map_type_to_python(self, type_str: str) -> str:
        type_mapping = {
            "string": "str",
            "number": "float",
            "boolean": "bool",
            "object": "Dict[str, Any]",
            "array": "List[Any]",
        }
        return type_mapping.get(type_str, "str")

    def _generate_node(self, node: Dict[str, Any]) -> List[str]:
        node_id = node["id"]
        node_label = node.get("label", node_id)
        node_type = node.get("type", NodeType.LLM)
        config = node.get("config", {})

        lines = []
        lines.append(f"def {node_id}(state: AgentState) -> AgentState:")
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
        model = config.get("model", "gpt-3.5-turbo")
        temperature = config.get("temperature", 0.7)
        system_prompt = config.get("systemPrompt", "")
        user_prompt = config.get("userPrompt", "")
        messages = config.get("messages", [])
        outputs = config.get("outputs", [])
        enable_stream = config.get("enableStream", False)

        lines.append(f"    # Initialize LLM: {model}")
        lines.append(f"    llm = ChatOpenAI(")
        lines.append(f'        model="{model}",')
        lines.append(f"        temperature={temperature},")
        if enable_stream:
            lines.append("        streaming=True,")
        lines.append("    )")
        lines.append("")

        lines.append("    # Build prompt template")
        prompt_parts = []
        if system_prompt:
            lines.append(f'    system_prompt = format_prompt("""{system_prompt}""", state, global_vars)')
            prompt_parts.append('        ("system", system_prompt),')
        if messages:
            lines.append("    # Add chat history")
            prompt_parts.append('        MessagesPlaceholder(variable_name="history"),')
        if user_prompt:
            lines.append(f'    user_prompt = format_prompt("""{user_prompt}""", state, global_vars)')
            prompt_parts.append('        ("human", user_prompt),')

        if prompt_parts:
            lines.append("    prompt = ChatPromptTemplate.from_messages([")
            for part in prompt_parts:
                lines.append(part)
            lines.append("    ])")
            lines.append("")
            lines.append("    # Create chain and invoke")
            if messages:
                lines.append("    chain = prompt | llm")
                lines.append('    history = [HumanMessage(content=state.get("query", ""))]')
                lines.append("    response = chain.invoke({\"history\": history, **state})")
            else:
                lines.append("    chain = prompt | llm")
                lines.append("    response = chain.invoke(state)")
        else:
            lines.append("    # Fallback: simple prompt")
            lines.append('    response = llm.invoke(state.get("query", ""))')

        lines.append("")
        lines.append("    # Update state with output")
        if outputs:
            for out in outputs:
                out_name = out.get("name", "output")
                lines.append(f'    state["{out_name}"] = response.content')
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
            lines.append("    # Extract inputs from state")
            for inp in inputs:
                inp_name = inp.get("name")
                if inp_name:
                    lines.append(f'    {inp_name} = state.get("{inp_name}", "")')
        lines.append("")

        lines.append("    # Execute custom code")
        lines.append("    try:")
        code_lines = code.split("\n")
        for line in code_lines:
            lines.append(f"        {line}")
        lines.append("    except Exception as e:")
        lines.append(f'        print(f"Error in {node_label}: {{e}}")')
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
        if variables:
            lines.append("    # Input variables:")
            for var in variables:
                var_name = var.get("name")
                var_type = var.get("type", "string")
                lines.append(f"    #   - {var_name}: {var_type}")
        lines.append("    return state")
        return lines

    def _generate_output_node(self, lines: List[str], config: Dict, node_label: str) -> List[str]:
        output_var = config.get("outputVariable", "output")
        lines.append("    # Output node")
        lines.append(f'    output_value = state.get("{output_var}", "")')
        lines.append('    print(f"\\nOutput: {output_value}")')
        lines.append("    return state")
        return lines

    def _generate_edge(self, edge: Dict[str, Any], all_nodes: List[Dict[str, Any]]) -> str:
        from_node = edge["from"]
        to_node = edge["to"]
        
        from_node_data = next((n for n in all_nodes if n["id"] == from_node), None)
        
        if from_node_data:
            from_label = from_node_data.get("label", from_node)
            from_type = from_node_data.get("type", "")
            if from_type == "condition":
                config = from_node_data.get("config", {})
                conditions = config.get("conditions", [])
                if conditions:
                    cond_label = conditions[0].get("label", "condition")
                    return f'workflow.add_edge("{from_node}", "{to_node}")  # {from_label} → {cond_label}'
        
        if from_node == "START":
            return f'workflow.set_entry_point("{to_node}")'
        elif to_node == "END":
            return f'workflow.add_edge("{from_node}", END)'
        else:
            to_node_data = next((n for n in all_nodes if n["id"] == to_node), None)
            to_label = to_node_data.get("label", to_node) if to_node_data else to_node
            from_label = from_node_data.get("label", from_node) if from_node_data else from_node
            return f'workflow.add_edge("{from_node}", "{to_node}")  # {from_label} → {to_label}'
