# LangFlow - 基于 LangGraph 的拖拽式编程工具

类似 Coze 的可视化 AI 工作流编辑器，基于 LangGraph 构建，提供强大的节点配置和代码生成功能。

## 项目结构

```
.
├── backend/          # 后端代码（Python + FastAPI）
│   ├── generator/    # 代码生成引擎
│   ├── api/          # API 服务
│   └── nodes/        # 节点定义
├── frontend/         # 前端代码（React + ReactFlow）
│   ├── src/
│   │   ├── components/
│   │   └── api/
│   └── public/
├── start-backend.bat # 后端启动脚本（Windows）
├── start-frontend.bat # 前端启动脚本（Windows）
└── README.md
```

## 快速开始

### Windows 用户

1. **启动后端**
   ```bash
   start-backend.bat
   ```

2. **启动前端**（新开一个终端）
   ```bash
   start-frontend.bat
   ```

### 手动启动

#### 后端

```bash
cd backend
pip install -r requirements.txt
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

#### 前端

```bash
cd frontend
npm install
npm run dev
```

## 使用说明

1. 打开浏览器访问 http://localhost:3000
2. 从左侧节点库拖拽节点到画布
3. **点击节点**打开右侧配置面板进行详细配置
4. 连接节点创建工作流
5. 点击"生成代码"按钮生成 LangGraph Python 代码

## 节点类型

### 基础节点
- **开始节点**：工作流起始点
- **结束节点**：工作流结束点
- **输入节点**：配置输入变量，支持对话框和表单输入
- **输出节点**：配置输出变量

### 功能节点
- **大模型节点**：
  - 支持多种模型选择（gpt-3.5-turbo, gpt-4, Claude 3 等）
  - 可配置温度参数
  - 支持系统提示词和用户提示词
- **代码节点**：
  - 内置代码编辑器
  - 支持配置输入输出参数
  - 自定义 Python 代码执行
- **条件分支节点**：
  - 支持多个条件配置
  - 可自定义条件表达式
- **知识库节点**：向量数据库检索（预留接口）

## 核心功能

- **可视化拖拽编辑器**：使用 ReactFlow 构建直观的工作流编辑器
- **强大的节点配置面板**：每个节点类型都有专属的配置界面
- **代码生成引擎**：将可视化工作流转换为可执行的 LangGraph 代码
- **多种节点类型**：8 种以上节点类型，覆盖 AI 应用开发常用场景
- **API 服务**：FastAPI 提供的 RESTful API 接口

## 技术栈

- **后端**：Python, FastAPI, LangGraph, LangChain
- **前端**：React, ReactFlow, TypeScript, Vite

## 示例工作流

1. 拖拽「开始」→「输入」→「大模型」→「代码」→「输出」→「结束」
2. 连接各个节点
3. 配置输入变量和提示词
4. 生成并运行代码！
