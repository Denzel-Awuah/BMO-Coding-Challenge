import React, { useEffect, useMemo, useState } from 'react'

export default function TestResultsModal({ isOpen, onClose }) {
  const [tests, setTests] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!isOpen) return

    let active = true
    setLoading(true)
    setError('')

    fetch('/testResults.json')
      .then((response) => {
        if (!response.ok) {
          throw new Error(`Unable to load test results (${response.status})`)
        }
        return response.json()
      })
      .then((data) => {
        if (active) {
          setTests(Array.isArray(data?.tests) ? data.tests : [])
        }
      })
      .catch((err) => {
        if (active) {
          setError(err.message || 'Unable to load test results')
        }
      })
      .finally(() => {
        if (active) {
          setLoading(false)
        }
      })

    return () => {
      active = false
    }
  }, [isOpen])

  const groupedTests = useMemo(() => {
    return tests.reduce((acc, test) => {
      const tool = test.tool || 'Other'
      if (!acc[tool]) acc[tool] = []
      acc[tool].push(test)
      return acc
    }, {})
  }, [tests])

  if (!isOpen) return null

  return (
    <div className="modal-backdrop" role="dialog" aria-modal="true" aria-labelledby="test-results-title" onClick={onClose}>
      <div className="modal-card" onClick={(event) => event.stopPropagation()}>
        <div className="modal-header">
          <div>
            <div id="test-results-title" className="modal-title">Test Results</div>
            <div className="modal-subtitle">Sample prompts and the responses produced by the agent tools</div>
          </div>
          <button className="btn secondary" type="button" onClick={onClose}>Close</button>
        </div>

        {loading && <div className="modal-state">Loading test cases…</div>}
        {error && <div className="modal-state error">{error}</div>}

        {!loading && !error && Object.keys(groupedTests).length === 0 && (
          <div className="modal-state">No sample test cases are available yet.</div>
        )}

        {!loading && !error && (
          <div className="modal-content">
            {Object.entries(groupedTests).map(([tool, toolTests]) => (
              <section key={tool} className={`modal-section${tool === 'Multi-Tool Usage' ? ' modal-section--multi' : ''}`}>
                <h3>{tool}</h3>
                <div className="test-grid">
                  {toolTests.map((test, index) => (
                    <article key={`${tool}-${index}`} className="test-card">
                      <div className="test-category">{test.category}</div>
                      <div className="test-query"><strong>Query:</strong> {test.query}</div>
                      <div className="test-result">
                        <strong>Result:</strong>{' '}
                        {test.result.split('\n\n').map((line, i) => (
                          <span key={i}>{i > 0 && <><br /><br /></>}{line}</span>
                        ))}
                      </div>
                    </article>
                  ))}
                </div>
              </section>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
