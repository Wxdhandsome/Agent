import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/backend')

from generator import CodeGenerator


def test_debug_workflow():
    code_gen = CodeGenerator()
    
    # 调试用工作流：输入 -> LLM1(showInChat=False, 意图判断) -> 条件分支 -> LLM2(showInChat=True) -> 输出
    test_data = {
        "state": {
            "fields": {
                "query": "string",
                "intent_result": "string",
                "final_output": "string"
            }
        },
        "nodes": [
            {
                "id": "input_node",
                "type": "input",
                "label": "用户输入"
            },
            {
                "id": "intent_llm",
                "type": "llm",
                "label": "意图判断(不显示)",
                "config": {
                    "showInChat": False,
                    "temperature": 0.1,
                    "systemPrompt": "你是意图判断专家。只返回'面试'或'闲聊'两个字，不要有其他内容。",
                    "userPrompt": "{{query}}",
                    "inputs": [{"name": "query", "type": "string"}],
                    "outputs": [{"name": "intent_result", "type": "string"}]
                }
            },
            {
                "id": "condition_node",
                "type": "condition",
                "label": "条件分支",
                "config": {
                    "conditions": [
                        {"label": "面试模式", "field": "intent_result", "operator": "contains", "value": "面试"}
                    ],
                    "hasElse": True
                }
            },
            {
                "id": "interview_llm",
                "type": "llm",
                "label": "面试问题(显示)",
                "config": {
                    "showInChat": True,
                    "temperature": 0.7,
                    "systemPrompt": "你是专业的面试官。请根据用户的输入生成一个相关的面试问题。",
                    "userPrompt": "用户输入: {{query}}",
                    "inputs": [{"name": "query", "type": "string"}],
                    "outputs": [{"name": "final_output", "type": "string"}]
                }
            },
            {
                "id": "chat_llm",
                "type": "llm",
                "label": "闲聊模式(显示)",
                "config": {
                    "showInChat": True,
                    "temperature": 0.7,
                    "systemPrompt": "你是友好的聊天助手。请与用户愉快地聊天。",
                    "userPrompt": "{{query}}",
                    "inputs": [{"name": "query", "type": "string"}],
                    "outputs": [{"name": "final_output", "type": "string"}]
                }
            },
            {
                "id": "output_node",
                "type": "output",
                "label": "最终输出",
                "config": {
                    "outputVariable": "final_output"
                }
            }
        ],
        "edges": [
            {"from": "input_node", "to": "intent_llm"},
            {"from": "intent_llm", "to": "condition_node"},
            {"sourceHandle": "condition_0", "from": "condition_node", "to": "interview_llm"},
            {"sourceHandle": "condition_else", "from": "condition_node", "to": "chat_llm"},
            {"from": "interview_llm", "to": "output_node"},
            {"from": "chat_llm", "to": "output_node"}
        ]
    }
    
    workflow_config = {
        "openingMessage": "",
        "runMode": "single",
        "interactionType": "input",
        "enableDialogInput": True,
        "outputVariable": "final_output"
    }
    
    generated_code = code_gen.generate(test_data, workflow_config)
    
    print("=" * 80)
    print("Generated Debug Workflow Code:")
    print("=" * 80)
    print(generated_code)
    print("=" * 80)
    
    with open("debug_workflow_output.py", "w", encoding="utf-8") as f:
        f.write(generated_code)
    
    print("\n✅ 调试工作流代码已保存到 debug_workflow_output.py")


if __name__ == "__main__":
    test_debug_workflow()
