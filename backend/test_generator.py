import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from generator import CodeGenerator

def test_code_generator():
    code_gen = CodeGenerator()
    
    test_data = {
        "state": {
            "fields": {
                "query": "string",
                "output": "string"
            }
        },
        "nodes": [
            {
                "id": "start",
                "type": "start",
                "label": "开始"
            },
            {
                "id": "input",
                "type": "input",
                "label": "输入",
                "config": {
                    "inputType": "dialog",
                    "variables": [{"name": "query", "type": "string"}]
                }
            },
            {
                "id": "llm_node",
                "type": "llm",
                "label": "大模型",
                "config": {
                    "model": "gpt-3.5-turbo",
                    "temperature": 0.7,
                    "systemPrompt": "You are a helpful assistant.",
                    "userPrompt": "{{query}}"
                }
            },
            {
                "id": "code_node",
                "type": "code",
                "label": "代码",
                "config": {
                    "code": "result = state['output'].upper()\nstate['output'] = result",
                    "inputs": [{"name": "output", "type": "string"}],
                    "outputs": [{"name": "output", "type": "string"}]
                }
            },
            {
                "id": "output",
                "type": "output",
                "label": "输出",
                "config": {
                    "outputVariable": "output"
                }
            },
            {
                "id": "end",
                "type": "end",
                "label": "结束"
            }
        ],
        "edges": [
            {"from": "START", "to": "input"},
            {"from": "input", "to": "llm_node"},
            {"from": "llm_node", "to": "code_node"},
            {"from": "code_node", "to": "output"},
            {"from": "output", "to": "END"}
        ]
    }
    
    generated_code = code_gen.generate(test_data)
    print("Generated code:")
    print("=" * 50)
    print(generated_code)
    print("=" * 50)
    
    with open("test_output.py", "w", encoding="utf-8") as f:
        f.write(generated_code)
    print("\nCode saved to test_output.py")

if __name__ == "__main__":
    test_code_generator()
