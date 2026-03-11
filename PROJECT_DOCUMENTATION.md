# LangFlow 项目文档

## 项目概述

LangFlow 是一个基于 LangGraph 的拖拽式可视化 AI 工作流编辑器，类似于 Coze 的可视化编程工具。用户可以通过拖拽节点来构建 AI 工作流，并自动生成可执行的 LangGraph Python 代码。

---

## 目录结构

```
agent/
├── backend/                    # 后端代码（Python + FastAPI）
│   ├── api/
│   │   ├── __init__.py         # API 模块初始化
│   │   └── main.py             # FastAPI 主应用，提供 REST API 接口
│   ├── generator/
│   │   ├── __init__.py         # 代码生成器模块初始化
│   │   └── code_gen.py         # 核心代码生成引擎，将工作流转换为 LangGraph 代码
│   ├── nodes/
│   │   ├── __init__.py         # 节点模块初始化
│   │   └── node_types.py       # 节点类型定义（枚举类）
│   ├── requirements.txt         # Python 依赖包列表
│   ├── test_generator.py       # 代码生成器测试文件
│   ├── test_output.py          # 测试输出文件
│   ├── example_workflow.py     # 示例工作流测试
│   └── example_output.py       # 示例输出文件
│
├── frontend/                   # 前端代码（React + ReactFlow）
│   ├── src/
│   │   ├── main.tsx           # React 应用入口
│   │   ├── App.tsx             # 主应用组件，包含画布和状态管理
│   │   ├── App.css            # 主应用样式
│   │   ├── index.css           # 全局样式
│   │   ├── api/
│   │   │   └── index.ts       # API 调用模块，与后端通信
│   │   └── components/
│   │       ├── Sidebar.tsx     # 左侧节点库面板
│   │       ├── Sidebar.css     # 侧边栏样式
│   │       ├── CodePanel.tsx  # 代码展示面板
│   │       ├── CodePanel.css  # 代码面板样式
│   │       ├── NodeConfigPanel.tsx   # 节点配置面板
│   │       ├── NodeConfigPanel.css   # 节点配置面板样式
│   │       ├── WorkflowConfigPanel.tsx   # 工作流全局配置面板
│   │       └── WorkflowConfigPanel.css   # 工作流配置面板样式
│   ├── package.json            # NPM 依赖配置
│   ├── vite.config.ts          # Vite 构建配置
│   ├── tsconfig.json           # TypeScript 配置
│   ├── tsconfig.node.json      # Node 环境 TypeScript 配置
│   └── index.html              # HTML 入口文件
│
├── start-backend.bat           # Windows 后端启动脚本
├── start-frontend.bat          # Windows 前端启动脚本
└── README.md                   # 项目说明文档
```

---

## 详细文件说明

### 后端文件

| 文件路径 | 说明 |
|---------|------|
| `backend/api/__init__.py` | API 模块的 Python 包初始化文件 |
| `backend/api/main.py` | FastAPI 主应用，包含以下功能：<br>- `/` 根路径健康检查<br>- `/api/generate` POST 接口，接收工作流数据并调用代码生成器 |
| `backend/generator/__init__.py` | 代码生成器模块初始化 |
| `backend/generator/code_gen.py` | **核心代码生成引擎**：<br>- `generate()` 方法：将工作流 JSON 数据转换为 LangGraph Python 代码<br>- `_generate_state()`：生成 AgentState TypedDict 类<br>- `_generate_node()`：根据节点类型生成对应的 Python 函数<br>- `_generate_edge()`：生成图连接代码 |
| `backend/nodes/__init__.py` | 节点模块初始化 |
| `backend/nodes/node_types.py` | 节点类型枚举定义，包含：<br>- `LLM` - 大模型节点<br>- `CODE` - 代码节点<br>- `KNOWLEDGE` - 知识库节点<br>- `API` - API 节点 |
| `backend/requirements.txt` | Python 依赖包：<br>- fastapi - Web 框架<br>- uvicorn - ASGI 服务器<br>- langgraph - 图工作流引擎<br>- langchain - LLM 应用框架<br>- pydantic - 数据验证 |
| `backend/test_generator.py` | 代码生成器单元测试，验证生成逻辑正确性 |
| `backend/example_workflow.py` | 示例工作流测试脚本，演示完整工作流生成 |
| `backend/test_output.py` | 测试输出结果文件 |
| `backend/example_output.py` | 示例输出结果文件 |

### 前端文件

| 文件路径 | 说明 |
|---------|------|
| `frontend/src/main.tsx` | React 应用入口点，挂载到 DOM |
| `frontend/src/App.tsx` | **主应用组件**，核心功能：<br>- 使用 ReactFlow 构建可视化画布<br>- 节点和边的状态管理<br>- 拖拽放置节点逻辑<br>- 节点点击事件处理<br>- 工作流配置状态管理<br>- 代码生成调用 |
| `frontend/src/App.css` | 主应用及节点的样式定义 |
| `frontend/src/index.css` | 全局 CSS 样式，重置默认样式 |
| `frontend/src/api/index.ts` | API 通信模块：<br>- `generateCode()` 函数：向后端 `/api/generate` 发送工作流数据 |
| `frontend/src/components/Sidebar.tsx` | **左侧节点库面板**，功能：<br>- 显示可拖拽的节点列表<br>- 支持 8 种节点类型：开始、结束、输入、输出、大模型、代码、条件分支、知识库<br>- 处理拖拽开始事件 |
| `frontend/src/components/Sidebar.css` | 侧边栏样式 |
| `frontend/src/components/CodePanel.tsx` | **代码展示弹窗**，功能：<br>- 显示生成的 Python 代码<br>- 复制代码功能<br>- 关闭按钮 |
| `frontend/src/components/CodePanel.css` | 代码面板样式 |
| `frontend/src/components/NodeConfigPanel.tsx` | **节点配置面板**（核心组件），功能：<br>- 根据节点类型显示不同配置表单<br>- 大模型节点：模型选择、温度、提示词、输入输出参数<br>- 代码节点：代码编辑器、输入输出参数<br>- 条件分支节点：条件表达式配置<br>- 输入/输出节点：变量配置<br>- 实时保存配置变更 |
| `frontend/src/components/NodeConfigPanel.css` | 节点配置面板样式 |
| `frontend/src/components/WorkflowConfigPanel.tsx` | **工作流全局配置面板**，功能：<br>- 开场白配置<br>- 运行模式（单次/批量）<br>- 交互类型配置<br>- 输入配置（对话框/表单/文件上传）<br>- 输出配置<br>- 预置问题列表<br>- 全局变量展示 |
| `frontend/src/components/WorkflowConfigPanel.css` | 工作流配置面板样式 |
| `frontend/package.json` | NPM 项目配置，包含依赖：<br>- react / react-dom - UI 框架<br>- reactflow - 可视化流程图库<br>- axios - HTTP 客户端<br>- vite - 构建工具 |
| `frontend/vite.config.ts` | Vite 开发服务器配置 |
| `frontend/tsconfig.json` | TypeScript 编译器配置 |
| `frontend/index.html` | HTML 入口文件 |

### 配置文件

| 文件路径 | 说明 |
|---------|------|
| `start-backend.bat` | Windows 批处理脚本，用于快速启动后端服务 |
| `start-frontend.bat` | Windows 批处理脚本，用于快速启动前端服务 |
| `README.md` | 项目说明文档 |

---

## 技术栈

### 后端技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| **Python** | 3.9+ | 编程语言 |
| **FastAPI** | 0.109.0 | Web 框架，提供 REST API |
| **Uvicorn** | 0.27.0 | ASGI 服务器 |
| **LangGraph** | 0.0.62 | 图工作流引擎 |
| **LangChain** | 0.1.8 | LLM 应用开发框架 |
| **LangChain OpenAI** | 0.0.6 | OpenAI API 集成 |
| **Pydantic** | 2.6.0 | 数据验证和类型定义 |
| **Python-multipart** | 0.0.6 | 表单数据处理 |

### 前端技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| **React** | 18.2.0 | UI 框架 |
| **ReactFlow** | 11.10.4 | 可视化流程图编辑器 |
| **TypeScript** | 5.3.3 | 类型安全 |
| **Vite** | 5.1.0 | 构建工具和开发服务器 |
| **Axios** | 1.6.7 | HTTP 客户端 |
| **@vitejs/plugin-react** | 4.2.1 | React 插件 |

---

## 核心功能模块

### 1. 可视化编辑器 (ReactFlow)
- 拖拽式节点放置
- 节点连接（边）
- 节点点击配置
- 画布缩放和平移

### 2. 节点类型
| 节点类型 | 功能 |
|---------|------|
| 开始 | 工作流起点 |
| 结束 | 工作流终点 |
| 输入 | 用户输入配置（对话框/表单） |
| 输出 | 结果输出配置 |
| 大模型 | LLM 调用配置（模型、温度、提示词） |
| 代码 | 自定义 Python 代码执行 |
| 条件分支 | 条件判断和分支 |
| 知识库 | 向量数据库检索 |

### 3. 代码生成引擎
- 将工作流 JSON 转换为完整的 LangGraph Python 代码
- 自动生成 TypedDict 状态类
- 根据节点类型生成对应的处理函数
- 生成图连接代码（add_node, add_edge）

### 4. API 服务
- `/api/generate` - 接收工作流数据，返回生成的代码

---

## 启动方式

### 后端启动
```bash
cd backend
pip install -r requirements.txt
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### 前端启动
```bash
cd frontend
npm install
npm run dev
```

### 访问地址
- 前端：http://localhost:3000（或 3001）
- 后端 API：http://localhost:8000

---

## 依赖关系图

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (React)                       │
├─────────────────────────────────────────────────────────────┤
│  App.tsx                                                    │
│    ├── Sidebar.tsx (节点库)                                 │
│    ├── NodeConfigPanel.tsx (节点配置)                       │
│    ├── WorkflowConfigPanel.tsx (工作流配置)                 │
│    ├── CodePanel.tsx (代码展示)                             │
│    └── api/index.ts → axios → Backend API                  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     Backend (FastAPI)                        │
├─────────────────────────────────────────────────────────────┤
│  api/main.py                                                │
│    └── generator/code_gen.py                                │
│          ├── nodes/node_types.py (节点类型定义)              │
│          └── 输出: LangGraph Python 代码                    │
└─────────────────────────────────────────────────────────────┘
```

---

## 生成代码示例

输入工作流配置后，生成的代码结构如下：

```python
from typing import TypedDict
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

class AgentState(TypedDict):
    query: str
    output: str

GLOBAL_VARS = {...}

def node_function(state: AgentState) -> AgentState:
    # 节点逻辑
    return state

def build_graph():
    workflow = StateGraph(AgentState)
    workflow.add_node("node_id", node_function)
    workflow.set_entry_point("node_id")
    workflow.add_edge("node_id", END)
    return workflow.compile()

if __name__ == "__main__":
    app = build_graph()
```

---

*文档生成时间：2026-03-10*
