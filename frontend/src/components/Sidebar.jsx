import React from 'react'
import IconCopy from './IconCopy'

export default function Sidebar({ history=[], selected, onSelect, copyOutput }){
  const formatTimestamp = (ts)=>{
    try{ return new Date(ts).toLocaleString() }catch(e){return ts}
  }

  return (
    <aside className="sidebar card">
      <div className="sidebar-header">
        <img src="/bmologo.png" className="logo-img" alt="BMO logo" />
        <div>
          <div className="title">BMO Agent Simulator</div>
          <div className="subtitle">Tool Usage</div>
        </div>
      </div>

      <div className="sidebar-section" style={{marginTop:8, marginBottom:8}}>
        <div className="title">Chats</div>
      </div>

      <div className="history-scroll">
        {history.length===0 && <div className="empty">No history yet — run a task to begin</div>}
        {history.map(h=> (
          <div key={h.id} className={`history-row ${selected===h.id? 'active': ''}`} onClick={()=>onSelect(h)}>
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
  )
}
