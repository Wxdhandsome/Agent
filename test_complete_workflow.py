import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/backend')

from generator import CodeGenerator


def test_complete_workflow():
    code_gen = CodeGenerator()
    
    # 完整的工作流测试：包含输入 -> LLM(showInChat=False) -> 条件分支 -> LLM(showInChat=True) -> 输出
    test_data = {
        "state": {
            "fields": {
                "query": "string",
                "intent_result": "string",
                "final_answer": "string"
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
                    "temperature": 0.7,
                    "systemPrompt": "你是一个意图判断专家，根据输入判断用户的意图。如果是面试返回'面试'，其他返回'闲聊'",
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
                        {"label": "面试模式", "field": "intent_result", "operator": "==", "value": "面试"}
                    ],
                    "hasElse": True
                }
            },
            {
                "id": "interview_llm",
                "type": "llm",
                "label": "面试问题生成(显示)",
                "config": {
                    "showInChat": True,
                    "temperature": 0.7,
                    "systemPrompt": "你是一个面试官，请根据用户输入生成一个相关的面试问题",
                    "userPrompt": "{{query}}",
                    "inputs": [{"name": "query", "type": "string"}],
                    "outputs": [{"name": "final_answer", "type": "string"}]
                }
            },
            {
                "id": "chat_llm",
                "type": "llm",
                "label": "闲聊模式(显示)",
                "config": {
                    "showInChat": True,
                    "temperature": 0.7,
                    "systemPrompt": "你是一个友好的助手，请与用户闲聊",
                    "userPrompt": "{{query}}",
                    "inputs": [{"name": "query", "type": "string"}],
                    "outputs": [{"name": "final_answer", "type": "string"}]
                }
            },
            {
                "id": "output_node",
                "type": "output",
                "label": "最终输出",
                "config": {
                    "outputVariable": "final_answer"
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
        "outputVariable": "final_answer"
    }
    
    generated_code = code_gen.generate(test_data, workflow_config)
    
    print("=" * 80)
    print("Generated Complete Workflow Code:")
    print("=" * 80)
    print(generated_code)
    print("=" * 80)
    
    with open("test_complete_workflow_output.py", "w", encoding="utf-8") as f:
        f.write(generated_code)
    
    print("\n✅ 完整工作流测试代码已保存到 test_complete_workflow_output.py")


if __name__ == "__main__":
    test_complete_workflow()
