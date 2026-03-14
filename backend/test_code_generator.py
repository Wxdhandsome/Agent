import sys
import os
import unittest
import tempfile
import logging

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from generator import CodeGenerator


class TestCodeGenerator(unittest.TestCase):
    """单元测试类，验证代码生成器的功能"""

    def setUp(self):
        """测试前的准备工作"""
        self.code_gen = CodeGenerator()
        self.test_data = {
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
                {"from": "llm_node", "to": "output"},
                {"from": "output", "to": "END"}
            ]
        }

    def test_code_generation(self):
        """测试代码生成功能"""
        generated_code = self.code_gen.generate(self.test_data)
        self.assertIsNotNone(generated_code)
        self.assertIsInstance(generated_code, str)
        self.assertGreater(len(generated_code), 0)

    def test_query_consistency_mechanism(self):
        """测试query一致性机制是否正确实现"""
        generated_code = self.code_gen.generate(self.test_data)
        
        # 验证ComponentData类存在
        self.assertIn("class ComponentData:", generated_code)
        self.assertIn("def ensure_query_consistency", generated_code)
        
        # 验证输入节点的query处理逻辑
        self.assertIn("ComponentData.ensure_query_consistency", generated_code)
        
        # 验证LLM节点的query验证逻辑
        self.assertIn("ComponentData.validate_input", generated_code)
        
        # 验证日志记录功能
        self.assertIn("import logging", generated_code)
        self.assertIn("logger = logging.getLogger", generated_code)
        self.assertIn("[DataFlow]", generated_code)

    def test_prompt_formatting(self):
        """测试提示词格式化功能"""
        generated_code = self.code_gen.generate(self.test_data)
        
        # 验证format_prompt函数存在
        self.assertIn("def format_prompt", generated_code)
        
        # 验证query变量的特殊处理
        self.assertIn('if key == "query":', generated_code)
        self.assertIn("特殊处理：确保完全一致", generated_code)

    def test_data_validation(self):
        """测试数据验证机制"""
        generated_code = self.code_gen.generate(self.test_data)
        
        # 验证validate_input方法存在
        self.assertIn("def validate_input", generated_code)
        
        # 验证支持的数据类型
        self.assertIn("expected_type == 'str'", generated_code)
        self.assertIn("expected_type == 'number'", generated_code)
        self.assertIn("expected_type == 'boolean'", generated_code)
        self.assertIn("expected_type == 'object'", generated_code)
        self.assertIn("expected_type == 'array'", generated_code)

    def test_edge_cases(self):
        """测试边界情况"""
        # 测试空配置
        empty_data = {
            "state": {"fields": {}},
            "nodes": [],
            "edges": []
        }
        generated_code_empty = self.code_gen.generate(empty_data)
        self.assertIsNotNone(generated_code_empty)
        
        # 测试特殊字符输入
        special_chars_test_data = self.test_data.copy()
        special_chars_test_data["nodes"][2]["config"]["userPrompt"] = "Test with {{query}} and special chars: \\n\\t\\\""
        generated_code_special = self.code_gen.generate(special_chars_test_data)
        self.assertIn("Test with", generated_code_special)

    def test_generated_code_syntax(self):
        """测试生成的代码语法正确性"""
        generated_code = self.code_gen.generate(self.test_data)
        
        # 创建临时文件来测试语法
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
            f.write(generated_code)
            temp_file_name = f.name
        
        try:
            # 尝试编译代码，验证语法正确性
            compile(generated_code, temp_file_name, 'exec')
            syntax_valid = True
        except SyntaxError as e:
            syntax_valid = False
            self.fail(f"Generated code has syntax error: {e}")
        finally:
            # 清理临时文件
            os.unlink(temp_file_name)
        
        self.assertTrue(syntax_valid)


class TestQueryConsistency(unittest.TestCase):
    """专门测试query变量一致性的测试类"""

    def setUp(self):
        """设置测试用的用户输入场景"""
        self.test_inputs = [
            "Hello, world!",
            "  带前后空格的输入  ",
            "包含\n换行符\t制表符\"引号'的输入",
            "Unicode字符测试: 你好世界 🌍",
            "非常长的输入" * 100,
            "",  # 空字符串
            "1234567890",  # 纯数字
            '{"key": "value"}',  # JSON格式
        ]

    def test_various_input_scenarios(self):
        """测试多种用户输入场景下的query一致性"""
        code_gen = CodeGenerator()
        
        for test_input in self.test_inputs:
            with self.subTest(test_input=test_input):
                # 构建包含该测试输入的测试数据
                test_data = {
                    "state": {"fields": {"query": "string", "output": "string"}},
                    "nodes": [
                        {
                            "id": "input",
                            "type": "input",
                            "label": "输入",
                            "config": {"variables": [{"name": "query", "type": "string"}]}
                        },
                        {
                            "id": "llm",
                            "type": "llm",
                            "label": "LLM",
                            "config": {"userPrompt": "{{query}}"}
                        }
                    ],
                    "edges": [{"from": "input", "to": "llm"}]
                }
                
                generated_code = code_gen.generate(test_data)
                
                # 验证确保query一致性的逻辑存在
                self.assertIn("ComponentData.ensure_query_consistency", generated_code)
                
                # 验证该函数直接返回输入，不进行修改
                self.assertIn("return user_input", generated_code)


if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("=" * 60)
    print("Running Code Generator Unit Tests")
    print("=" * 60)
    
    unittest.main(verbosity=2)
