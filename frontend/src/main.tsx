import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './styles/global.css'
import './styles/theme.css'

// 初始化 data-theme（避免首次闪白）
const savedTheme = localStorage.getItem('life-planner:theme')
const initialTheme = savedTheme || (window.matchMedia?.('(prefers-color-scheme: dark)').matches ? 'dark' : 'light')
document.documentElement.setAttribute('data-theme', initialTheme)

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
