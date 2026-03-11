import { useState, useCallback, useRef } from 'react'
import ReactFlow, {
  ReactFlowProvider,
  addEdge,
  useNodesState,
  useEdgesState,
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
      {data.type !== 'end' && <Handle type="source" position={Position.Bottom} />}
    </div>
  )
}

const nodeTypes = {
  custom: CustomNode,
}

const AppContent = () => {
  const reactFlowWrapper = useRef<HTMLDivElement>(null)
  const [nodes, setNodes, onNodesChange] = useNodesState([])
  const [edges, setEdges, onEdgesChange] = useEdgesState([])
  const [reactFlowInstance, setReactFlowInstance] = useState<any>(null)
  const [generatedCode, setGeneratedCode] = useState('')
  const [showCodePanel, setShowCodePanel] = useState(false)
  const [selectedNode, setSelectedNode] = useState<Node | null>(null)
  const [showConfigPanel, setShowConfigPanel] = useState(false)
  const [showWorkflowConfig, setShowWorkflowConfig] = useState(false)
  const [loading, setLoading] = useState(false)
  const [workflowConfig, setWorkflowConfig] = useState<WorkflowConfig>({
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
  })

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

  const handleGenerateCode = async () => {
    setLoading(true)
    try {
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
        })),
        workflowConfig: workflowConfig,
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
            nodeTypes={nodeTypes}
            fitView
          >
            <Background />
            <Controls />
            <Panel position="top-center">
              <div className="panel-hint">Drag nodes from sidebar</div>
            </Panel>
          </ReactFlow>
        </div>
        {showConfigPanel && selectedNode && (
          <NodeConfigPanel
            node={selectedNode}
            onClose={() => setShowConfigPanel(false)}
            onUpdateConfig={updateNodeConfig}
            onUpdateLabel={updateNodeLabel}
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
