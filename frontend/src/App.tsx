import { useState, useCallback, useRef, useEffect } from 'react'
import ReactFlow, {
  ReactFlowProvider,
  addEdge,
  useNodesState,
  useEdgesState,
  useReactFlow,
  Controls,
  Background,
  Handle,
  Position,
  Node,
  Connection,
  MarkerType,
  Panel,
} from 'reactflow'
import './App.css'
import Sidebar from './components/Sidebar'
import CodePanel from './components/CodePanel'
import NodeConfigPanel from './components/NodeConfigPanel'
import WorkflowConfigPanel from './components/WorkflowConfigPanel'
import { generateCode } from './api'

const WORKFLOW_STORAGE_KEY = 'langflow_workflow'

interface WorkflowConfig {
  openingMessage: string
  runMode: 'single' | 'batch'
  interactionType: 'none' | 'select' | 'input'
  enableDialogInput: boolean
  enableFormInput: boolean
  enableFileUpload: boolean
  fileSizeLimit: number
  fileTypes: string
  outputVariable: string
  presetQuestions: string[]
}

const defaultWorkflowConfig: WorkflowConfig = {
  openingMessage: '',
  runMode: 'single',
  interactionType: 'input',
  enableDialogInput: true,
  enableFormInput: false,
  enableFileUpload: false,
  fileSizeLimit: 15000,
  fileTypes: 'all',
  outputVariable: 'output',
  presetQuestions: [],
}

function loadWorkflowFromStorage(): {
  nodes: Node[]
  edges: any[]
  workflowConfig: Partial<WorkflowConfig> | null
} {
  try {
    const raw = localStorage.getItem(WORKFLOW_STORAGE_KEY)
    if (!raw) return { nodes: [], edges: [], workflowConfig: null }
    const parsed = JSON.parse(raw)
    return {
      nodes: Array.isArray(parsed.nodes) ? parsed.nodes : [],
      edges: Array.isArray(parsed.edges) ? parsed.edges : [],
      workflowConfig: parsed.workflowConfig && typeof parsed.workflowConfig === 'object' ? parsed.workflowConfig : null,
    }
  } catch {
    return { nodes: [], edges: [], workflowConfig: null }
  }
}

const CustomNode = ({ data, selected }: { data: any; selected: boolean }) => {
  const getColor = () => {
    switch (data.type) {
      case 'start':
        return '#10b981'
      case 'end':
        return '#ef4444'
      case 'llm':
        return '#3b82f6'
      case 'code':
        return '#8b5cf6'
      case 'knowledge':
        return '#f59e0b'
      case 'condition':
        return '#ec4899'
      case 'input':
        return '#06b6d4'
      case 'output':
        return '#84cc16'
      default:
        return '#6b7280'
    }
  }

  const getIcon = () => {
    switch (data.type) {
      case 'start':
        return '>'
      case 'end':
        return '[]'
      case 'llm':
        return 'AI'
      case 'code':
        return 'JS'
      case 'knowledge':
        return 'KB'
      case 'condition':
        return '? '
      case 'input':
        return 'In'
      case 'output':
        return 'Out'
      default:
        return '??'
    }
  }

  const isCondition = data.type === 'condition'

  return (
    <div className="custom-node" style={{ borderColor: getColor() }}>
      {data.type !== 'start' && <Handle type="target" position={Position.Top} />}
      <div className="node-header" style={{ backgroundColor: getColor() }}>
        <span className="node-icon">{getIcon()}</span>
        <span className="node-title">{data.label || data.type}</span>
      </div>
      <div className="node-body">
        <div className="node-type">{data.type}</div>
      </div>
      {data.type === 'end' && null}
      {data.type !== 'end' && !isCondition && (
        <Handle type="source" position={Position.Bottom} />
      )}
      {isCondition && (
        <>
          <Handle
            type="source"
            position={Position.Bottom}
            id="condition_0"
            style={{ left: '30%' }}
            title="条件成立 (if)"
          />
          <Handle
            type="source"
            position={Position.Bottom}
            id="condition_else"
            style={{ left: '70%' }}
            title="否则 (else)"
          />
        </>
      )}
    </div>
  )
}

const nodeTypes = {
  custom: CustomNode,
}

const AppContent = () => {
  const reactFlowWrapper = useRef<HTMLDivElement>(null)
  const initialWorkflow = useRef(loadWorkflowFromStorage()).current
  const [nodes, setNodes, onNodesChange] = useNodesState(initialWorkflow.nodes)
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialWorkflow.edges)
  const [reactFlowInstance, setReactFlowInstance] = useState<any>(null)
  const { getSelectedNodes, getSelectedEdges, deleteElements } = useReactFlow()
  const [generatedCode, setGeneratedCode] = useState('')
  const [showCodePanel, setShowCodePanel] = useState(false)
  const [selectedNode, setSelectedNode] = useState<Node | null>(null)
  const [showConfigPanel, setShowConfigPanel] = useState(false)
  const [showWorkflowConfig, setShowWorkflowConfig] = useState(false)
  const [loading, setLoading] = useState(false)
  const [workflowConfig, setWorkflowConfig] = useState<WorkflowConfig>({
    ...defaultWorkflowConfig,
    ...initialWorkflow.workflowConfig,
  })

  // 防抖保存到 localStorage，刷新后可恢复
  const saveTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  useEffect(() => {
    if (saveTimeoutRef.current) clearTimeout(saveTimeoutRef.current)
    saveTimeoutRef.current = setTimeout(() => {
      try {
        localStorage.setItem(
          WORKFLOW_STORAGE_KEY,
          JSON.stringify({
            nodes,
            edges,
            workflowConfig,
          })
        )
      } catch (_) {}
      saveTimeoutRef.current = null
    }, 800)
    return () => {
      if (saveTimeoutRef.current) clearTimeout(saveTimeoutRef.current)
    }
  }, [nodes, edges, workflowConfig])

  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge({ ...params, markerEnd: { type: MarkerType.ArrowClosed } }, eds)),
    [setEdges]
  )

  const onDragOver = useCallback((event: React.DragEvent) => {
    event.preventDefault()
    event.dataTransfer.dropEffect = 'move'
  }, [])

  const onDrop = useCallback(
    (event: React.DragEvent) => {
      event.preventDefault()

      const type = event.dataTransfer.getData('application/reactflow')
      const label = event.dataTransfer.getData('application/label')

      if (typeof type === 'undefined' || !type) {
        return
      }

      const position = reactFlowInstance.screenToFlowPosition({
        x: event.clientX,
        y: event.clientY,
      })

      const newNode: Node = {
        id: 'node_' + Date.now(),
        type: 'custom',
        position,
        data: {
          label,
          type,
          config: getDefaultConfig(type)
        },
      }

      setNodes((nds) => nds.concat(newNode))
    },
    [reactFlowInstance, setNodes]
  )

  const getDefaultConfig = (type: string) => {
    switch (type) {
      case 'llm':
        return {
          model: 'vllm2/Qwen3-32B-FP8',
          temperature: 0.7,
          systemPrompt: '',
          userPrompt: '',
          inputs: [
            { name: 'arg1', type: 'string' },
            { name: 'arg2', type: 'string' },
          ],
          outputs: [
            { name: 'result1', type: 'string' },
            { name: 'result2', type: 'string' },
          ],
          enableReference: true,
        }
      case 'code':
        return {
          code: "def main(arg1, arg2):\n    return {'result1': arg1, 'result2': arg2}",
          inputs: [
            { name: 'arg1', type: 'string' },
            { name: 'arg2', type: 'string' },
          ],
          outputs: [
            { name: 'result1', type: 'string' },
            { name: 'result2', type: 'string' },
          ],
        }
      case 'condition':
        return {
          conditions: [
            { label: '条件1', expression: 'true' },
          ],
          hasElse: true,
        }
      case 'input':
        return {
          inputType: 'dialog',
          variables: [{ name: 'query', type: 'string' }],
        }
      case 'output':
        return {
          outputVariable: 'output',
        }
      default:
        return {}
    }
  }

  const onNodeClick = useCallback((_: React.MouseEvent, node: Node) => {
    setSelectedNode(node)
    setShowConfigPanel(true)
  }, [])

  const onPaneClick = useCallback(() => {
    setShowConfigPanel(false)
    setSelectedNode(null)
  }, [])

  const handleDeleteSelected = useCallback(() => {
    const selectedNodes = getSelectedNodes()
    const selectedEdges = getSelectedEdges()
    if (selectedNodes.length > 0 || selectedEdges.length > 0) {
      deleteElements({ nodes: selectedNodes, edges: selectedEdges })
      if (selectedNode && selectedNodes.some((n) => n.id === selectedNode.id)) {
        setShowConfigPanel(false)
        setSelectedNode(null)
      }
    }
  }, [getSelectedNodes, getSelectedEdges, deleteElements, selectedNode])

  const onNodesDelete = useCallback(
    (deleted: Node[]) => {
      if (selectedNode && deleted.some((n) => n.id === selectedNode.id)) {
        setShowConfigPanel(false)
        setSelectedNode(null)
      }
    },
    [selectedNode]
  )

  const onEdgesDelete = useCallback(() => {}, [])

  const updateNodeConfig = useCallback((nodeId: string, config: any) => {
    setNodes((nds) =>
      nds.map((node) => {
        if (node.id === nodeId) {
          return { ...node, data: { ...node.data, config } }
        }
        return node
      })
    )
  }, [setNodes])

  const updateNodeLabel = useCallback((nodeId: string, label: string) => {
    setNodes((nds) =>
      nds.map((node) => {
        if (node.id === nodeId) {
          return { ...node, data: { ...node.data, label } }
        }
        return node
      })
    )
  }, [setNodes])

  const collectStateFields = (nodesData: Node[]) => {
    const fields: Record<string, string> = {}
    nodesData.forEach((node) => {
      if (node.data.type === 'input' && node.data.config?.variables) {
        node.data.config.variables.forEach((v: any) => {
          fields[v.name] = v.type || 'string'
        })
      }
    })
    if (Object.keys(fields).length === 0) {
      fields['query'] = 'string'
      fields['output'] = 'string'
    }
    return fields
  }

  interface VariableWithSource {
    name: string
    sourceNodeId: string
    sourceNodeLabel: string
    sourceNodeType: string
  }

  /** 收集图中所有可能的状态变量名，供输出节点选择 */
  const collectAvailableStateKeys = (nodesData: Node[]) => {
    const variables: VariableWithSource[] = []
    const seenNames = new Set<string>()
    
    const addVariable = (name: string, node: Node) => {
      if (!name || seenNames.has(name)) return
      seenNames.add(name)
      variables.push({
        name,
        sourceNodeId: node.id,
        sourceNodeLabel: node.data.label || node.data.type,
        sourceNodeType: node.data.type
      })
    }

    nodesData.forEach((node) => {
      const type = node.data?.type
      const config = node.data?.config || {}
      if (type === 'input' && config.variables) {
        config.variables.forEach((v: any) => {
          addVariable(v.name, node)
        })
      }
      if (type === 'llm' || type === 'code') {
        ;(config.outputs || []).forEach((o: any) => {
          addVariable(o.name, node)
        })
      }
    })

    if (!seenNames.has('query')) {
      variables.unshift({
        name: 'query',
        sourceNodeId: 'global',
        sourceNodeLabel: '全局变量',
        sourceNodeType: 'global'
      })
    }
    if (!seenNames.has('output')) {
      variables.unshift({
        name: 'output',
        sourceNodeId: 'global',
        sourceNodeLabel: '全局变量',
        sourceNodeType: 'global'
      })
    }

    return variables.sort((a, b) => a.name.localeCompare(b.name))
  }

  const handleGenerateCode = async () => {
    setLoading(true)
    try {
      // 开始节点的「开场引导」会参与生成 OPENING_MESSAGE，优先于 Workflow Config 中的设置
      const startNode = nodes.find((n) => n.data?.type === 'start')
      const mergedWorkflowConfig = {
        ...workflowConfig,
        ...(startNode?.data?.config?.openingMessage != null &&
        String(startNode.data.config.openingMessage).trim() !== ''
          ? { openingMessage: String(startNode.data.config.openingMessage).trim() }
          : {}),
      }

      const graphData = {
        state: { fields: collectStateFields(nodes) },
        nodes: nodes.map((n) => ({
          id: n.id,
          type: n.data.type,
          label: n.data.label,
          config: n.data.config || {},
        })),
        edges: edges.map((e) => ({
          from: e.source,
          to: e.target,
          ...(e.sourceHandle != null && { sourceHandle: e.sourceHandle }),
        })),
        workflowConfig: mergedWorkflowConfig,
      }

      const code = await generateCode(graphData)
      setGeneratedCode(code)
      setShowCodePanel(true)
    } catch (error) {
      console.error('Failed to generate code:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app">
      <div className="header">
        <h1>LangFlow</h1>
        <div className="header-actions">
          <button
            className="btn btn-secondary"
            onClick={handleDeleteSelected}
            title="删除选中的节点和连线（也可按 Backspace）"
          >
            删除选中
          </button>
          <button className="btn btn-secondary" onClick={() => setShowWorkflowConfig(true)}>
            Workflow Config
          </button>
          <button className="btn btn-primary" onClick={handleGenerateCode} disabled={loading}>
            {loading ? 'Generating...' : 'Generate Code'}
          </button>
        </div>
      </div>
      <div className="main">
        <Sidebar />
        <div className="canvas-wrapper" ref={reactFlowWrapper}>
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            onInit={setReactFlowInstance}
            onDrop={onDrop}
            onDragOver={onDragOver}
            onNodeClick={onNodeClick}
            onPaneClick={onPaneClick}
            onNodesDelete={onNodesDelete}
            onEdgesDelete={onEdgesDelete}
            nodeTypes={nodeTypes}
            fitView
            deleteKeyCode={['Backspace', 'Delete']}
          >
            <Background />
            <Controls />
            <Panel position="top-center">
              <div className="panel-hint">
                从左侧拖拽添加节点 · 选中后按 Delete/Backspace 或点击「删除选中」可删除 · 工作流已自动保存，刷新可恢复
              </div>
            </Panel>
          </ReactFlow>
        </div>
        {showConfigPanel && selectedNode && (
          <NodeConfigPanel
            node={selectedNode}
            onClose={() => setShowConfigPanel(false)}
            onUpdateConfig={updateNodeConfig}
            onUpdateLabel={updateNodeLabel}
            availableStateKeys={collectAvailableStateKeys(nodes)}
          />
        )}
      </div>
      {showCodePanel && (
        <CodePanel code={generatedCode} onClose={() => setShowCodePanel(false)} />
      )}
      {showWorkflowConfig && (
        <WorkflowConfigPanel
          config={workflowConfig}
          onUpdate={setWorkflowConfig}
          onClose={() => setShowWorkflowConfig(false)}
        />
      )}
    </div>
  )
}

const App = () => (
  <ReactFlowProvider>
    <AppContent />
  </ReactFlowProvider>
)

export default App
