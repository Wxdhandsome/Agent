import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from generator import CodeGenerator

def test_example_workflow():
    code_gen = CodeGenerator()
    
    example_data = {
        "state": {
            "fields": {
                "arg1": "string",
                "arg2": "string",
                "result1": "string",
                "result2": "string"
            }
        },
        "nodes": [
            {
                "id": "start",
                "type": "start",
                "label": "开始"
            },
            {
                "id": "condition_node",
                "type": "condition",
                "label": "条件分支",
                "config": {
                    "conditions": [
                        { "label": "使用大模型", "expression": "state.get('use_llm', True)" }
                    ],
                    "hasElse": True
                }
            },
            {
                "id": "llm_node",
                "type": "llm",
                "label": "大模型",
                "config": {
                    "model": "vllm2/Qwen3-32B-FP8",
                    "temperature": 0.7,
                    "systemPrompt": "",
                    "userPrompt": "",
                    "inputs": [
                        { "name": "arg1", "type": "string" },
                        { "name": "arg2", "type": "string" }
                    ],
                    "outputs": [
                        { "name": "result1", "type": "string" },
                        { "name": "result2", "type": "string" }
                    ],
                    "enableReference": True
                }
            },
            {
                "id": "code_node",
                "type": "code",
                "label": "代码",
                "config": {
                    "code": "def main(arg1: str, arg2: str) -> dict:\n    # 在此编写自定义逻辑，例如数据处理、API调用等\n    return {\"result1\": arg1, \"result2\": arg2}",
                    "inputs": [
                        { "name": "arg1", "type": "string" },
                        { "name": "arg2", "type": "string" }
                    ],
                    "outputs": [
                        { "name": "result1", "type": "string" },
                        { "name": "result2", "type": "string" }
                    ]
                }
            },
            {
                "id": "output_node",
                "type": "output",
                "label": "输出",
                "config": {
                    "outputVariable": "result1"
                }
            },
            {
                "id": "end",
                "type": "end",
                "label": "结束"
            }
        ],
        "edges": [
            { "from": "START", "to": "condition_node" },
            { "from": "condition_node", "to": "llm_node" },
            { "from": "condition_node", "to": "code_node" },
            { "from": "llm_node", "to": "output_node" },
            { "from": "code_node", "to": "output_node" },
            { "from": "output_node", "to": "END" }
        ]
    }
    
    workflow_config = {
        "openingMessage": "",
        "runMode": "single",
        "interactionType": "input",
        "enableDialogInput": True,
        "enableFormInput": False,
        "enableFileUpload": False,
        "fileSizeLimit": 15000,
        "fileTypes": "all",
        "outputVariable": "output",
        "presetQuestions": []
    }
    
    generated_code = code_gen.generate(example_data, workflow_config)
    print("Generated Example Workflow Code:")
    print("=" * 60)
    print(generated_code)
    print("=" * 60)
    
    with open("example_output.py", "w", encoding="utf-8") as f:
        f.write(generated_code)
    print("\nExample code saved to example_output.py")

if __name__ == "__main__":
    test_example_workflow()
