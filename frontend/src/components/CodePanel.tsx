import { useState } from 'react'
import { reviewCode, ReviewResult } from '../api'
import './CodePanel.css'

interface CodePanelProps {
  code: string
  onClose: () => void
}

const CodePanel = ({ code, onClose }: CodePanelProps) => {
  const [copied, setCopied] = useState(false)
  const [reviewing, setReviewing] = useState(false)
  const [showReview, setShowReview] = useState(false)
  const [reviewResult, setReviewResult] = useState<ReviewResult | null>(null)
  const [showFixedCode, setShowFixedCode] = useState(false)
  const [displayCode, setDisplayCode] = useState(code)

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(displayCode)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch (error) {
      console.error('Failed to copy:', error)
    }
  }

  const handleReview = async () => {
    setReviewing(true)
    try {
      const result = await reviewCode(code)
      setReviewResult(result)
      setShowReview(true)
    } catch (error) {
      console.error('Failed to review code:', error)
    } finally {
      setReviewing(false)
    }
  }

  const toggleFixedCode = () => {
    setShowFixedCode(!showFixedCode)
    if (reviewResult) {
      setDisplayCode(showFixedCode ? code : reviewResult.fixed_code)
    }
  }

  return (
    <div className="code-panel-overlay" onClick={onClose}>
      <div className="code-panel" onClick={(e) => e.stopPropagation()}>
        <div className="code-panel-header">
          <h3>生成的代码</h3>
          <div className="code-panel-actions">
            <button 
              className="btn btn-secondary" 
              onClick={handleReview}
              disabled={reviewing}
            >
              {reviewing ? '审查中...' : '🔍 审查代码'}
            </button>
            <button className="btn btn-secondary" onClick={handleCopy}>
              {copied ? '已复制!' : '复制代码'}
            </button>
            <button className="btn btn-close" onClick={onClose}>
              ×
            </button>
          </div>
        </div>
        <div className="code-panel-content">
          {showReview && reviewResult && (
            <div className="review-panel">
              <div className="review-panel-header">
                <h4>代码审查报告</h4>
                <div className="review-status">
                  {reviewResult.syntax_valid ? (
                    <span className="status-success">✓ 语法正确</span>
                  ) : (
                    <span className="status-error">✗ 语法错误</span>
                  )}
                  {reviewResult.has_errors ? (
                    <span className="status-warning">⚠ 发现问题</span>
                  ) : (
                    <span className="status-success">✓ 未发现问题</span>
                  )}
                </div>
                <button 
                  className="btn btn-small" 
                  onClick={toggleFixedCode}
                >
                  {showFixedCode ? '显示原代码' : '显示修复代码'}
                </button>
              </div>
              {reviewResult.issues.length > 0 && (
                <div className="issues-list">
                  <h5>发现的问题：</h5>
                  {reviewResult.issues.map((issue, index) => (
                    <div key={index} className="issue-item">
                      <div className="issue-type">{issue.type}</div>
                      <div className="issue-location">{issue.location}</div>
                      <div className="issue-desc">{issue.issue}</div>
                      <div className="issue-suggestion">💡 {issue.suggestion}</div>
                    </div>
                  ))}
                </div>
              )}
              <div className="review-report">
                <h5>详细报告：</h5>
                <pre>{reviewResult.review_report}</pre>
              </div>
            </div>
          )}
          <pre>
            <code>{displayCode}</code>
          </pre>
        </div>
      </div>
    </div>
  )
}

export default CodePanel
