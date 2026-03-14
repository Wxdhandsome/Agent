import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export interface GraphData {
  state: { fields: Record<string, string> }
  nodes: Array<{
    id: string
    type: string
    label?: string
    config: Record<string, any>
  }>
  edges: Array<{
    from: string
    to: string
    sourceHandle?: string | null
    condition?: string
  }>
  workflowConfig: Record<string, any>
}

export interface ReviewResult {
  success: boolean
  has_errors: boolean
  syntax_valid: boolean
  issues: Array<{
    type: string
    location: string
    issue: string
    suggestion: string
  }>
  review_report: string
  fixed_code: string
}

export const generateCode = async (graphData: GraphData): Promise<string> => {
  const response = await api.post('/api/generate', graphData)
  return response.data.code
}

export const reviewCode = async (code: string): Promise<ReviewResult> => {
  const response = await api.post('/api/review-code', { code })
  return response.data
}

export default api
