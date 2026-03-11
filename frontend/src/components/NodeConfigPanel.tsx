import { useState } from 'react'
import { Node } from 'reactflow'
import './NodeConfigPanel.css'

interface NodeConfigPanelProps {
  node: Node
  onClose: () => void
  onUpdateConfig: (nodeId: string, config: any) => void
  onUpdateLabel: (nodeId: string, label: string) => void
}

const NodeConfigPanel = ({ node, onClose, onUpdateConfig, onUpdateLabel }: NodeConfigPanelProps) => {
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

  const insertVariable = (variable: string, targetField: string) => {
    const currentValue = config[targetField] || ''
    handleConfigChange(targetField, currentValue + `{{${variable}}}`)
  }

  const availableVariables = ['query', 'user_info', 'current_time', 'chat_history', 'message', 'context']

  const renderConfig = () => {
    switch (node.data.type) {
      case 'start':
        return (
          <div className="config-section">
            <h4>开始节点</h4>
            <p className="config-description">工作流的起始节点，无需额外配置。</p>
            <div className="config-item">
              <label>开场引导消息</label>
              <textarea
                value={config.openingMessage || ''}
                onChange={(e) => handleConfigChange('openingMessage', e.target.value)}
                placeholder="每次工作流开始执行时向用户发送此消息，支持 Markdown 格式"
                rows={4}
              />
            </div>
          </div>
        )
      case 'end':
        return (
          <div className="config-section">
            <h4>结束节点</h4>
            <p className="config-description">工作流的结束节点，无需额外配置。</p>
          </div>
        )
      case 'llm':
        return (
          <>
            <div className="config-section">
              <h4>运行模式</h4>
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
                  value={config.model || 'gpt-3.5-turbo'}
                  onChange={(e) => handleConfigChange('model', e.target.value)}
                >
                  <option value="vllm2/Qwen3-32B-FP8">vllm2/Qwen3-32B-FP8</option>
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
              <div className="config-item">
                <label className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={config.enableStream}
                    onChange={(e) => handleConfigChange('enableStream', e.target.checked)}
                  />
                  启用流式输出
                </label>
              </div>
            </div>

            <div className="config-section">
              <h4>输入参数</h4>
              <div className="config-item">
                <label>快速插入变量</label>
                <div className="variable-tags">
                  {availableVariables.map((v) => (
                    <span
                      key={v}
                      className="variable-tag"
                      onClick={() => insertVariable(v, 'systemPrompt')}
                    >
                      {v}
                    </span>
                  ))}
                </div>
              </div>
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
              <h4>提示词配置</h4>
              <div className="config-item">
                <label>系统提示词</label>
                <textarea
                  value={config.systemPrompt || ''}
                  onChange={(e) => handleConfigChange('systemPrompt', e.target.value)}
                  rows={5}
                  placeholder="系统角色设定，例如：You are a helpful assistant that helps users with their questions."
                />
              </div>
              <div className="config-item">
                <div className="prompt-header">
                  <label>用户提示词模板</label>
                </div>
                <textarea
                  value={config.userPrompt || ''}
                  onChange={(e) => handleConfigChange('userPrompt', e.target.value)}
                  rows={5}
                  placeholder="用户消息模板，例如：请回答以下问题：{{query}}"
                />
              </div>
              <div className="config-item">
                <label>对话历史（可选）</label>
                <div className="message-list">
                  {(config.messages || []).map((msg: any, index: number) => (
                    <div key={index} className="message-item">
                      <select
                        value={msg.role}
                        onChange={(e) => updateMessage(index, 'role', e.target.value)}
                      >
                        <option value="user">用户</option>
                        <option value="assistant">助手</option>
                        <option value="system">系统</option>
                      </select>
                      <textarea
                        value={msg.content}
                        onChange={(e) => updateMessage(index, 'content', e.target.value)}
                        placeholder="消息内容"
                        rows={2}
                      />
                      <button className="btn-remove" onClick={() => removeMessage(index)}>×</button>
                    </div>
                  ))}
                </div>
                <button className="btn-add" onClick={addMessage}>+ 添加历史消息</button>
              </div>
            </div>

            <div className="config-section">
              <h4>引用全局变量</h4>
              <div className="global-vars-list">
                <div className="global-var-item">
                  <span className="var-name">user_info</span>
                  <span className="var-desc">用户信息</span>
                </div>
                <div className="global-var-item">
                  <span className="var-name">current_time</span>
                  <span className="var-desc">当前时间</span>
                </div>
                <div className="global-var-item">
                  <span className="var-name">chat_history</span>
                  <span className="var-desc">最近10条聊天记录</span>
                </div>
                <div className="global-var-item">
                  <span className="var-name">message</span>
                  <span className="var-desc">当前消息内容</span>
                </div>
              </div>
            </div>

            <div className="config-section">
              <h4>输出参数</h4>
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
                        <label>条件名称</label>
                        <input
                          type="text"
                          value={condition.label}
                          onChange={(e) => handleNestedConfigChange('conditions', index, 'label', e.target.value)}
                          placeholder="例如: 包含关键词"
                        />
                      </div>
                      <div className="config-item">
                        <label>条件表达式</label>
                        <input
                          type="text"
                          value={condition.expression}
                          onChange={(e) => handleNestedConfigChange('conditions', index, 'expression', e.target.value)}
                          placeholder="例如: 'hello' in state.get('query', '').lower()"
                        />
                      </div>
                    </>
                  )}
                  <button className="btn-remove" onClick={() => removeCondition(index)}>删除</button>
                </div>
              ))}
              <button className="btn-add" onClick={addCondition}>+ 添加条件</button>
              <button className="btn-add btn-add-else" onClick={() => handleConfigChange('hasElse', true)}>+ 添加否则分支</button>
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
              <div className="config-item">
                <label className="checkbox-label">
                  <input type="checkbox" defaultChecked />
                  将输出结果展示在会话中
                </label>
              </div>
              <div className="config-item">
                <label>输出变量</label>
                <div className="output-var-wrapper">
                  <input
                    type="text"
                    value={config.outputVariable || 'output'}
                    onChange={(e) => handleConfigChange('outputVariable', e.target.value)}
                  />
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
