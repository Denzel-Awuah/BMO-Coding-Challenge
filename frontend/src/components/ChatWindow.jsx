import React, { useEffect, useRef } from 'react'
import Message from './Message'
import Composer from './Composer'

export default function ChatWindow({ messages=[], task, setTask, onSubmit, loading, onClear, onShowTestResults }){
  const messagesRef = useRef(null)

  // auto-scroll to bottom when messages change
  useEffect(()=>{
    const el = messagesRef.current
    if(el){ el.scrollTop = el.scrollHeight }
  }, [messages])

  return (
    <main className="main card chat-window">
      <div className="chat-header">
        <div>
          <div style={{fontWeight:700}}>Agent Chat</div>
          <div className="subtitle">Submit a task and inspect the agent's execution trace</div>
          <div className="badge connection-badge"><span className="status-dot" aria-hidden="true"></span>Connected</div>
        </div>
        <div className="chat-header-actions">
          <button className="btn view-tests-button" type="button" onClick={onShowTestResults}>
            View Tests Results
          </button>
        </div>
      </div>

      <div className="messages" id="messages" ref={messagesRef}>
        {messages.map((m,i)=> (<Message key={i} m={m} />))}
      </div>

      {/* Composer is placed inside ChatWindow so it stays anchored to the bottom */}
      <div className="composer-wrapper">
        <Composer task={task} setTask={setTask} onSubmit={onSubmit} loading={loading} onClear={onClear} />
      </div>
    </main>
  )
}
