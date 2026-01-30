import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Landing from './pages/Landing'
import ScoringForm from './pages/ScoringForm'
import Results from './pages/Results'
import Dashboard from './pages/Dashboard'
import ErrorBoundary from './components/ErrorBoundary'
import Toast from './components/Toast'
import { useState } from 'react'
import { ScoringResponse, ApplicantInput } from './types'

function App() {
  const [lastResult, setLastResult] = useState<ScoringResponse | null>(null)
  const [lastInput, setLastInput] = useState<ApplicantInput | null>(null)
  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' | 'info' } | null>(null)

  const showToast = (message: string, type: 'success' | 'error' | 'info' = 'info') => {
    setToast({ message, type })
    setTimeout(() => setToast(null), 4000)
  }

  return (
    <ErrorBoundary>
      <Router>
        <div className="min-h-screen" style={{ backgroundColor: 'var(--color-cream, #faf8f5)' }}>
          <Routes>
            <Route path="/" element={<Landing />} />
            <Route
              path="/score"
              element={
                <ScoringForm
                  onResult={(result, input) => {
                    setLastResult(result)
                    setLastInput(input)
                  }}
                  showToast={showToast}
                />
              }
            />
            <Route
              path="/results"
              element={
                <Results
                  result={lastResult}
                  input={lastInput}
                />
              }
            />
            <Route path="/dashboard" element={<Dashboard showToast={showToast} />} />
          </Routes>
          {toast && (
            <Toast
              message={toast.message}
              type={toast.type}
              onClose={() => setToast(null)}
            />
          )}
        </div>
      </Router>
    </ErrorBoundary>
  )
}

export default App
