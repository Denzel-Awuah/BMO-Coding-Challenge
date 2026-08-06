import React from 'react'

export default function Message({m}){
  return (
    <div className={`message ${m.role==='user'? 'user':'assistant'}`}>
      <div className="message-content">
        {m.loading ? (
          <span className="loading-dots"><span></span><span></span><span></span></span>
        ) : (
          m.text
        )}
      </div>
      {m.meta && (
        <div className="message-meta">
          <div><strong>Tools:</strong> {m.meta.tools.join(', ')}</div>
          <div><strong>At:</strong> {new Date(m.meta.timestamp).toLocaleString()}</div>
          <details>
            <summary className="steps-summary">Execution steps</summary>
            <ol className="steps">
              {m.meta.steps.map((s,si)=>(<li key={si} className="step-item">{s}</li>))}
            </ol>
          </details>
        </div>
      )}
    </div>
  )
}
