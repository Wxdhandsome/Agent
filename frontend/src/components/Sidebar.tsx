import './Sidebar.css'

const nodeItems = [
  { type: 'start', label: '开始', color: '#10b981', icon: '▶' },
  { type: 'end', label: '结束', color: '#ef4444', icon: '■' },
  { type: 'input', label: '输入', color: '#06b6d4', icon: '📥' },
  { type: 'output', label: '输出', color: '#84cc16', icon: '📤' },
  { type: 'llm', label: '大模型', color: '#3b82f6', icon: '🤖' },
  { type: 'code', label: '代码', color: '#8b5cf6', icon: '💻' },
  { type: 'condition', label: '条件分支', color: '#ec4899', icon: '🔀' },
  { type: 'knowledge', label: '知识库', color: '#f59e0b', icon: '📚' },
]

const Sidebar = () => {
  const onDragStart = (event: React.DragEvent, nodeType: string, label: string) => {
    event.dataTransfer.setData('application/reactflow', nodeType)
    event.dataTransfer.setData('application/label', label)
    event.dataTransfer.effectAllowed = 'move'
  }

  return (
    <div className="sidebar">
      <div className="sidebar-section">
        <h3>节点库</h3>
        <div className="node-list">
          {nodeItems.map((item) => (
            <div
              key={item.type}
              className="node-item"
              draggable
              onDragStart={(e) => onDragStart(e, item.type, item.label)}
              style={{ borderLeftColor: item.color }}
            >
              <span className="node-item-icon">{item.icon}</span>
              <div className="node-item-name">{item.label}</div>
            </div>
          ))}
        </div>
      </div>
      <div className="sidebar-section">
        <h3>使用说明</h3>
        <ul className="instructions">
          <li>从左侧拖拽节点到画布</li>
          <li>连接节点创建工作流</li>
          <li>点击生成代码按钮</li>
        </ul>
      </div>
    </div>
  )
}

export default Sidebar
