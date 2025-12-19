'use client'

import { useState } from 'react'
import Chat from '@/components/Chat'
import AdminPanel from '@/components/AdminPanel'
import styles from './page.module.css'

export default function Home() {
  const [showAdmin, setShowAdmin] = useState(false)

  return (
    <main className={styles.main}>
      <div className={styles.container}>
        <header className={styles.header}>
          <div className={styles.titleContainer}>
            <span className={styles.logo}>🤖</span>
            <h1 className={styles.title}>Business Assistant AI</h1>
          </div>
          <button
            className={styles.adminButton}
            onClick={() => setShowAdmin(!showAdmin)}
          >
            {showAdmin ? '💬 Chat' : '⚙️ Admin Panel'}
          </button>
        </header>

        {showAdmin ? <AdminPanel /> : <Chat />}

        <footer className={styles.footer}>
          <p>🔒 Powered by AI & Vector Database | 📚 RAG Technology | 🚀 Business Intelligence</p>
        </footer>
      </div>
    </main>
  )
}
