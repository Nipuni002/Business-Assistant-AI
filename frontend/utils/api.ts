import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add auth token to requests if available
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('adminToken')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Chat API
export const sendMessage = async (message: string, sessionId: string | null) => {
  const response = await api.post('/api/chat/message', {
    message,
    session_id: sessionId,
  })
  return response.data
}

export const getChatHistory = async (sessionId: string) => {
  const response = await api.get(`/api/chat/history/${sessionId}`)
  return response.data
}

export const clearSession = async (sessionId: string) => {
  const response = await api.delete(`/api/chat/session/${sessionId}`)
  return response.data
}

// Document API
export const uploadDocument = async (file: File) => {
  const formData = new FormData()
  formData.append('file', file)

  const response = await api.post('/api/documents/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
  return response.data
}

export const getDocuments = async () => {
  const response = await api.get('/api/documents/list')
  return response.data
}

export const deleteDocument = async (fileId: string) => {
  const response = await api.delete(`/api/documents/delete/${fileId}`)
  return response.data
}

export const clearAllDocuments = async () => {
  const response = await api.post('/api/documents/clear-all')
  return response.data
}

// Admin API
export const loginAdmin = async (username: string, password: string) => {
  const response = await api.post('/api/admin/login', {
    username,
    password,
  })
  return response.data
}

export const getAdminStats = async () => {
  const response = await api.get('/api/admin/stats')
  return response.data
}

export const verifyToken = async () => {
  const response = await api.get('/api/admin/verify')
  return response.data
}

export default api
