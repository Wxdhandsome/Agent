import { useState } from 'react'
import './WorkflowConfigPanel.css'

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

interface WorkflowConfigPanelProps {
  config: WorkflowConfig
  onUpdate: (config: WorkflowConfig) => void
  onClose: () => void
}

const WorkflowConfigPanel = ({ config, onUpdate, onClose }: WorkflowConfigPanelProps) => {
  const [localConfig, setLocalConfig] = useState<WorkflowConfig>(config)
  const [newQuestion, setNewQuestion] = useState('')

  const handleChange = (key: keyof WorkflowConfig, value: any) => {
    const newConfig = { ...localConfig, [key]: value }
    setLocalConfig(newConfig)
    onUpdate(newConfig)
  }

  const addPresetQuestion = () => {
    if (newQuestion.trim()) {
      const newQuestions = [...(localConfig.presetQuestions || []), newQuestion.trim()]
      handleChange('presetQuestions', newQuestions)
      setNewQuestion('')
    }
  }

  const removePresetQuestion = (index: number) => {
    const newQuestions = [...(localConfig.presetQuestions || [])]
    newQuestions.splice(index, 1)
    handleChange('presetQuestions', newQuestions)
  }

  return (
    <div className="workflow-config-overlay" onClick={onClose}>
      <div className="workflow-config-panel" onClick={(e) => e.stopPropagation()}>
        <div className="workflow-config-header">
          <h3>工作流配置</h3>
          <button className="btn-close" onClick={onClose}>×</button>
        </div>
        <div className="workflow-config-content">
          <div className="config-section">
            <h4>开场引导</h4>
            <div className="config-item">
              <label>开场白</label>
              <textarea
                value={localConfig.openingMessage}
                onChange={(e) => handleChange('openingMessage', e.target.value)}
                placeholder="每次工作流开始执行时向用户发送此消息，支持Markdown格式"
                rows={4}
              />
            </div>
          </div>

          <div className="config-section">
            <h4>运行模式</h4>
            <div className="config-item">
              <div className="radio-group">
                <label>
                  <input
                    type="radio"
                    value="single"
                    checked={localConfig.runMode === 'single'}
                    onChange={(e) => handleChange('runMode', e.target.value)}
                  />
                  单次运行
                </label>
                <label>
                  <input
                    type="radio"
                    value="batch"
                    checked={localConfig.runMode === 'batch'}
                    onChange={(e) => handleChange('runMode', e.target.value)}
                  />
                  批量运行
                </label>
              </div>
            </div>
          </div>

          <div className="config-section">
            <h4>交互类型</h4>
            <div className="config-item">
              <div className="radio-group-vertical">
                <label>
                  <input
                    type="radio"
                    value="none"
                    checked={localConfig.interactionType === 'none'}
                    onChange={(e) => handleChange('interactionType', e.target.value)}
                  />
                  无交互
                </label>
                <label>
                  <input
                    type="radio"
                    value="select"
                    checked={localConfig.interactionType === 'select'}
                    onChange={(e) => handleChange('interactionType', e.target.value)}
                  />
                  选择型交互
                </label>
                <label>
                  <input
                    type="radio"
                    value="input"
                    checked={localConfig.interactionType === 'input'}
                    onChange={(e) => handleChange('interactionType', e.target.value)}
                  />
                  输入型交互
                </label>
              </div>
            </div>
          </div>

          <div className="config-section">
            <h4>输入配置</h4>
            <div className="config-item">
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={localConfig.enableDialogInput}
                  onChange={(e) => handleChange('enableDialogInput', e.target.checked)}
                />
                对话框输入
              </label>
            </div>
            <div className="config-item">
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={localConfig.enableFormInput}
                  onChange={(e) => handleChange('enableFormInput', e.target.checked)}
                />
                表单输入
              </label>
            </div>
            <div className="config-item">
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={localConfig.enableFileUpload}
                  onChange={(e) => handleChange('enableFileUpload', e.target.checked)}
                />
                上传文件
              </label>
            </div>
            {localConfig.enableFileUpload && (
              <>
                <div className="config-item">
                  <label>文件内容长度上限</label>
                  <input
                    type="number"
                    value={localConfig.fileSizeLimit}
                    onChange={(e) => handleChange('fileSizeLimit', parseInt(e.target.value))}
                  />
                  <span className="unit">字</span>
                </div>
                <div className="config-item">
                  <label>上传文件类型</label>
                  <select
                    value={localConfig.fileTypes}
                    onChange={(e) => handleChange('fileTypes', e.target.value)}
                  >
                    <option value="all">全部类型</option>
                    <option value="image">图片文件</option>
                    <option value="document">文档文件</option>
                  </select>
                </div>
              </>
            )}
          </div>

          <div className="config-section">
            <h4>输出配置</h4>
            <div className="config-item">
              <label>输出变量</label>
              <input
                type="text"
                value={localConfig.outputVariable}
                onChange={(e) => handleChange('outputVariable', e.target.value)}
              />
            </div>
          </div>

          <div className="config-section">
            <h4>预置问题列表</h4>
            <div className="preset-questions">
              {(localConfig.presetQuestions || []).map((question, index) => (
                <div key={index} className="preset-question-item">
                  <span>{question}</span>
                  <button
                    className="btn-remove"
                    onClick={() => removePresetQuestion(index)}
                  >
                    ×
                  </button>
                </div>
              ))}
            </div>
            <div className="add-question">
              <input
                type="text"
                value={newQuestion}
                onChange={(e) => setNewQuestion(e.target.value)}
                placeholder="输入预置问题"
                onKeyPress={(e) => e.key === 'Enter' && addPresetQuestion()}
              />
              <button className="btn-add" onClick={addPresetQuestion}>
                + 添加
              </button>
            </div>
          </div>

          <div className="config-section">
            <h4>全局变量</h4>
            <div className="global-variables">
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
                <span className="var-desc">消息内容变量</span>
              </div>
              <div className="global-var-item">
                <span className="var-name">dialog_files_content</span>
                <span className="var-desc">文件内容变量</span>
              </div>
              <div className="global-var-item">
                <span className="var-name">dialog_image_files</span>
                <span className="var-desc">图片文件变量</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default WorkflowConfigPanel
