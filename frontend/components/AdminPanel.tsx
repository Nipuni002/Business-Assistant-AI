'use client'

import { useState, useRef } from 'react'
import { loginAdmin, uploadDocument, getDocuments, deleteDocument } from '@/utils/api'
import styles from './AdminPanel.module.css'

interface Document {
  id: string
  filename: string
  upload_date: string
  size: number
  status: string
}

export default function AdminPanel() {
  const [isLoggedIn, setIsLoggedIn] = useState(false)
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [documents, setDocuments] = useState<Document[]>([])
  const [uploading, setUploading] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const response = await loginAdmin(username, password)
      localStorage.setItem('adminToken', response.access_token)
      setIsLoggedIn(true)
      loadDocuments()
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || error.message || 'Invalid credentials. Please check username and password.'
      setError(errorMessage)
      console.error('Login error:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadDocuments = async () => {
    try {
      const response = await getDocuments()
      setDocuments(response.documents)
    } catch (error) {
      console.error('Error loading documents:', error)
    }
  }

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    setUploading(true)
    setError('')

    try {
      await uploadDocument(file)
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }
      loadDocuments()
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Error uploading file')
      console.error('Upload error:', error)
    } finally {
      setUploading(false)
    }
  }

  const handleDelete = async (fileId: string) => {
    if (!confirm('Are you sure you want to delete this document?')) return

    try {
      await deleteDocument(fileId)
      loadDocuments()
    } catch (error) {
      console.error('Delete error:', error)
    }
  }

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + ' B'
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB'
    return (bytes / (1024 * 1024)).toFixed(2) + ' MB'
  }

  if (!isLoggedIn) {
    return (
      <div className={styles.loginContainer}>
        <div className={styles.loginBox}>
          <h2>Admin Login</h2>
          <form onSubmit={handleLogin}>
            <div className={styles.formGroup}>
              <label>Username</label>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Enter username"
                required
              />
            </div>
            <div className={styles.formGroup}>
              <label>Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter password"
                required
              />
            </div>
            {error && <div className={styles.error}>{error}</div>}
            <button type="submit" className={styles.loginButton} disabled={loading}>
              {loading ? 'Logging in...' : 'Login'}
            </button>
            <div className={styles.loginHint}>
              <small>💡 Default: username: <strong>admin</strong> | password: <strong>admin123</strong></small>
            </div>
          </form>
        </div>
      </div>
    )
  }

  return (
    <div className={styles.adminContainer}>
      <div className={styles.uploadSection}>
        <h2>Upload Documents</h2>
        <p className={styles.subtitle}>Upload documents to train the chatbot</p>

        <div className={styles.uploadBox}>
          <input
            ref={fileInputRef}
            type="file"
            onChange={handleFileUpload}
            accept=".pdf,.txt,.docx,.xlsx"
            className={styles.fileInput}
            id="file-upload"
            disabled={uploading}
          />
          <label htmlFor="file-upload" className={styles.fileLabel}>
            {uploading ? '⏳ Uploading...' : '📁 Choose File'}
          </label>
          <p className={styles.uploadHint}>
            Supported: PDF, TXT, DOCX, XLSX (Max 10MB)
          </p>
        </div>

        {error && <div className={styles.error}>{error}</div>}
      </div>

      <div className={styles.documentsSection}>
        <h2>Uploaded Documents</h2>
        <p className={styles.subtitle}>Total: {documents.length} documents</p>

        {documents.length === 0 ? (
          <div className={styles.emptyState}>
            <p>No documents uploaded yet</p>
          </div>
        ) : (
          <div className={styles.documentList}>
            {documents.map((doc) => (
              <div key={doc.id} className={styles.documentCard}>
                <div className={styles.documentIcon}>📄</div>
                <div className={styles.documentInfo}>
                  <h3>{doc.filename}</h3>
                  <p>
                    {formatFileSize(doc.size)} • {new Date(doc.upload_date).toLocaleDateString()}
                  </p>
                </div>
                <button
                  className={styles.deleteButton}
                  onClick={() => handleDelete(doc.id)}
                >
                  🗑️
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
