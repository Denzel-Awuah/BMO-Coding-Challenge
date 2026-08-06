import React from 'react'

export default function Message({m}){
  const tools = m.meta && Array.isArray(m.meta.tools) ? m.meta.tools : []
  const ts = m.meta && m.meta.timestamp ? new Date(m.meta.timestamp) : null
  const steps = m.meta && Array.isArray(m.meta.steps) ? m.meta.steps : []

  return (
    <div className={`message ${m.role==='user'? 'user':'assistant'}`}>
      <div className="message-content">
        {m.loading ? (
          <span className="loading-dots"><span></span><span></span><span></span></span>
        ) : (
          m.text
        )}
      </div>

      {steps.length > 0 && (
        <div className="message-meta">
          {/* While still streaming: show steps flat and visible, no toggle */}
          {m.loading ? (
            <ol className="steps steps-streaming">
              {steps.map((s,si)=>(
                <li key={si} className="step-item step-item--live">{s}</li>
              ))}
            </ol>
          ) : (
            /* Streaming done: wrap in a collapsible summary */
            <>
              {tools.length > 0 && <div><strong>Tools:</strong> {tools.join(', ')}</div>}
              {ts && <div><strong>At:</strong> {ts.toLocaleString()}</div>}
              <details>
                <summary className="steps-summary">Execution steps</summary>
                <ol className="steps">
                  {steps.map((s,si)=>(<li key={si} className="step-item">{s}</li>))}
                </ol>
              </details>
            </>
          )}
        </div>
      )}

      {/* Show tools + timestamp even when there are no steps (e.g. history load) */}
      {!m.loading && steps.length === 0 && (tools.length > 0 || ts) && (
        <div className="message-meta">
          {tools.length > 0 && <div><strong>Tools:</strong> {tools.join(', ')}</div>}
          {ts && <div><strong>At:</strong> {ts.toLocaleString()}</div>}
        </div>
      )}
    </div>
  )
}
