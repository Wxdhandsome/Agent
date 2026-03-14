import { useState } from 'react'
import { Node } from 'reactflow'
import './NodeConfigPanel.css'

interface VariableWithSource {
  name: string
  sourceNodeId: string
  sourceNodeLabel: string
  sourceNodeType: string
}

interface NodeConfigPanelProps {
  node: Node
  onClose: () => void
  onUpdateConfig: (nodeId: string, config: any) => void
  onUpdateLabel: (nodeId: string, label: string) => void
  /** 输出节点可选：图中可用的状态变量名，用于下拉选择 */
  availableStateKeys?: VariableWithSource[]
}

const NodeConfigPanel = ({ node, onClose, onUpdateConfig, onUpdateLabel, availableStateKeys = [] }: NodeConfigPanelProps) => {
  const [config, setConfig] = useState(node.data.config || {})
  const [label, setLabel] = useState(node.data.label || '')

  const handleConfigChange = (key: string, value: any) => {
    const newConfig = { ...config, [key]: value }
    setConfig(newConfig)
    onUpdateConfig(node.id, newConfig)
  }

  const handleLabelChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setLabel(e.target.value)
    onUpdateLabel(node.id, e.target.value)
  }

  const handleNestedConfigChange = (parentKey: string, index: number, key: string, value: any) => {
    const newConfig = { ...config }
    if (newConfig[parentKey] && newConfig[parentKey][index]) {
      newConfig[parentKey][index] = { ...newConfig[parentKey][index], [key]: value }
      setConfig(newConfig)
      onUpdateConfig(node.id, newConfig)
    }
  }

  const addCondition = () => {
    const newConditions = [...(config.conditions || []), { label: `条件${(config.conditions?.length || 0) + 1}`, expression: 'true' }]
    handleConfigChange('conditions', newConditions)
  }

  const removeCondition = (index: number) => {
    const newConditions = [...(config.conditions || [])]
    newConditions.splice(index, 1)
    handleConfigChange('conditions', newConditions)
  }

  const addVariable = () => {
    const newVariables = [...(config.variables || []), { name: `var${(config.variables?.length || 0) + 1}`, type: 'string' }]
    handleConfigChange('variables', newVariables)
  }

  const removeVariable = (index: number) => {
    const newVariables = [...(config.variables || [])]
    newVariables.splice(index, 1)
    handleConfigChange('variables', newVariables)
  }

  const addInputParam = () => {
    const newInputs = [...(config.inputs || []), { name: `arg${(config.inputs?.length || 0) + 1}`, type: 'string' }]
    handleConfigChange('inputs', newInputs)
  }

  const removeInputParam = (index: number) => {
    const newInputs = [...(config.inputs || [])]
    newInputs.splice(index, 1)
    handleConfigChange('inputs', newInputs)
  }

  const addOutputParam = () => {
    const newOutputs = [...(config.outputs || []), { name: `result${(config.outputs?.length || 0) + 1}`, type: 'string' }]
    handleConfigChange('outputs', newOutputs)
  }

  const removeOutputParam = (index: number) => {
    const newOutputs = [...(config.outputs || [])]
    newOutputs.splice(index, 1)
    handleConfigChange('outputs', newOutputs)
  }

  const addMessage = () => {
    const newMessages = [...(config.messages || []), { role: 'user', content: '' }]
    handleConfigChange('messages', newMessages)
  }

  const removeMessage = (index: number) => {
    const newMessages = [...(config.messages || [])]
    newMessages.splice(index, 1)
    handleConfigChange('messages', newMessages)
  }

  const updateMessage = (index: number, key: string, value: string) => {
    const newMessages = [...(config.messages || [])]
    if (newMessages[index]) {
      newMessages[index] = { ...newMessages[index], [key]: value }
      handleConfigChange('messages', newMessages)
    }
  }

  const insertVariable = (variable: VariableWithSource, targetField: string) => {
    const currentValue = config[targetField] || ''
    handleConfigChange(targetField, currentValue + `{{${variable.name}}}`)
  }

  const globalVariables: VariableWithSource[] = [
    { name: 'user_info', sourceNodeId: 'global', sourceNodeLabel: '全局变量', sourceNodeType: 'global' },
    { name: 'current_time', sourceNodeId: 'global', sourceNodeLabel: '全局变量', sourceNodeType: 'global' },
    { name: 'chat_history', sourceNodeId: 'global', sourceNodeLabel: '全局变量', sourceNodeType: 'global' },
    { name: 'message', sourceNodeId: 'global', sourceNodeLabel: '全局变量', sourceNodeType: 'global' },
    { name: 'context', sourceNodeId: 'global', sourceNodeLabel: '全局变量', sourceNodeType: 'global' },
  ]
  
  const availableNames = new Set(availableStateKeys.map(v => v.name))
  const filteredGlobalVariables = globalVariables.filter(v => !availableNames.has(v.name))
  const allAvailableVariables = [...availableStateKeys, ...filteredGlobalVariables]

  const renderConfig = () => {
    switch (node.data.type) {
      case 'start':
        return (
          <div className="config-section">
            <h4>开始节点</h4>
            <p className="config-description">工作流运行的起始节点。</p>
            <div className="config-item">
              <label>开场引导</label>
              <textarea
                value={config.openingMessage || ''}
                onChange={(e) => handleConfigChange('openingMessage', e.target.value)}
                placeholder="每次工作流开始执行时向用户发送此消息，支持 Markdown 格式，为空时不发送"
                rows={4}
              />
            </div>
            <div className="config-item">
              <label>引导问题</label>
              <input
                type="text"
                value={config.guidingQuestion || ''}
                onChange={(e) => handleConfigChange('guidingQuestion', e.target.value)}
                placeholder="请输入引导问题"
              />
            </div>
            <div className="config-section">
              <h4>全局变量</h4>
              <div className="global-vars-list">
                <div className="global-var-item">
                  <span className="var-name">用户信息</span>
                  <span className="var-desc">user_info</span>
                </div>
                <div className="global-var-item">
                  <span className="var-name">当前时间</span>
                  <span className="var-desc">current_time</span>
                </div>
                <div className="global-var-item">
                  <span className="var-name">最近10条聊天记录</span>
                  <span className="var-desc">chat_history</span>
                </div>
                <div className="global-var-item">
                  <span className="var-name">输入内容</span>
                  <span className="var-desc">message</span>
                </div>
              </div>
            </div>
          </div>
        )
      case 'end':
        return (
          <div className="config-section">
            <h4>输出</h4>
            <p className="config-description">向用户发送文本和文件，并且支持进行丰富的交互，确保在用户的特殊场景能够被允许在模型的特殊场景上直接提升并提交。</p>
            <div className="config-item">
              <label>消息内容变量</label>
              <div className="output-var-wrapper">
                <input
                  type="text"
                  value={config.outputVariable || 'message'}
                  onChange={(e) => handleConfigChange('outputVariable', e.target.value)}
                />
                <button className="btn-icon">📋</button>
              </div>
              <p className="config-hint-text">输入需要发送给用户的消息，例如“输入以下变量来祝贺我将 XX 操作，请您确认”，“以下是我的初稿草稿，您可以在其基础上进行”</p>
            </div>
            <div className="config-item">
              <label>交互类型</label>
              <div className="radio-group-tabs">
                <label className={`radio-tab ${config.interactionType !== 'select' && config.interactionType !== 'input' ? 'active' : ''}`}>
                  <input
                    type="radio"
                    name="interactionType"
                    value="none"
                    checked={config.interactionType !== 'select' && config.interactionType !== 'input'}
                    onChange={(e) => handleConfigChange('interactionType', e.target.value)}
                  />
                  无交互
                </label>
                <label className={`radio-tab ${config.interactionType === 'select' ? 'active' : ''}`}>
                  <input
                    type="radio"
                    name="interactionType"
                    value="select"
                    checked={config.interactionType === 'select'}
                    onChange={(e) => handleConfigChange('interactionType', e.target.value)}
                  />
                  选择型交互
                </label>
                <label className={`radio-tab ${config.interactionType === 'input' ? 'active' : ''}`}>
                  <input
                    type="radio"
                    name="interactionType"
                    value="input"
                    checked={config.interactionType === 'input'}
                    onChange={(e) => handleConfigChange('interactionType', e.target.value)}
                  />
                  输入型交互
                </label>
              </div>
            </div>
          </div>
        )
      case 'llm':
        return (
          <>
            <div className="config-section">
              <div className="config-item">
                <div className="radio-group-tabs">
                  <label className={`radio-tab ${config.runMode !== 'batch' ? 'active' : ''}`}>
                    <input
                      type="radio"
                      name="runMode"
                      value="single"
                      checked={config.runMode !== 'batch'}
                      onChange={(e) => handleConfigChange('runMode', e.target.value)}
                    />
                    单次运行
                  </label>
                  <label className={`radio-tab ${config.runMode === 'batch' ? 'active' : ''}`}>
                    <input
                      type="radio"
                      name="runMode"
                      value="batch"
                      checked={config.runMode === 'batch'}
                      onChange={(e) => handleConfigChange('runMode', e.target.value)}
                    />
                    批量运行
                  </label>
                </div>
              </div>
            </div>

            <div className="config-section">
              <h4>模型设置</h4>
              <div className="config-item">
                <label>模型</label>
                <select
                  value={config.model || '202-5090/Qwen3-32B-FP8'}
                  onChange={(e) => handleConfigChange('model', e.target.value)}
                >
                  <option value="202-5090/Qwen3-32B-FP8">202-5090/Qwen3-32B-FP8</option>
                  <option value="gpt-3.5-turbo">gpt-3.5-turbo</option>
                  <option value="gpt-4">gpt-4</option>
                  <option value="gpt-4-turbo">gpt-4-turbo</option>
                  <option value="claude-3-opus">claude-3-opus</option>
                  <option value="claude-3-sonnet">claude-3-sonnet</option>
                </select>
              </div>
              <div className="config-item">
                <label>温度: {config.temperature || 0.7}</label>
                <input
                  type="range"
                  min="0"
                  max="2"
                  step="0.1"
                  value={config.temperature || 0.7}
                  onChange={(e) => handleConfigChange('temperature', parseFloat(e.target.value))}
                />
              </div>
            </div>

            <div className="config-section">
              <h4>提示词</h4>
              <div className="config-item">
                <label>系统提示词</label>
                <textarea
                  value={config.systemPrompt || ''}
                  onChange={(e) => handleConfigChange('systemPrompt', e.target.value)}
                  rows={3}
                  placeholder="系统角色设定"
                />
              </div>
              <div className="config-item">
                <div className="prompt-header">
                  <label>用户提示词</label>
                </div>
                <textarea
                  value={config.userPrompt || ''}
                  onChange={(e) => handleConfigChange('userPrompt', e.target.value)}
                  rows={3}
                  placeholder="用户消息内容"
                />
              </div>
              <div className="config-item">
                <label>历史聊天记录</label>
                <div className="config-item">
                  <input
                    type="number"
                    value={config.historyCount || 50}
                    onChange={(e) => handleConfigChange('historyCount', parseInt(e.target.value))}
                    min="0"
                    max="100"
                  />
                </div>
              </div>
            </div>

            <div className="config-section">
              <h4>视觉</h4>
              <div className="config-item">
                <label className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={config.enableVision}
                    onChange={(e) => handleConfigChange('enableVision', e.target.checked)}
                  />
                  启用视觉功能
                </label>
              </div>
            </div>

            <div className="config-section">
              <h4>知识库</h4>
              <div className="config-item">
                <label className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={config.enableKnowledge}
                    onChange={(e) => handleConfigChange('enableKnowledge', e.target.checked)}
                  />
                  检索知识库范围
                </label>
                <select
                  value={config.knowledgeBase || ''}
                  onChange={(e) => handleConfigChange('knowledgeBase', e.target.value)}
                >
                  <option value="">请选择知识库</option>
                </select>
              </div>
            </div>

            <div className="config-section">
              <h4>数据库</h4>
              <div className="config-item">
                <label className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={config.enableDatabase}
                    onChange={(e) => handleConfigChange('enableDatabase', e.target.checked)}
                  />
                  启用数据库
                </label>
              </div>
            </div>

            <div className="config-section">
              <h4>显示设置</h4>
              <div className="config-item">
                <label className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={config.showInChat !== false}
                    onChange={(e) => handleConfigChange('showInChat', e.target.checked)}
                  />
                  在对话中显示生成内容
                </label>
                <p className="config-hint-text">如果关闭，此节点的内容将不会显示在对话中，但仍可作为参数传递给后续节点</p>
              </div>
            </div>

            <div className="config-section">
              <h4>工具</h4>
              <div className="tool-list">
                <div className="tool-item">
                  <span className="tool-name">🪟 窗口</span>
                  <button className="btn-add-tool">+</button>
                </div>
                <div className="tool-item">
                  <span className="tool-name">🔍 搜索</span>
                  <button className="btn-add-tool">+</button>
                </div>
                <div className="tool-item">
                  <span className="tool-name">📊 分析</span>
                  <button className="btn-add-tool">+</button>
                </div>
                <div className="tool-item">
                  <span className="tool-name">📝 写作</span>
                  <button className="btn-add-tool">+</button>
                </div>
              </div>
            </div>
          </>
        )
      case 'code':
        return (
          <>
            <div className="config-section">
              <h4>入参</h4>
              <div className="param-list">
                {(config.inputs || []).map((input: any, index: number) => (
                  <div key={index} className="param-item">
                    <input
                      type="text"
                      value={input.name}
                      onChange={(e) => handleNestedConfigChange('inputs', index, 'name', e.target.value)}
                      placeholder="参数名"
                    />
                    <select
                      value={input.type}
                      onChange={(e) => handleNestedConfigChange('inputs', index, 'type', e.target.value)}
                    >
                      <option value="string">String</option>
                      <option value="number">Number</option>
                      <option value="boolean">Boolean</option>
                      <option value="object">Object</option>
                      <option value="array">Array</option>
                    </select>
                    <button className="btn-remove" onClick={() => removeInputParam(index)}>×</button>
                  </div>
                ))}
              </div>
              <button className="btn-add" onClick={addInputParam}>+ 添加新的参数</button>
            </div>

            <div className="config-section">
              <h4>执行代码</h4>
              <textarea
                value={config.code || `def main(state):
    # 示例：处理输入并返回结果
    # 你可以使用 state 中的任何变量
    # 例如: query = state.get('query', '')
    # 处理完成后修改 state 并返回
    
    return state`}
                onChange={(e) => handleConfigChange('code', e.target.value)}
                rows={15}
                className="code-editor"
              />
              <div className="config-hint">
                <p>💡 提示：</p>
                <ul>
                  <li>使用 <code>state.get('变量名')</code> 获取输入</li>
                  <li>使用 <code>state['输出变量名'] = 值</code> 设置输出</li>
                  <li>函数必须返回修改后的 state</li>
                </ul>
              </div>
            </div>

            <div className="config-section">
              <h4>出参</h4>
              <div className="param-list">
                {(config.outputs || []).map((output: any, index: number) => (
                  <div key={index} className="param-item">
                    <input
                      type="text"
                      value={output.name}
                      onChange={(e) => handleNestedConfigChange('outputs', index, 'name', e.target.value)}
                      placeholder="参数名"
                    />
                    <select
                      value={output.type}
                      onChange={(e) => handleNestedConfigChange('outputs', index, 'type', e.target.value)}
                    >
                      <option value="string">String</option>
                      <option value="number">Number</option>
                      <option value="boolean">Boolean</option>
                      <option value="object">Object</option>
                      <option value="array">Array</option>
                    </select>
                    <button className="btn-remove" onClick={() => removeOutputParam(index)}>×</button>
                  </div>
                ))}
              </div>
              <button className="btn-add" onClick={addOutputParam}>+ 添加新的参数</button>
            </div>
          </>
        )
      case 'condition':
        return (
          <>
            <div className="config-section">
              <h4>条件分支</h4>
              <p className="config-description">根据条件表达式执行不同的分支。</p>
              {(config.conditions || []).map((condition: any, index: number) => (
                <div key={index} className="condition-item">
                  <div className="condition-label">
                    {index === 0 ? '如果' : index === (config.conditions?.length || 0) - 1 && config.hasElse ? '否则' : '否则如果'}
                  </div>
                  {(!(index === (config.conditions?.length || 0) - 1 && config.hasElse)) && (
                    <>
                      <div className="config-item">
                        <select
                          value={condition.field || ''}
                          onChange={(e) => handleNestedConfigChange('conditions', index, 'field', e.target.value)}
                        >
                          <option value="">选择变量</option>
                          {allAvailableVariables.map((v) => (
                            <option key={v.name} value={v.name}>
                              {v.name} — {v.sourceNodeLabel} ({v.sourceNodeType})
                            </option>
                          ))}
                        </select>
                        <select
                          value={condition.operator || '=='}
                          onChange={(e) => handleNestedConfigChange('conditions', index, 'operator', e.target.value)}
                        >
                          <option value="==">等于</option>
                          <option value="!=">不等于</option>
                          <option value=">">大于</option>
                          <option value="<">小于</option>
                          <option value=">=">大于等于</option>
                          <option value="<=">小于等于</option>
                          <option value="contains">包含</option>
                        </select>
                        <input
                          type="text"
                          value={condition.value || ''}
                          onChange={(e) => handleNestedConfigChange('conditions', index, 'value', e.target.value)}
                          placeholder="输入值"
                        />
                      </div>
                    </>
                  )}
                  <button className="btn-remove" onClick={() => removeCondition(index)}>删除</button>
                </div>
              ))}
              <button className="btn-add" onClick={addCondition}>+ 添加条件</button>
              <button className="btn-add" onClick={() => handleConfigChange('hasElse', true)}>+ 添加分支</button>
            </div>
          </>
        )
      case 'input':
        return (
          <>
            <div className="config-section">
              <h4>输入类型</h4>
              <div className="config-item">
                <div className="radio-group-tabs">
                  <label className={`radio-tab ${config.inputType !== 'form' ? 'active' : ''}`}>
                    <input
                      type="radio"
                      name="inputType"
                      value="dialog"
                      checked={config.inputType !== 'form'}
                      onChange={(e) => handleConfigChange('inputType', e.target.value)}
                    />
                    对话框输入
                  </label>
                  <label className={`radio-tab ${config.inputType === 'form' ? 'active' : ''}`}>
                    <input
                      type="radio"
                      name="inputType"
                      value="form"
                      checked={config.inputType === 'form'}
                      onChange={(e) => handleConfigChange('inputType', e.target.value)}
                    />
                    表单输入
                  </label>
                </div>
              </div>
            </div>
            <div className="config-section">
              <h4>输入变量</h4>
              <div className="param-list">
                {(config.variables || []).map((variable: any, index: number) => (
                  <div key={index} className="param-item">
                    <input
                      type="text"
                      value={variable.name}
                      onChange={(e) => handleNestedConfigChange('variables', index, 'name', e.target.value)}
                      placeholder="变量名"
                    />
                    <select
                      value={variable.type}
                      onChange={(e) => handleNestedConfigChange('variables', index, 'type', e.target.value)}
                    >
                      <option value="string">String</option>
                      <option value="number">Number</option>
                      <option value="boolean">Boolean</option>
                      <option value="object">Object</option>
                      <option value="array">Array</option>
                    </select>
                    <button className="btn-remove" onClick={() => removeVariable(index)}>×</button>
                  </div>
                ))}
              </div>
              <button className="btn-add" onClick={addVariable}>+ 添加新的变量</button>
            </div>
          </>
        )
      case 'output':
        return (
          <>
            <div className="config-section">
              <h4>输出设置</h4>
              <p className="config-description">选择要输出的状态变量（如 LLM 回复、代码结果等）。</p>
              <div className="config-item">
                <label className="checkbox-label">
                  <input type="checkbox" defaultChecked />
                  将输出结果展示在会话中
                </label>
              </div>
              <div className="config-item">
                <label>输出变量</label>
                <div className="output-var-wrapper">
                  {availableStateKeys.length > 0 ? (
                    <>
                      <select
                        value={availableStateKeys.some(v => v.name === config.outputVariable) ? config.outputVariable : '__custom__'}
                        onChange={(e) => {
                          const v = e.target.value
                          handleConfigChange('outputVariable', v === '__custom__' ? '' : v)
                        }}
                      >
                        {availableStateKeys.map((v) => (
                          <option key={v.name} value={v.name}>
                            {v.name} — {v.sourceNodeLabel} ({v.sourceNodeType})
                          </option>
                        ))}
                        <option value="__custom__">其他（手动输入）</option>
                      </select>
                      {(!config.outputVariable || !availableStateKeys.some(v => v.name === config.outputVariable)) && (
                        <input
                          type="text"
                          className="custom-output-var"
                          value={config.outputVariable || ''}
                          onChange={(e) => handleConfigChange('outputVariable', e.target.value)}
                          placeholder="输入状态变量名，如 result1"
                        />
                      )}
                    </>
                  ) : (
                    <input
                      type="text"
                      value={config.outputVariable || 'output'}
                      onChange={(e) => handleConfigChange('outputVariable', e.target.value)}
                      placeholder="如 output、result1、query"
                    />
                  )}
                </div>
              </div>
            </div>
          </>
        )
      case 'knowledge':
        return (
          <div className="config-section">
            <h4>知识节点</h4>
            <p className="config-description">从知识库检索相关文档</p>
            <div className="config-item">
              <label>知识库名称</label>
              <input
                type="text"
                value={config.knowledgeBase || ''}
                onChange={(e) => handleConfigChange('knowledgeBase', e.target.value)}
                placeholder="知识库名称"
              />
            </div>
            <div className="config-item">
              <label>检索数量</label>
              <input
                type="number"
                value={config.topK || 5}
                onChange={(e) => handleConfigChange('topK', parseInt(e.target.value))}
                min="1"
                max="20"
              />
            </div>
          </div>
        )
      default:
        return (
          <div className="config-section">
            <p>节点类型: {node.data.type}</p>
          </div>
        )
    }
  }

  return (
    <div className="config-panel">
      <div className="config-panel-header">
        <input
          type="text"
          value={label}
          onChange={handleLabelChange}
          className="node-title-input"
        />
        <button className="btn-close" onClick={onClose}>×</button>
      </div>
      <div className="config-panel-content">
        {renderConfig()}
      </div>
    </div>
  )
}

export default NodeConfigPanel
