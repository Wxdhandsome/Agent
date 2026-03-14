from typing import Dict, Any, Optional, Tuple
import ast
import os
import re
import sys

# 确保 backend 在 path 中，以便导入 config
_backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)


class CodeReviewer:
    def __init__(self):
        self.review_prompt = """
你是一个专业的 Python 代码审查专家。请审查以下代码，找出以下问题：

1. **命名规范问题**：
   - 变量名、函数名、类名是否符合 PEP 8 规范
   - 是否使用了描述性的名称
   - 是否有保留字或不恰当的命名

2. **语法错误**：
   - 语法错误
   - 缩进问题
   - 拼写错误

3. **逻辑错误**：
   - 潜在的逻辑问题
   - 边界条件处理
   - 资源管理问题
   - 异常处理

4. **代码质量**：
   - 代码可读性
   - 重复代码
   - 性能优化建议
   - 最佳实践

请按照以下格式输出：

--- 审查报告 ---
问题类型：[问题类型]
位置：[行号或描述]
问题：[问题描述]
建议：[修复建议]

--- 修复后的代码 ---
[完整的修复后代码]
"""

    def _check_python_syntax(self, code: str) -> Tuple[bool, Optional[str]]:
        """检查 Python 语法是否正确"""
        try:
            ast.parse(code)
            return True, None
        except SyntaxError as e:
            return False, f"语法错误: {e.msg} (第 {e.lineno} 行)"
        except Exception as e:
            return False, f"解析错误: {str(e)}"

    def _check_naming_conventions(self, code: str) -> list:
        """检查命名规范"""
        issues = []
        
        # 检查类名（应该使用驼峰命名）
        class_pattern = r'class\s+([a-z_][a-zA-Z0-9_]*)'
        class_matches = re.findall(class_pattern, code)
        for class_name in class_matches:
            if not class_name[0].isupper():
                issues.append({
                    'type': '命名规范',
                    'location': f'类名: {class_name}',
                    'issue': '类名应该使用驼峰命名法（首字母大写）',
                    'suggestion': f'将 {class_name} 改为 {class_name.capitalize()}'
                })
        
        # 检查函数名（应该使用下划线命名）
        func_pattern = r'def\s+([A-Z][a-zA-Z0-9_]*)'
        func_matches = re.findall(func_pattern, code)
        for func_name in func_matches:
            if func_name[0].isupper() and '_' not in func_name:
                issues.append({
                    'type': '命名规范',
                    'location': f'函数名: {func_name}',
                    'issue': '函数名应该使用下划线命名法',
                    'suggestion': f'将 {func_name} 改为 {func_name.lower()}'
                })
        
        return issues

    def _review_with_llm(self, code: str) -> Tuple[str, str]:
        """使用 LLM 进行深度代码审查"""
        try:
            from langchain_openai import ChatOpenAI
            from langchain_core.prompts import ChatPromptTemplate
            from langchain_core.messages import HumanMessage
            from config.chat_openai_config import (
                CHAT_OPENAI_BASE_URL,
                CHAT_OPENAI_API_KEY,
                CHAT_OPENAI_DEFAULT_MODEL,
                CHAT_OPENAI_DEFAULT_TEMPERATURE,
            )

            llm = ChatOpenAI(
                base_url=CHAT_OPENAI_BASE_URL,
                api_key=CHAT_OPENAI_API_KEY,
                model=CHAT_OPENAI_DEFAULT_MODEL,
                temperature=CHAT_OPENAI_DEFAULT_TEMPERATURE,
            )

            prompt = ChatPromptTemplate.from_messages([
                ("system", self.review_prompt),
                ("human", "请审查以下代码：\n\n{code}")
            ])

            chain = prompt | llm
            response = chain.invoke({"code": code})
            return response.content, code
        except Exception as e:
            return f"LLM 审查失败: {str(e)}", code

    def review(self, code: str) -> Dict[str, Any]:
        """
        审查代码并返回结果
        返回包含审查报告和修复后代码的字典
        """
        results = {
            'has_errors': False,
            'syntax_valid': True,
            'issues': [],
            'review_report': '',
            'fixed_code': code
        }

        # 1. 基础语法检查
        syntax_ok, syntax_error = self._check_python_syntax(code)
        if not syntax_ok:
            results['has_errors'] = True
            results['syntax_valid'] = False
            results['issues'].append({
                'type': '语法错误',
                'location': '整体',
                'issue': syntax_error,
                'suggestion': '请修复语法错误'
            })

        # 2. 命名规范检查
        naming_issues = self._check_naming_conventions(code)
        if naming_issues:
            results['has_errors'] = True
            results['issues'].extend(naming_issues)

        # 3. 使用 LLM 进行深度审查
        review_report, fixed_code = self._review_with_llm(code)
        results['review_report'] = review_report
        results['fixed_code'] = fixed_code

        return results

    def _basic_fix(self, code: str, issues: list) -> str:
        """基础代码修复"""
        fixed_code = code
        
        # 简单的命名修复
        for issue in issues:
            if issue['type'] == '命名规范':
                # 这里可以实现简单的命名修复逻辑
                pass
        
        return fixed_code
