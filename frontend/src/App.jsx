import React, { useEffect, useState } from 'react'
import IconCopy from './components/IconCopy'

const API_BASE = 'http://localhost:5000/api'

function formatTimestamp(ts){
  try{ return new Date(ts).toLocaleString() }catch(e){return ts}
}

export default function App(){
  const [task, setTask] = useState('')
  const [history, setHistory] = useState([])
  const [loading, setLoading] = useState(false)
  const [selected, setSelected] = useState(null) // selected history id
  const [messages, setMessages] = useState([]) // current chat messages [{role, text}]

  useEffect(()=>{ fetchHistory() }, [])

  async function fetchHistory(){
    try{ const res = await fetch(`${API_BASE}/tasks`); const data = await res.json(); setHistory(data); if(data.length>0 && !selected){ setSelected(data[0].id); populateFromHistory(data[0]) } }catch(e){console.error(e)}
  }

  function populateFromHistory(item){
    setSelected(item.id)
    const msgs = [ {role:'user', text:item.task}, {role:'assistant', text: typeof item.output==='object'? JSON.stringify(item.output): String(item.output), meta:{tools:item.tools, steps:item.steps, timestamp:item.timestamp}} ]
    setMessages(msgs)
  }

  async function submit(e){
    e && e.preventDefault()
    if(!task.trim()) return
    setLoading(true)
    // clear current chat and show only the new user message (single request/response)
    const userMsg = {role:'user', text:task}
    // insert assistant placeholder with loading flag
    const placeholderAssistant = {role:'assistant', text:'', loading:true}
    setMessages([userMsg, placeholderAssistant])
    setSelected(null)
    try{
      const res = await fetch(`${API_BASE}/tasks`, { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({task}) })
      const data = await res.json()
      const assistantMsg = {role:'assistant', text: typeof data.output==='object'? JSON.stringify(data.output): String(data.output), meta:{tools:data.tools, steps:data.steps, timestamp:data.timestamp}}
      setMessages([userMsg, assistantMsg])
      await fetchHistory()
      setTask('')
      setSelected(data.id)
    }catch(err){ 
      console.error(err); 
      // replace placeholder with error message
      setMessages([userMsg, {role:'assistant', text:'Error: failed to get response from backend.'}])
      alert('Failed to submit task') 
    }
    finally{ setLoading(false) }
  }

  async function copyOutput(text){ try{ await navigator.clipboard.writeText(text) }catch(e){console.warn(e)} }

  return (
    <div className="app chat-app">
      <aside className="sidebar card">
        <div className="sidebar-header">
          <img src="/bmologo.png" className="logo-img" alt="BMO logo" />
          <div>
            <div className="title">BMO Agent Simulator</div>
            <div className="subtitle">Chat interface</div>
          </div>
        </div>

        <div className="history-scroll">
          {history.length===0 && <div className="empty">No history yet — run a task to begin</div>}
          {history.map(h=> (
            <div key={h.id} className={`history-row ${selected===h.id? 'active': ''}`} onClick={()=>populateFromHistory(h)}>
              <div className="history-row-left">
                <div className="history-task">{h.task}</div>
                <div className="history-ts">{formatTimestamp(h.timestamp)}</div>
              </div>
              <div className="history-right">
                <div className="tool-tag">{h.tools.join(', ')}</div>
              </div>
            </div>
          ))}
        </div>

        <div className="sidebar-footer">Backend: http://localhost:5000</div>
      </aside>

      <main className="main card">
        <div className="chat-header">
          <div>
            <div style={{fontWeight:700}}>Agent Chat</div>
            <div className="subtitle">Submit a task and inspect the agent's execution trace</div>
          </div>
          <div>
            <div className="badge">Connected</div>
          </div>
        </div>

        <div className="messages" id="messages">
          {messages.map((m,i)=> (
            <div key={i} className={`message ${m.role==='user'? 'user':'assistant'}`}>
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
                  <div><strong>At:</strong> {formatTimestamp(m.meta.timestamp)}</div>
                  <details>
                    <summary className="steps-summary">Execution steps</summary>
                    <ol className="steps">
                      {m.meta.steps.map((s,si)=>(<li key={si} className="step-item">{s}</li>))}
                    </ol>
                  </details>
                </div>
              )}
            </div>
          ))}
        </div>

        <form className="composer" onSubmit={submit}>
          <textarea value={task} onChange={(e)=>setTask(e.target.value)} placeholder='Ask the agent, e.g. "Weather in Toronto?"' />
          <div className="composer-actions">
            <button className="btn" type="submit" disabled={loading}>{loading? 'Thinking...':'Send'}</button>
            <button type="button" className="btn secondary" onClick={()=>setTask('')}>Clear</button>
          </div>
        </form>
      </main>
    </div>
  )
}
