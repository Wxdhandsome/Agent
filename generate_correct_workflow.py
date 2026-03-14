import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/backend')

from generator import CodeGenerator


def generate_correct_workflow():
    code_gen = CodeGenerator()
    
    correct_workflow = {
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
    
    generated_code = code_gen.generate(correct_workflow, workflow_config)
    
    with open("correct_workflow.py", "w", encoding="utf-8") as f:
        f.write(generated_code)
    
    print("=" * 80)
    print("✅ 正确的工作流代码已生成到: correct_workflow.py")
    print("=" * 80)
    print("\n你现在可以:")
    print("1. 在前端界面重新设计工作流（按照完整解决方案说明.md中的步骤）")
    print("2. 或者直接使用这个生成的 correct_workflow.py 进行测试")
    print("\n关键要点:")
    print("- 第一个 LLM (意图判断) 设置 showInChat=False")
    print("- 条件分支连接到两个 LLM 节点，不是直接连接到输出节点")
    print("- 最后只有一个输出节点，显示最终结果")
    
    return generated_code


if __name__ == "__main__":
    generate_correct_workflow()
