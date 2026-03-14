import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/backend')

from generator import CodeGenerator


def test_show_in_chat():
    code_gen = CodeGenerator()
    
    # 测试数据，包含两个 LLM 节点，一个 showInChat=True，一个 showInChat=False
    test_data = {
        "state": {
            "fields": {
                "query": "string",
                "intermediate_result": "string",
                "final_output": "string"
            }
        },
        "nodes": [
            {
                "id": "node_1",
                "type": "input",
                "label": "用户输入"
            },
            {
                "id": "node_2",
                "type": "llm",
                "label": "中间处理(不显示)",
                "config": {
                    "showInChat": False,
                    "temperature": 0.7,
                    "systemPrompt": "你是一个助手，请对用户输入进行处理",
                    "userPrompt": "{{query}}",
                    "inputs": [{"name": "query", "type": "string"}],
                    "outputs": [{"name": "intermediate_result", "type": "string"}]
                }
            },
            {
                "id": "node_3",
                "type": "condition",
                "label": "判断分支",
                "config": {
                    "conditions": [
                        {"label": "正常处理", "expression": "True"}
                    ]
                }
            },
            {
                "id": "node_4",
                "type": "llm",
                "label": "最终生成(显示)",
                "config": {
                    "showInChat": True,
                    "temperature": 0.7,
                    "systemPrompt": "你是一个助手，基于中间结果给出最终回答",
                    "userPrompt": "{{intermediate_result}}",
                    "inputs": [{"name": "intermediate_result", "type": "string"}],
                    "outputs": [{"name": "final_output", "type": "string"}]
                }
            },
            {
                "id": "node_5",
                "type": "output",
                "label": "最终输出",
                "config": {
                    "outputVariable": "final_output"
                }
            }
        ],
        "edges": [
            {"from": "node_1", "to": "node_2"},
            {"from": "node_2", "to": "node_3"},
            {"from": "node_3", "to": "node_4"},
            {"from": "node_4", "to": "node_5"}
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
    print("Generated Code with showInChat support:")
    print("=" * 80)
    print(generated_code)
    print("=" * 80)
    
    # 保存生成的代码
    with open("test_show_in_chat_output.py", "w", encoding="utf-8") as f:
        f.write(generated_code)
    
    print("\n✅ 测试代码已保存到 test_show_in_chat_output.py")


if __name__ == "__main__":
    test_show_in_chat()
