import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'

createRoot(document.getElementById('root')!).render(
  // <StrictMode> todo uncomment this later. removed to prevent double API calls
    <App />
  // </StrictMode>,
)
