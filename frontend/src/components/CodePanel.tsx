import { useState } from 'react'
import './CodePanel.css'

interface CodePanelProps {
  code: string
  onClose: () => void
}

const CodePanel = ({ code, onClose }: CodePanelProps) => {
  const [copied, setCopied] = useState(false)

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(code)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch (error) {
      console.error('Failed to copy:', error)
    }
  }

  return (
    <div className="code-panel-overlay" onClick={onClose}>
      <div className="code-panel" onClick={(e) => e.stopPropagation()}>
        <div className="code-panel-header">
          <h3>生成的代码</h3>
          <div className="code-panel-actions">
            <button className="btn btn-secondary" onClick={handleCopy}>
              {copied ? '已复制!' : '复制代码'}
            </button>
            <button className="btn btn-close" onClick={onClose}>
              ×
            </button>
          </div>
        </div>
        <div className="code-panel-content">
          <pre>
            <code>{code}</code>
          </pre>
        </div>
      </div>
    </div>
  )
}

export default CodePanel
